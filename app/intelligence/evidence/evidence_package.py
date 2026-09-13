from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any, Iterable, Mapping

from schemas.evidence.evidence_item import EvidenceItem
from schemas.evidence.evidence_package import EvidencePackage


class PackageStatus:
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EvidencePackageBuildResult:
    status: str
    package: EvidencePackage | None
    accepted_count: int
    rejected_count: int
    duplicate_count: int
    conflict_count: int
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def is_valid(self) -> bool:
        return self.status == PackageStatus.VALID and self.package is not None


class EvidencePackageEngine:
    """
    Canonical application-layer builder for EvidencePackage.

    Responsibilities
    ----------------
    1. Validate EvidenceItem objects.
    2. Preserve evidence identity and lineage.
    3. Prevent incompatible market/instrument/timeframe mixing.
    4. Detect duplicate and conflicting evidence IDs.
    5. Produce deterministic package identity when package_id is omitted.
    6. Preserve missing/partial information instead of inventing values.

    Non-responsibilities
    --------------------
    - Does not calculate confidence.
    - Does not calculate source reliability.
    - Does not resolve conflicts.
    - Does not make trading decisions.
    - Does not manufacture missing evidence.
    """

    ENGINE_NAME = "EvidencePackageEngine"
    VERSION = "1.0"

    def build(
        self,
        items: Iterable[EvidenceItem],
        *,
        package_id: str | None = None,
        market: str | None = None,
        instrument_id: str | None = None,
        timeframe: str | None = None,
        created_at: datetime | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> EvidencePackageBuildResult:
        errors: list[str] = []
        warnings: list[str] = []

        materialized = tuple(items)

        if not materialized:
            return EvidencePackageBuildResult(
                status=PackageStatus.INSUFFICIENT,
                package=None,
                accepted_count=0,
                rejected_count=0,
                duplicate_count=0,
                conflict_count=0,
                warnings=("No evidence items supplied.",),
            )

        for index, item in enumerate(materialized):
            if not isinstance(item, EvidenceItem):
                errors.append(
                    f"item[{index}] is not an EvidenceItem"
                )
                continue

            if not item.is_valid():
                errors.append(
                    f"item[{index}] ({item.evidence_id!r}) failed EvidenceItem validation"
                )

        if errors:
            return EvidencePackageBuildResult(
                status=PackageStatus.INVALID,
                package=None,
                accepted_count=0,
                rejected_count=len(materialized),
                duplicate_count=0,
                conflict_count=0,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )

        normalized_items = self._sort_items(materialized)

        context_result = self._resolve_context(
            normalized_items,
            market=market,
            instrument_id=instrument_id,
            timeframe=timeframe,
        )

        errors.extend(context_result["errors"])
        warnings.extend(context_result["warnings"])

        if errors:
            return EvidencePackageBuildResult(
                status=PackageStatus.INVALID,
                package=None,
                accepted_count=0,
                rejected_count=len(normalized_items),
                duplicate_count=0,
                conflict_count=0,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )

        unique_items, duplicate_count, conflict_count = (
            self._deduplicate(normalized_items, warnings, errors)
        )

        if errors:
            return EvidencePackageBuildResult(
                status=PackageStatus.INVALID,
                package=None,
                accepted_count=len(unique_items),
                rejected_count=len(normalized_items) - len(unique_items),
                duplicate_count=duplicate_count,
                conflict_count=conflict_count,
                errors=tuple(errors),
                warnings=tuple(warnings),
            )

        if not unique_items:
            return EvidencePackageBuildResult(
                status=PackageStatus.INSUFFICIENT,
                package=None,
                accepted_count=0,
                rejected_count=len(normalized_items),
                duplicate_count=duplicate_count,
                conflict_count=conflict_count,
                warnings=tuple(warnings),
            )

        resolved_market = context_result["market"]
        resolved_instrument = context_result["instrument_id"]
        resolved_timeframe = context_result["timeframe"]

        final_metadata = dict(metadata or {})

        final_metadata.update(
            {
                "engine": self.ENGINE_NAME,
                "engine_version": self.VERSION,
                "evidence_count": len(unique_items),
                "unique_source_count": len(
                    {item.source for item in unique_items}
                ),
                "unique_evidence_type_count": len(
                    {item.evidence_type for item in unique_items}
                ),
            }
        )

        observed_times = [
            item.observed_at
            for item in unique_items
            if isinstance(item.observed_at, datetime)
        ]

        if observed_times:
            final_metadata["observed_from"] = min(
                observed_times
            ).astimezone(timezone.utc).isoformat()

            final_metadata["observed_to"] = max(
                observed_times
            ).astimezone(timezone.utc).isoformat()

        final_metadata["duplicate_count"] = duplicate_count

        final_metadata["conflict_count"] = conflict_count

        final_metadata["context_complete"] = all(
            value is not None
            for value in (
                resolved_market,
                resolved_instrument,
                resolved_timeframe,
            )
        )

        if package_id is None:
            package_id = self._deterministic_package_id(
                unique_items,
                market=resolved_market,
                instrument_id=resolved_instrument,
                timeframe=resolved_timeframe,
            )

        try:
            final_created_at = self._validate_created_at(created_at)
        except ValueError as exc:
            return EvidencePackageBuildResult(
                status=PackageStatus.INVALID,
                package=None,
                accepted_count=len(unique_items),
                rejected_count=0,
                duplicate_count=duplicate_count,
                conflict_count=conflict_count,
                errors=(str(exc),),
                warnings=tuple(warnings),
            )

        package = EvidencePackage(
            package_id=package_id,
            items=tuple(unique_items),
            market=resolved_market,
            instrument_id=resolved_instrument,
            timeframe=resolved_timeframe,
            created_at=final_created_at,
            metadata=final_metadata,
        )

        if not package.is_valid():
            return EvidencePackageBuildResult(
                status=PackageStatus.INVALID,
                package=None,
                accepted_count=len(unique_items),
                rejected_count=0,
                duplicate_count=duplicate_count,
                conflict_count=conflict_count,
                errors=("Constructed EvidencePackage failed validation.",),
                warnings=tuple(warnings),
            )

        status = PackageStatus.VALID

        if warnings:
            status = PackageStatus.PARTIAL

        return EvidencePackageBuildResult(
            status=status,
            package=package,
            accepted_count=len(unique_items),
            rejected_count=0,
            duplicate_count=duplicate_count,
            conflict_count=conflict_count,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    # Context
    # ------------------------------------------------------------------

    def _resolve_context(
        self,
        items: tuple[EvidenceItem, ...],
        *,
        market: str | None,
        instrument_id: str | None,
        timeframe: str | None,
    ) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []

        resolved = {}

        for field_name, explicit_value in (
            ("market", market),
            ("instrument_id", instrument_id),
            ("timeframe", timeframe),
        ):
            values = {
                getattr(item, field_name)
                for item in items
                if getattr(item, field_name) is not None
            }

            if explicit_value is not None:
                if values and values != {explicit_value}:
                    errors.append(
                        f"Explicit {field_name} conflicts with evidence context: "
                        f"{explicit_value!r} vs {sorted(map(str, values))}"
                    )
                    continue

                resolved[field_name] = explicit_value
                continue

            if len(values) == 1:
                resolved[field_name] = next(iter(values))
            elif len(values) == 0:
                resolved[field_name] = None
                warnings.append(
                    f"{field_name} is not present in evidence context."
                )
            else:
                errors.append(
                    f"Mixed {field_name} values detected: "
                    f"{sorted(map(str, values))}"
                )

        return {
            "market": resolved.get("market"),
            "instrument_id": resolved.get("instrument_id"),
            "timeframe": resolved.get("timeframe"),
            "errors": errors,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # Duplicate / conflict handling
    # ------------------------------------------------------------------

    def _deduplicate(
        self,
        items: tuple[EvidenceItem, ...],
        warnings: list[str],
        errors: list[str],
    ) -> tuple[list[EvidenceItem], int, int]:
        by_id: dict[str, EvidenceItem] = {}
        unique_items: list[EvidenceItem] = []

        duplicate_count = 0
        conflict_count = 0

        for item in items:
            existing = by_id.get(item.evidence_id)

            if existing is None:
                by_id[item.evidence_id] = item
                unique_items.append(item)
                continue

            if self._canonical_item(existing) == self._canonical_item(item):
                duplicate_count += 1
                warnings.append(
                    f"Exact duplicate evidence ignored: {item.evidence_id}"
                )
                continue

            conflict_count += 1
            errors.append(
                "Conflicting evidence items share the same evidence_id: "
                f"{item.evidence_id}"
            )

        return unique_items, duplicate_count, conflict_count

    # ------------------------------------------------------------------
    # Deterministic identity
    # ------------------------------------------------------------------

    def _deterministic_package_id(
        self,
        items: tuple[EvidenceItem, ...] | list[EvidenceItem],
        *,
        market: str | None,
        instrument_id: str | None,
        timeframe: str | None,
    ) -> str:
        payload = {
            "market": market,
            "instrument_id": instrument_id,
            "timeframe": timeframe,
            "items": [
                self._canonical_item(item)
                for item in items
            ],
        }

        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")

        digest = sha256(encoded).hexdigest()

        return f"EP-{digest[:32]}"

    # ------------------------------------------------------------------
    # Canonical representation
    # ------------------------------------------------------------------

    @staticmethod
    def _canonical_item(item: EvidenceItem) -> dict[str, Any]:
        value = item.to_dict()

        return EvidencePackageEngine._canonicalize_mapping(value)

    @staticmethod
    def _canonicalize_mapping(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(key): EvidencePackageEngine._canonicalize_mapping(
                    nested
                )
                for key, nested in sorted(
                    value.items(),
                    key=lambda pair: str(pair[0]),
                )
            }

        if isinstance(value, (list, tuple)):
            return [
                EvidencePackageEngine._canonicalize_mapping(item)
                for item in value
            ]

        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(
                    "Non-finite numeric value encountered during "
                    "evidence canonicalization."
                )

            return value

        if isinstance(value, datetime):
            if value.tzinfo is None:
                raise ValueError(
                    "Naive datetime encountered during "
                    "evidence canonicalization."
                )

            return value.astimezone(timezone.utc).isoformat()

        return value

    @staticmethod
    def _sort_items(
        items: tuple[EvidenceItem, ...],
    ) -> tuple[EvidenceItem, ...]:
        return tuple(
            sorted(
                items,
                key=lambda item: (
                    item.observed_at.astimezone(timezone.utc),
                    item.evidence_type,
                    item.evidence_id,
                    item.source,
                ),
            )
        )

    @staticmethod
    def _validate_created_at(
        created_at: datetime | None,
    ) -> datetime:
        if created_at is None:
            return datetime.now(timezone.utc)

        if created_at.tzinfo is None:
            raise ValueError(
                "created_at must be timezone-aware."
            )

        return created_at.astimezone(timezone.utc)


# ----------------------------------------------------------------------
# Convenience API
# ----------------------------------------------------------------------

def build_evidence_package(
    items: Iterable[EvidenceItem],
    **kwargs: Any,
) -> EvidencePackageBuildResult:
    return EvidencePackageEngine().build(items, **kwargs)


__all__ = [
    "PackageStatus",
    "EvidencePackageBuildResult",
    "EvidencePackageEngine",
    "build_evidence_package",
]