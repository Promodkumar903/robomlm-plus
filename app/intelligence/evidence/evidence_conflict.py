from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

from schemas.evidence.evidence_item import EvidenceItem
from schemas.evidence.evidence_package import EvidencePackage


class ConflictStatus(str, Enum):
    """
    Structural state of conflict analysis.
    """

    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class ConflictType(str, Enum):
    """
    Types of disagreement that can be established from evidence.
    """

    VALUE = "VALUE"
    DIRECTION = "DIRECTION"
    SOURCE = "SOURCE"
    TEMPORAL = "TEMPORAL"
    IDENTITY = "IDENTITY"
    SEMANTIC = "SEMANTIC"


@dataclass(frozen=True)
class EvidenceConflict:
    """
    Canonical description of a detected disagreement.

    A conflict records what disagrees and why. It does not decide which
    evidence item is correct.
    """

    conflict_id: str
    conflict_type: ConflictType

    evidence_ids: tuple[str, ...]

    evidence_type: str | None = None
    metric: str | None = None

    values: tuple[Any, ...] = field(default_factory=tuple)

    reason: str = ""

    detected_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        if not self.conflict_id:
            return False

        if not self.evidence_ids:
            return False

        if not self.reason:
            return False

        if not isinstance(self.conflict_type, ConflictType):
            return False

        if self.detected_at.tzinfo is None:
            return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "evidence_ids": list(self.evidence_ids),
            "evidence_type": self.evidence_type,
            "metric": self.metric,
            "values": list(self.values),
            "reason": self.reason,
            "detected_at": self.detected_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class ConflictAnalysisResult:
    """
    Result of deterministic conflict analysis over an evidence package.
    """

    status: ConflictStatus

    package_id: str | None

    conflicts: tuple[EvidenceConflict, ...] = field(default_factory=tuple)

    analyzed_count: int = 0
    comparable_count: int = 0
    conflict_count: int = 0

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    analyzer: str = "EvidenceConflictEngine"
    analyzer_version: str = "1.0"

    reason: str = ""

    def is_valid(self) -> bool:
        if self.status == ConflictStatus.INVALID:
            return False

        if self.analyzed_count < 0:
            return False

        if self.comparable_count < 0:
            return False

        if self.conflict_count != len(self.conflicts):
            return False

        return all(conflict.is_valid() for conflict in self.conflicts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "package_id": self.package_id,
            "conflicts": [conflict.to_dict() for conflict in self.conflicts],
            "analyzed_count": self.analyzed_count,
            "comparable_count": self.comparable_count,
            "conflict_count": self.conflict_count,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "analyzer": self.analyzer,
            "analyzer_version": self.analyzer_version,
            "reason": self.reason,
        }


class EvidenceConflictEngine:
    """
    Evidence conflict detection engine.

    Responsibilities
    ----------------
    1. Validate the evidence package.
    2. Preserve evidence identity and lineage.
    3. Detect incompatible evidence contexts.
    4. Detect contradictory directional/value observations when they
       are semantically comparable.
    5. Preserve dissent rather than selecting a winner.

    Non-responsibilities
    -------------------
    - Does not assign confidence.
    - Does not assign reliability.
    - Does not select a winning source.
    - Does not calculate a trading score.
    - Does not make BUY/SELL decisions.
    """

    VERSION = "1.0"

    # Common semantic aliases are intentionally limited to fields that
    # represent the same underlying observation.
    _METRIC_KEYS = (
        "metric",
        "indicator",
        "measure",
        "field",
        "variable",
    )

    _DIRECTION_KEYS = (
        "direction",
        "side",
        "bias",
        "signal",
        "state",
    )

    _VALUE_KEYS = (
        "value",
        "observation",
        "observed_value",
    )

    _IDENTITY_KEYS = (
        "market",
        "market_id",
        "instrument_id",
        "venue_id",
        "timeframe",
        "contract_id",
        "expiry",
    )

    def analyze(
        self,
        package: EvidencePackage,
        *,
        tolerance: float = 0.0,
        temporal_overlap_seconds: float | None = None,
    ) -> ConflictAnalysisResult:
        """
        Analyze an EvidencePackage for deterministic conflicts.

        `tolerance` is only used for comparing numeric values that
        represent the same metric. It must be explicitly supplied and
        can therefore not silently alter conflict semantics.

        `temporal_overlap_seconds`, when supplied, determines the maximum
        time separation for two observations to be considered temporally
        comparable.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(package, EvidencePackage):
            return ConflictAnalysisResult(
                status=ConflictStatus.INVALID,
                package_id=None,
                errors=("package must be an EvidencePackage",),
                reason="Invalid package type.",
            )

        if not package.is_valid():
            return ConflictAnalysisResult(
                status=ConflictStatus.INVALID,
                package_id=package.package_id,
                analyzed_count=len(package.items),
                errors=("EvidencePackage failed structural validation.",),
                reason="Invalid evidence package.",
            )

        if not isfinite(float(tolerance)) or tolerance < 0.0:
            return ConflictAnalysisResult(
                status=ConflictStatus.INVALID,
                package_id=package.package_id,
                analyzed_count=len(package.items),
                errors=("tolerance must be finite and non-negative.",),
                reason="Invalid comparison tolerance.",
            )

        if temporal_overlap_seconds is not None:
            if (
                not isfinite(float(temporal_overlap_seconds))
                or temporal_overlap_seconds < 0.0
            ):
                return ConflictAnalysisResult(
                    status=ConflictStatus.INVALID,
                    package_id=package.package_id,
                    analyzed_count=len(package.items),
                    errors=(
                        "temporal_overlap_seconds must be finite "
                        "and non-negative.",
                    ),
                    reason="Invalid temporal comparison window.",
                )

        if not package.items:
            return ConflictAnalysisResult(
                status=ConflictStatus.INSUFFICIENT,
                package_id=package.package_id,
                analyzed_count=0,
                comparable_count=0,
                reason="No evidence items available for conflict analysis.",
            )

        identity_conflicts = self._detect_identity_conflicts(package)

        duplicate_conflicts = self._detect_duplicate_identity_conflicts(
            package.items
        )

        comparable_groups = self._build_comparable_groups(package.items)

        conflicts: list[EvidenceConflict] = []

        conflicts.extend(identity_conflicts)
        conflicts.extend(duplicate_conflicts)

        for group in comparable_groups:
            conflicts.extend(
                self._analyze_group(
                    group,
                    tolerance=tolerance,
                    temporal_overlap_seconds=temporal_overlap_seconds,
                )
            )

        conflicts = self._deduplicate_conflicts(conflicts)

        comparable_count = sum(
            max(0, len(group) - 1)
            for group in comparable_groups
        )

        if errors:
            status = ConflictStatus.INVALID
            reason = "Conflict analysis failed."
        elif comparable_count == 0 and not conflicts:
            status = ConflictStatus.INSUFFICIENT
            reason = "No comparable evidence relationships were available."
        elif conflicts:
            status = ConflictStatus.PARTIAL
            reason = (
                "Comparable evidence contains one or more detected "
                "conflicts. No conflict was resolved."
            )
        else:
            status = ConflictStatus.VALID
            reason = "No deterministic conflicts detected."

        return ConflictAnalysisResult(
            status=status,
            package_id=package.package_id,
            conflicts=tuple(conflicts),
            analyzed_count=len(package.items),
            comparable_count=comparable_count,
            conflict_count=len(conflicts),
            errors=tuple(errors),
            warnings=tuple(warnings),
            analyzer="EvidenceConflictEngine",
            analyzer_version=self.VERSION,
            reason=reason,
        )

    def analyze_items(
        self,
        items: Iterable[EvidenceItem],
        *,
        package_id: str = "UNPACKAGED",
        tolerance: float = 0.0,
        temporal_overlap_seconds: float | None = None,
    ) -> ConflictAnalysisResult:
        """
        Convenience entry point for an iterable of EvidenceItem objects.
        """
        normalized_items = tuple(items)

        if not all(isinstance(item, EvidenceItem) for item in normalized_items):
            return ConflictAnalysisResult(
                status=ConflictStatus.INVALID,
                package_id=package_id,
                analyzed_count=len(normalized_items),
                errors=("All items must be EvidenceItem instances.",),
                reason="Invalid evidence collection.",
            )

        package = EvidencePackage(
            package_id=package_id,
            items=normalized_items,
        )

        return self.analyze(
            package,
            tolerance=tolerance,
            temporal_overlap_seconds=temporal_overlap_seconds,
        )

    # ------------------------------------------------------------------
    # Group construction
    # ------------------------------------------------------------------

    def _build_comparable_groups(
        self,
        items: Sequence[EvidenceItem],
    ) -> list[tuple[EvidenceItem, ...]]:
        """
        Group evidence only when it can reasonably describe the same
        semantic observation.

        Evidence is never grouped merely because it has the same source.
        """
        groups: dict[tuple[Any, ...], list[EvidenceItem]] = {}

        for item in items:
            metric = self._extract_metric(item)

            # Without a metric/type anchor, two arbitrary values must not
            # be compared merely because they happen to be numeric.
            if metric is None and item.evidence_type is None:
                continue

            key = (
                item.market,
                item.instrument_id,
                item.timeframe,
                item.evidence_type,
                metric,
            )

            groups.setdefault(key, []).append(item)

        return [
            tuple(sorted(group, key=self._sort_key))
            for group in groups.values()
            if len(group) > 1
        ]

    # ------------------------------------------------------------------
    # Group analysis
    # ------------------------------------------------------------------

    def _analyze_group(
        self,
        group: Sequence[EvidenceItem],
        *,
        tolerance: float,
        temporal_overlap_seconds: float | None,
    ) -> list[EvidenceConflict]:
        conflicts: list[EvidenceConflict] = []

        for index, left in enumerate(group):
            for right in group[index + 1 :]:
                if not self._temporally_comparable(
                    left,
                    right,
                    temporal_overlap_seconds,
                ):
                    continue

                direction_conflict = self._direction_conflict(left, right)

                if direction_conflict:
                    conflicts.append(
                        self._make_conflict(
                            ConflictType.DIRECTION,
                            (left, right),
                            reason=direction_conflict,
                        )
                    )
                    continue

                value_conflict = self._value_conflict(
                    left,
                    right,
                    tolerance=tolerance,
                )

                if value_conflict:
                    conflicts.append(
                        self._make_conflict(
                            ConflictType.VALUE,
                            (left, right),
                            reason=value_conflict,
                        )
                    )

        return conflicts

    def _direction_conflict(
        self,
        left: EvidenceItem,
        right: EvidenceItem,
    ) -> str | None:
        left_direction = self._extract_direction(left)
        right_direction = self._extract_direction(right)

        if left_direction is None or right_direction is None:
            return None

        if left_direction == right_direction:
            return None

        if not self._is_known_direction(left_direction):
            return None

        if not self._is_known_direction(right_direction):
            return None

        return (
            f"Directional disagreement: {left_direction!r} "
            f"versus {right_direction!r}."
        )

    def _value_conflict(
        self,
        left: EvidenceItem,
        right: EvidenceItem,
        *,
        tolerance: float,
    ) -> str | None:
        left_value = self._extract_value(left)
        right_value = self._extract_value(right)

        if left_value is None or right_value is None:
            return None

        if isinstance(left_value, bool) or isinstance(right_value, bool):
            if left_value != right_value:
                return (
                    f"Boolean disagreement: {left_value!r} "
                    f"versus {right_value!r}."
                )
            return None

        if self._is_numeric(left_value) and self._is_numeric(right_value):
            difference = abs(float(left_value) - float(right_value))

            if difference > tolerance:
                return (
                    f"Numeric disagreement: {left_value!r} "
                    f"versus {right_value!r}; "
                    f"absolute difference={difference} exceeds "
                    f"tolerance={tolerance}."
                )

            return None

        if isinstance(left_value, str) and isinstance(right_value, str):
            if left_value.strip().casefold() != right_value.strip().casefold():
                return (
                    f"Value disagreement: {left_value!r} "
                    f"versus {right_value!r}."
                )

        return None

    # ------------------------------------------------------------------
    # Package-level identity checks
    # ------------------------------------------------------------------

    def _detect_identity_conflicts(
        self,
        package: EvidencePackage,
    ) -> list[EvidenceConflict]:
        conflicts: list[EvidenceConflict] = []

        fields = (
            ("market", package.market),
            ("instrument_id", package.instrument_id),
            ("timeframe", package.timeframe),
        )

        for field_name, package_value in fields:
            values = {
                getattr(item, field_name)
                for item in package.items
                if getattr(item, field_name) is not None
            }

            if package_value is not None:
                values.add(package_value)

            if len(values) > 1:
                conflicts.append(
                    self._make_conflict_from_identity(
                        package.items,
                        field_name,
                        values,
                    )
                )

        return conflicts

    def _make_conflict_from_identity(
        self,
        items: Sequence[EvidenceItem],
        field_name: str,
        values: set[Any],
    ) -> EvidenceConflict:
        evidence_ids = tuple(
            sorted(item.evidence_id for item in items)
        )

        return EvidenceConflict(
            conflict_id=self._conflict_id(
                ConflictType.IDENTITY,
                evidence_ids,
                field_name,
            ),
            conflict_type=ConflictType.IDENTITY,
            evidence_ids=evidence_ids,
            evidence_type=None,
            metric=field_name,
            values=tuple(sorted(map(str, values))),
            reason=(
                f"Incompatible {field_name} values exist in the "
                f"same evidence package."
            ),
            metadata={
                "identity_field": field_name,
                "distinct_values": sorted(map(str, values)),
            },
        )

    # ------------------------------------------------------------------
    # Duplicate IDs
    # ------------------------------------------------------------------

    def _detect_duplicate_identity_conflicts(
        self,
        items: Sequence[EvidenceItem],
    ) -> list[EvidenceConflict]:
        by_id: dict[str, list[EvidenceItem]] = {}

        for item in items:
            by_id.setdefault(item.evidence_id, []).append(item)

        conflicts: list[EvidenceConflict] = []

        for evidence_id, duplicates in by_id.items():
            if len(duplicates) < 2:
                continue

            first = duplicates[0]

            for duplicate in duplicates[1:]:
                if self._canonical_item(first) == self._canonical_item(
                    duplicate
                ):
                    # Exact duplicate is not a semantic conflict.
                    continue

                conflicts.append(
                    EvidenceConflict(
                        conflict_id=self._conflict_id(
                            ConflictType.VALUE,
                            (
                                first.evidence_id,
                                duplicate.evidence_id,
                            ),
                            "duplicate_evidence_id",
                        ),
                        conflict_type=ConflictType.VALUE,
                        evidence_ids=(
                            first.evidence_id,
                            duplicate.evidence_id,
                        ),
                        evidence_type=first.evidence_type,
                        metric="duplicate_evidence_id",
                        values=(
                            first.value,
                            duplicate.value,
                        ),
                        reason=(
                            "The same evidence_id represents "
                            "different evidence content."
                        ),
                        metadata={
                            "duplicate_evidence_id": evidence_id,
                            "semantic_conflict": True,
                        },
                    )
                )

        return conflicts

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_metric(self, item: EvidenceItem) -> str | None:
        metadata = item.metadata

        for key in self._METRIC_KEYS:
            value = metadata.get(key)

            if value is not None:
                return str(value)

        return item.evidence_type or None

    def _extract_direction(self, item: EvidenceItem) -> str | None:
        metadata = item.metadata

        for key in self._DIRECTION_KEYS:
            value = metadata.get(key)

            if value is not None:
                return self._normalize_direction(value)

        if isinstance(item.value, str):
            normalized = self._normalize_direction(item.value)

            if self._is_known_direction(normalized):
                return normalized

        return None

    def _extract_value(self, item: EvidenceItem) -> Any:
        metadata = item.metadata

        for key in self._VALUE_KEYS:
            if key in metadata:
                return metadata[key]

        return item.value

    @staticmethod
    def _normalize_direction(value: Any) -> str:
        return str(value).strip().upper()

    @staticmethod
    def _is_known_direction(value: str | None) -> bool:
        if value is None:
            return False

        return value in {
            "BUY",
            "SELL",
            "LONG",
            "SHORT",
            "BULLISH",
            "BEARISH",
            "UP",
            "DOWN",
            "POSITIVE",
            "NEGATIVE",
        }

    # ------------------------------------------------------------------
    # Temporal comparability
    # ------------------------------------------------------------------

    def _temporally_comparable(
        self,
        left: EvidenceItem,
        right: EvidenceItem,
        temporal_overlap_seconds: float | None,
    ) -> bool:
        if temporal_overlap_seconds is None:
            return True

        delta = abs(
            (
                left.observed_at - right.observed_at
            ).total_seconds()
        )

        return delta <= temporal_overlap_seconds

    # ------------------------------------------------------------------
    # Canonicalization / deterministic identity
    # ------------------------------------------------------------------

    def _canonical_item(
        self,
        item: EvidenceItem,
    ) -> tuple[Any, ...]:
        return (
            item.evidence_id,
            item.evidence_type,
            item.source,
            self._freeze(item.value),
            item.observed_at.astimezone(timezone.utc).isoformat(),
            item.market,
            item.instrument_id,
            item.timeframe,
            item.confidence,
            item.quality,
            item.description,
            self._freeze(dict(item.metadata)),
        )

    def _make_conflict(
        self,
        conflict_type: ConflictType,
        items: Sequence[EvidenceItem],
        *,
        reason: str,
    ) -> EvidenceConflict:
        evidence_ids = tuple(
            sorted(item.evidence_id for item in items)
        )

        evidence_type = items[0].evidence_type if items else None
        metric = self._extract_metric(items[0]) if items else None

        return EvidenceConflict(
            conflict_id=self._conflict_id(
                conflict_type,
                evidence_ids,
                metric or "",
            ),
            conflict_type=conflict_type,
            evidence_ids=evidence_ids,
            evidence_type=evidence_type,
            metric=metric,
            values=tuple(
                self._extract_value(item)
                for item in items
            ),
            reason=reason,
            metadata={
                "sources": tuple(
                    sorted(item.source for item in items)
                ),
                "observed_at": tuple(
                    item.observed_at.astimezone(timezone.utc).isoformat()
                    for item in items
                ),
            },
        )

    @staticmethod
    def _conflict_id(
        conflict_type: ConflictType,
        evidence_ids: Sequence[str],
        metric: str,
    ) -> str:
        import hashlib

        canonical = "|".join(
            [
                conflict_type.value,
                metric,
                *sorted(evidence_ids),
            ]
        )

        digest = hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()[:24]

        return f"CONFLICT-{digest}"

    @staticmethod
    def _sort_key(item: EvidenceItem) -> tuple[str, str, str, str]:
        return (
            item.observed_at.astimezone(timezone.utc).isoformat(),
            item.evidence_type,
            item.evidence_id,
            item.source,
        )

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and isfinite(float(value))
        )

    def _deduplicate_conflicts(
        self,
        conflicts: Sequence[EvidenceConflict],
    ) -> list[EvidenceConflict]:
        unique: dict[str, EvidenceConflict] = {}

        for conflict in conflicts:
            unique[conflict.conflict_id] = conflict

        return [
            unique[key]
            for key in sorted(unique)
        ]

    @classmethod
    def _freeze(cls, value: Any) -> Any:
        """
        Convert nested metadata/value structures into deterministic,
        hash/comparison-friendly representations.
        """
        if isinstance(value, Mapping):
            return tuple(
                sorted(
                    (
                        str(key),
                        cls._freeze(val),
                    )
                    for key, val in value.items()
                )
            )

        if isinstance(value, (list, tuple)):
            return tuple(cls._freeze(item) for item in value)

        if isinstance(value, set):
            return tuple(
                sorted(cls._freeze(item) for item in value)
            )

        if isinstance(value, datetime):
            return value.astimezone(timezone.utc).isoformat()

        try:
            hash(value)
            return value
        except TypeError:
            return repr(value)


# ----------------------------------------------------------------------
# Convenience API
# ----------------------------------------------------------------------

def detect_evidence_conflicts(
    package: EvidencePackage,
    *,
    tolerance: float = 0.0,
    temporal_overlap_seconds: float | None = None,
) -> ConflictAnalysisResult:
    """
    Detect conflicts in an EvidencePackage.
    """
    return EvidenceConflictEngine().analyze(
        package,
        tolerance=tolerance,
        temporal_overlap_seconds=temporal_overlap_seconds,
    )


# ----------------------------------------------------------------------
# Deterministic self-test
# ----------------------------------------------------------------------

def _self_test() -> None:
    from datetime import timedelta

    t0 = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    buy = EvidenceItem(
        evidence_id="E-001",
        evidence_type="direction",
        source="feed_a",
        value="BUY",
        observed_at=t0,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    sell = EvidenceItem(
        evidence_id="E-002",
        evidence_type="direction",
        source="feed_b",
        value="SELL",
        observed_at=t0 + timedelta(seconds=1),
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    package = EvidencePackage(
        package_id="PKG-001",
        items=(buy, sell),
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    engine = EvidenceConflictEngine()

    result = engine.analyze(
        package,
        temporal_overlap_seconds=5.0,
    )

    assert result.status == ConflictStatus.PARTIAL
    assert result.conflict_count == 1
    assert result.conflicts[0].conflict_type == ConflictType.DIRECTION
    assert result.is_valid()

    # Exact duplicate is not treated as a semantic conflict.
    duplicate = EvidenceItem(
        evidence_id="E-003",
        evidence_type="direction",
        source="feed_c",
        value="BUY",
        observed_at=t0,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    duplicate_copy = EvidenceItem(
        evidence_id="E-003",
        evidence_type="direction",
        source="feed_c",
        value="BUY",
        observed_at=t0,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    duplicate_package = EvidencePackage(
        package_id="PKG-002",
        items=(duplicate, duplicate_copy),
    )

    duplicate_result = engine.analyze(duplicate_package)

    assert duplicate_result.conflict_count == 0

    # Same ID with different content must be detected.
    conflicting_duplicate = EvidenceItem(
        evidence_id="E-003",
        evidence_type="direction",
        source="feed_c",
        value="SELL",
        observed_at=t0,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="5m",
    )

    conflicting_package = EvidencePackage(
        package_id="PKG-003",
        items=(duplicate, conflicting_duplicate),
    )

    conflicting_result = engine.analyze(conflicting_package)

    assert conflicting_result.conflict_count == 1

    # Mixed instrument identity must never be silently compared as
    # though it were the same market object.
    other_instrument = EvidenceItem(
        evidence_id="E-004",
        evidence_type="direction",
        source="feed_d",
        value="SELL",
        observed_at=t0,
        market="NSE",
        instrument_id="BANKNIFTY",
        timeframe="5m",
    )

    mixed_package = EvidencePackage(
        package_id="PKG-004",
        items=(buy, other_instrument),
    )

    mixed_result = engine.analyze(mixed_package)

    assert any(
        conflict.conflict_type == ConflictType.IDENTITY
        for conflict in mixed_result.conflicts
    )

    # Deterministic conflict identity.
    result_again = engine.analyze(
        package,
        temporal_overlap_seconds=5.0,
    )

    assert (
        result.conflicts[0].conflict_id
        == result_again.conflicts[0].conflict_id
    )


__all__ = [
    "ConflictStatus",
    "ConflictType",
    "EvidenceConflict",
    "ConflictAnalysisResult",
    "EvidenceConflictEngine",
    "detect_evidence_conflicts",
]