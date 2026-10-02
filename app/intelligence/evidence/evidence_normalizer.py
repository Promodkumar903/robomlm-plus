from __future__ import annotations

"""
ROBOMLM Evidence Normalizer
===========================

Purpose
-------
Convert heterogeneous evidence outputs into the canonical
schemas.evidence.evidence_item.EvidenceItem representation.

Constitution
------------
1. Normalization MUST NOT invent evidence.
2. Normalization MUST NOT calculate trading decisions.
3. Normalization MUST NOT manufacture confidence.
4. Normalization MUST NOT silently impute missing values.
5. Normalization MUST preserve source and lineage.
6. Normalization MUST preserve the original semantic value.
7. Normalization MUST be deterministic.
8. Invalid evidence MUST be rejected or explicitly reported.
9. Derived evidence remains derived; it is never converted into observation.
10. The normalizer is an Evidence-layer component only.

Canonical flow
--------------
Raw engine output
        ↓
Input validation
        ↓
Identity normalization
        ↓
Timestamp normalization
        ↓
Metadata normalization
        ↓
Canonical EvidenceItem
        ↓
EvidencePackage
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from numbers import Real
from typing import Any, Iterable, Mapping

from schemas.evidence.evidence_item import EvidenceItem


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

NORMALIZER_NAME = "EvidenceNormalizer"
NORMALIZER_VERSION = "1.0"

DEFAULT_SOURCE = "unknown"

# These keys are semantic aliases only.
# They are NOT used to alter the evidence value.
_ENGINE_KEYS = (
    "engine",
    "source",
    "evidence_source",
)

_TYPE_KEYS = (
    "evidence_type",
    "metric",
    "type",
    "name",
)

_VALUE_KEYS = (
    "value",
    "result",
    "output",
)

_TIMESTAMP_KEYS = (
    "observed_at",
    "timestamp",
    "time",
)

_MARKET_KEYS = (
    "market",
    "market_id",
)

_INSTRUMENT_KEYS = (
    "instrument_id",
    "symbol",
    "instrument",
)

_TIMEFRAME_KEYS = (
    "timeframe",
    "interval",
)

_CONFIDENCE_KEYS = (
    "confidence",
)

_QUALITY_KEYS = (
    "quality",
    "status",
)

# Metadata fields that carry lineage / calculation information.
_LINEAGE_KEYS = (
    "lineage",
    "calculation",
    "inputs",
    "source_type",
    "unit",
    "reason",
    "layer",
    "metric",
    "evidence_kind",
    "evidence_status",
    "integrity_state",
    "observation_id",
)


# ---------------------------------------------------------------------------
# RESULT CONTRACT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NormalizationResult:
    """
    Result of evidence normalization.

    The result is deliberately separate from EvidenceItem so that
    normalization failures can be audited without manufacturing evidence.
    """

    status: str
    items: tuple[EvidenceItem, ...] = field(default_factory=tuple)

    normalized_count: int = 0
    rejected_count: int = 0

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    normalizer: str = NORMALIZER_NAME
    version: str = NORMALIZER_VERSION

    def is_valid(self) -> bool:
        """
        Structural validity.

        VALID means every supplied item was normalized successfully.
        PARTIAL means at least one item succeeded and at least one failed.
        INSUFFICIENT means nothing usable was produced.
        INVALID means an explicit invalid condition was encountered and
        no valid evidence was produced.
        """

        if self.status == "VALID":
            return (
                self.normalized_count == len(self.items)
                and self.rejected_count == 0
                and all(item.is_valid() for item in self.items)
            )

        if self.status == "PARTIAL":
            return (
                self.normalized_count > 0
                and self.rejected_count > 0
                and all(item.is_valid() for item in self.items)
            )

        if self.status == "INSUFFICIENT":
            return self.normalized_count == 0

        if self.status == "INVALID":
            return self.normalized_count == 0

        return False


# ---------------------------------------------------------------------------
# NORMALIZER
# ---------------------------------------------------------------------------

class EvidenceNormalizer:
    """
    Canonicalizes evidence into EvidenceItem.

    Important:
        This class does NOT assign a confidence score.

    If confidence is supplied by the originating evidence source,
    it is validated and preserved. If absent, it remains None.
    """

    def __init__(
        self,
        *,
        normalizer_name: str = NORMALIZER_NAME,
        normalizer_version: str = NORMALIZER_VERSION,
    ) -> None:
        self.normalizer_name = self._require_text(
            normalizer_name,
            "normalizer_name",
        )
        self.normalizer_version = self._require_text(
            normalizer_version,
            "normalizer_version",
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def normalize(
        self,
        evidence: EvidenceItem | Mapping[str, Any],
    ) -> EvidenceItem:
        """
        Normalize one evidence object.

        Accepted inputs:
            - EvidenceItem
            - Mapping[str, Any]

        Returns:
            Canonical EvidenceItem

        Raises:
            TypeError
            ValueError
        """

        if isinstance(evidence, EvidenceItem):
            return self._normalize_existing_item(evidence)

        if isinstance(evidence, Mapping):
            return self._normalize_mapping(evidence)

        raise TypeError(
            "evidence must be an EvidenceItem or Mapping[str, Any]"
        )

    def normalize_many(
        self,
        evidence: Iterable[EvidenceItem | Mapping[str, Any]],
    ) -> NormalizationResult:
        """
        Normalize a collection without hiding individual failures.

        One malformed evidence item does not corrupt the valid items.
        Every rejection is explicitly recorded.
        """

        normalized: list[EvidenceItem] = []
        errors: list[str] = []
        warnings: list[str] = []

        for index, item in enumerate(evidence):
            try:
                normalized_item = self.normalize(item)
                normalized.append(normalized_item)

            except (TypeError, ValueError) as exc:
                errors.append(
                    f"item[{index}] rejected: {type(exc).__name__}: {exc}"
                )

        normalized_count = len(normalized)
        rejected_count = len(errors)

        if normalized_count == 0:
            status = "INVALID" if rejected_count else "INSUFFICIENT"

        elif rejected_count == 0:
            status = "VALID"

        else:
            status = "PARTIAL"

        return NormalizationResult(
            status=status,
            items=tuple(normalized),
            normalized_count=normalized_count,
            rejected_count=rejected_count,
            errors=tuple(errors),
            warnings=tuple(warnings),
            normalizer=self.normalizer_name,
            version=self.normalizer_version,
        )

    # ------------------------------------------------------------------
    # EXISTING EVIDENCE ITEM
    # ------------------------------------------------------------------

    def _normalize_existing_item(
        self,
        item: EvidenceItem,
    ) -> EvidenceItem:
        """
        Canonicalize an already-created EvidenceItem.

        No semantic value is changed.
        """

        if not item.is_valid():
            raise ValueError(
                f"EvidenceItem '{item.evidence_id}' failed structural validation"
            )

        evidence_id = self._normalize_identifier(
            item.evidence_id,
            "evidence_id",
        )

        evidence_type = self._normalize_identifier(
            item.evidence_type,
            "evidence_type",
        )

        source = self._normalize_identifier(
            item.source,
            "source",
        )

        observed_at = self._normalize_timestamp(item.observed_at)

        confidence = self._normalize_confidence(item.confidence)

        quality = self._normalize_optional_text(item.quality)

        market = self._normalize_optional_text(item.market)

        instrument_id = self._normalize_optional_text(
            item.instrument_id
        )

        timeframe = self._normalize_optional_text(item.timeframe)

        metadata = self._normalize_metadata(item.metadata)

        # Preserve the exact semantic value.
        value = self._normalize_value(item.value)

        return EvidenceItem(
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            source=source,
            value=value,
            observed_at=observed_at,
            market=market,
            instrument_id=instrument_id,
            timeframe=timeframe,
            confidence=confidence,
            quality=quality,
            description=item.description,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # MAPPING INPUT
    # ------------------------------------------------------------------

    def _normalize_mapping(
        self,
        raw: Mapping[str, Any],
    ) -> EvidenceItem:
        """
        Convert a heterogeneous engine mapping into EvidenceItem.
        """

        if not raw:
            raise ValueError("evidence mapping is empty")

        evidence_id = self._extract_required(
            raw,
            "evidence_id",
        )

        evidence_type = self._extract_first(
            raw,
            _TYPE_KEYS,
        )

        if evidence_type is None:
            raise ValueError(
                "evidence_type is required; metric/type/name cannot all be absent"
            )

        source = self._extract_first(
            raw,
            _ENGINE_KEYS,
        )

        if source is None:
            raise ValueError(
                "source is required; evidence provenance cannot be invented"
            )

        value = self._extract_first(
            raw,
            _VALUE_KEYS,
        )

        observed_at = self._extract_first(
            raw,
            _TIMESTAMP_KEYS,
        )

        if observed_at is None:
            raise ValueError(
                "observed_at/timestamp/time is required for canonical evidence"
            )

        market = self._extract_first(
            raw,
            _MARKET_KEYS,
        )

        instrument_id = self._extract_first(
            raw,
            _INSTRUMENT_KEYS,
        )

        timeframe = self._extract_first(
            raw,
            _TIMEFRAME_KEYS,
        )

        confidence = self._extract_first(
            raw,
            _CONFIDENCE_KEYS,
        )

        quality = self._extract_first(
            raw,
            _QUALITY_KEYS,
        )

        description = raw.get("description")

        metadata = self._build_metadata(raw)

        return EvidenceItem(
            evidence_id=self._normalize_identifier(
                evidence_id,
                "evidence_id",
            ),
            evidence_type=self._normalize_identifier(
                evidence_type,
                "evidence_type",
            ),
            source=self._normalize_identifier(
                source,
                "source",
            ),
            value=self._normalize_value(value),
            observed_at=self._normalize_timestamp(observed_at),
            market=self._normalize_optional_text(market),
            instrument_id=self._normalize_optional_text(
                instrument_id
            ),
            timeframe=self._normalize_optional_text(
                timeframe
            ),
            confidence=self._normalize_confidence(confidence),
            quality=self._normalize_optional_text(quality),
            description=self._normalize_optional_text(description),
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # METADATA / LINEAGE
    # ------------------------------------------------------------------

    def _build_metadata(
        self,
        raw: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Preserve non-canonical information as metadata.

        Nothing is discarded merely because the normalizer does not
        understand its semantic meaning.
        """

        metadata: dict[str, Any] = {}

        supplied_metadata = raw.get("metadata")

        if supplied_metadata is not None:
            if not isinstance(supplied_metadata, Mapping):
                raise ValueError(
                    "metadata must be a mapping when supplied"
                )

            metadata.update(
                self._normalize_metadata(supplied_metadata)
            )

        canonical_keys = {
            "evidence_id",
            "evidence_type",
            "source",
            "value",
            "observed_at",
            "timestamp",
            "time",
            "market",
            "market_id",
            "instrument_id",
            "symbol",
            "instrument",
            "timeframe",
            "interval",
            "confidence",
            "quality",
            "status",
            "description",
            "metadata",
        }

        # Preserve every additional field instead of silently throwing it
        # away. This is important for lineage and auditability.
        for key, value in raw.items():
            if key in canonical_keys:
                continue

            metadata[str(key)] = self._normalize_metadata_value(value)

        # Preserve explicit lineage-related fields visibly.
        for key in _LINEAGE_KEYS:
            if key in raw:
                metadata[key] = self._normalize_metadata_value(
                    raw[key]
                )

        metadata.setdefault(
            "normalized_by",
            self.normalizer_name,
        )

        metadata.setdefault(
            "normalizer_version",
            self.normalizer_version,
        )

        return metadata

    # ------------------------------------------------------------------
    # VALUE NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize_value(self, value: Any) -> Any:
        """
        Normalize representation without changing semantic meaning.

        Numeric values:
            - finite numbers accepted
            - NaN rejected
            - +/- infinity rejected

        Collections:
            recursively normalized

        Strings:
            whitespace around the string is removed

        None:
            preserved as None
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, Real):
            numeric = float(value)

            if not math.isfinite(numeric):
                raise ValueError(
                    "evidence value must be finite"
                )

            return value

        if isinstance(value, datetime):
            return self._normalize_timestamp(value)

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, Mapping):
            return {
                str(key): self._normalize_metadata_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return tuple(
                self._normalize_value(item)
                for item in value
            )

        # Do not coerce unknown domain objects into strings.
        # Semantic loss is worse than rejection.
        raise TypeError(
            "unsupported evidence value type: "
            f"{type(value).__name__}"
        )

    # ------------------------------------------------------------------
    # METADATA VALUE NORMALIZATION
    # ------------------------------------------------------------------

    def _normalize_metadata_value(self, value: Any) -> Any:
        """
        Recursively make metadata deterministic while preserving meaning.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, Real):
            numeric = float(value)

            if not math.isfinite(numeric):
                raise ValueError(
                    "metadata numeric value must be finite"
                )

            return value

        if isinstance(value, datetime):
            return self._normalize_timestamp(value)

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, Mapping):
            return {
                str(key): self._normalize_metadata_value(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return tuple(
                self._normalize_metadata_value(item)
                for item in value
            )

        # Preserve simple immutable scalar-like objects only when safe.
        if isinstance(value, (bytes,)):
            return value.hex()

        raise TypeError(
            "unsupported metadata value type: "
            f"{type(value).__name__}"
        )

    def _normalize_metadata(
        self,
        metadata: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            str(key): self._normalize_metadata_value(value)
            for key, value in metadata.items()
        }

    # ------------------------------------------------------------------
    # TIMESTAMP
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_timestamp(
        timestamp: datetime | str,
    ) -> datetime:
        """
        Canonical timestamp representation = timezone-aware UTC.

        Naive timestamps are rejected because their timezone cannot
        be inferred safely.
        """

        if isinstance(timestamp, str):
            text = timestamp.strip()

            if not text:
                raise ValueError("timestamp cannot be empty")

            # Accept ISO-8601 strings, including trailing Z.
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"

            try:
                timestamp = datetime.fromisoformat(text)
            except ValueError as exc:
                raise ValueError(
                    f"invalid ISO-8601 timestamp: {timestamp!r}"
                ) from exc

        if not isinstance(timestamp, datetime):
            raise TypeError(
                "observed_at must be datetime or ISO-8601 string"
            )

        if timestamp.tzinfo is None:
            raise ValueError(
                "naive timestamp rejected; timezone information is required"
            )

        return timestamp.astimezone(timezone.utc)

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_confidence(
        confidence: Any,
    ) -> float | None:
        """
        Validate supplied confidence.

        IMPORTANT:
            This method validates an existing confidence value.
            It never creates one.
        """

        if confidence is None:
            return None

        if isinstance(confidence, bool):
            raise TypeError(
                "confidence must be numeric, not boolean"
            )

        if not isinstance(confidence, Real):
            raise TypeError(
                "confidence must be numeric"
            )

        confidence_value = float(confidence)

        if not math.isfinite(confidence_value):
            raise ValueError(
                "confidence must be finite"
            )

        if not 0.0 <= confidence_value <= 100.0:
            raise ValueError(
                "confidence must be within [0, 100]"
            )

        return confidence_value

    # ------------------------------------------------------------------
    # IDENTIFIERS / TEXT
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_identifier(
        value: Any,
        field_name: str,
    ) -> str:
        if value is None:
            raise ValueError(
                f"{field_name} cannot be None"
            )

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized

    @staticmethod
    def _normalize_optional_text(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                "optional textual field must be a string"
            )

        normalized = value.strip()

        return normalized if normalized else None

    # ------------------------------------------------------------------
    # EXTRACTION HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_required(
        mapping: Mapping[str, Any],
        key: str,
    ) -> Any:
        if key not in mapping:
            raise ValueError(
                f"{key} is required"
            )

        value = mapping[key]

        if value is None:
            raise ValueError(
                f"{key} cannot be None"
            )

        return value

    @staticmethod
    def _extract_first(
        mapping: Mapping[str, Any],
        keys: tuple[str, ...],
    ) -> Any:
        for key in keys:
            if key in mapping and mapping[key] is not None:
                return mapping[key]

        return None

    @staticmethod
    def _require_text(
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return value


# ---------------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------------------------------

def normalize_evidence(
    evidence: EvidenceItem | Mapping[str, Any],
) -> EvidenceItem:
    """
    Stateless convenience API.
    """

    return EvidenceNormalizer().normalize(evidence)


def normalize_evidence_many(
    evidence: Iterable[EvidenceItem | Mapping[str, Any]],
) -> NormalizationResult:
    """
    Stateless batch normalization API.
    """

    return EvidenceNormalizer().normalize_many(evidence)


# ---------------------------------------------------------------------------
# SELF-TESTS
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """
    Deterministic mathematical/structural smoke tests.

    These tests intentionally verify invariants rather than trading
    outcomes.
    """

    observed_at = datetime(
        2026,
        9,
        4,
        4,
        0,
        0,
        tzinfo=timezone.utc,
    )

    # --------------------------------------------------------------
    # TEST 1: Mapping → EvidenceItem
    # --------------------------------------------------------------

    raw = {
        "evidence_id": "NED-TEST-001",
        "metric": "net_execution_delta",
        "source": "test_feed",
        "value": 125.5,
        "observed_at": observed_at,
        "market": "TEST",
        "instrument_id": "TEST/USDT",
        "timeframe": "1m",
        "metadata": {
            "unit": "contracts",
            "evidence_kind": "DERIVED",
        },
    }

    item = normalize_evidence(raw)

    assert isinstance(item, EvidenceItem)
    assert item.evidence_id == "NED-TEST-001"
    assert item.evidence_type == "net_execution_delta"
    assert item.source == "test_feed"
    assert item.value == 125.5
    assert item.observed_at == observed_at
    assert item.market == "TEST"
    assert item.instrument_id == "TEST/USDT"
    assert item.timeframe == "1m"
    assert item.confidence is None
    assert item.is_valid()

    # --------------------------------------------------------------
    # TEST 2: Timezone conversion
    # --------------------------------------------------------------

    local_timestamp = "2026-09-04T09:30:00+05:30"

    converted = normalize_evidence(
        {
            "evidence_id": "TIME-001",
            "evidence_type": "price",
            "source": "feed",
            "value": 100.0,
            "observed_at": local_timestamp,
        }
    )

    assert converted.observed_at.tzinfo is not None
    assert converted.observed_at.utcoffset().total_seconds() == 0
    assert converted.observed_at.hour == 4
    assert converted.observed_at.minute == 0

    # --------------------------------------------------------------
    # TEST 3: Existing EvidenceItem remains semantically unchanged
    # --------------------------------------------------------------

    original = EvidenceItem(
        evidence_id="EXISTING-001",
        evidence_type="volume",
        source="feed",
        value=500,
        observed_at=observed_at,
        market="TEST",
        instrument_id="ABC",
    )

    normalized = normalize_evidence(original)

    assert normalized.value == original.value
    assert normalized.evidence_type == original.evidence_type
    assert normalized.source == original.source
    assert normalized.market == original.market
    assert normalized.instrument_id == original.instrument_id
    assert normalized.confidence is None

    # --------------------------------------------------------------
    # TEST 4: Confidence is validated, not invented
    # --------------------------------------------------------------

    no_confidence = normalize_evidence(
        {
            "evidence_id": "CONF-001",
            "evidence_type": "price",
            "source": "feed",
            "value": 100,
            "observed_at": observed_at,
        }
    )

    assert no_confidence.confidence is None

    supplied_confidence = normalize_evidence(
        {
            "evidence_id": "CONF-002",
            "evidence_type": "price",
            "source": "feed",
            "value": 100,
            "observed_at": observed_at,
            "confidence": 87.5,
        }
    )

    assert supplied_confidence.confidence == 87.5

    # --------------------------------------------------------------
    # TEST 5: NaN rejected
    # --------------------------------------------------------------

    try:
        normalize_evidence(
            {
                "evidence_id": "BAD-001",
                "evidence_type": "price",
                "source": "feed",
                "value": float("nan"),
                "observed_at": observed_at,
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "NaN evidence value must be rejected"
        )

    # --------------------------------------------------------------
    # TEST 6: Infinity rejected
    # --------------------------------------------------------------

    try:
        normalize_evidence(
            {
                "evidence_id": "BAD-002",
                "evidence_type": "price",
                "source": "feed",
                "value": float("inf"),
                "observed_at": observed_at,
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Infinite evidence value must be rejected"
        )

    # --------------------------------------------------------------
    # TEST 7: Naive datetime rejected
    # --------------------------------------------------------------

    try:
        normalize_evidence(
            {
                "evidence_id": "BAD-003",
                "evidence_type": "price",
                "source": "feed",
                "value": 100,
                "observed_at": datetime(2026, 9, 4),
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Naive timestamps must be rejected"
        )

    # --------------------------------------------------------------
    # TEST 8: Missing provenance rejected
    # --------------------------------------------------------------

    try:
        normalize_evidence(
            {
                "evidence_id": "BAD-004",
                "evidence_type": "price",
                "value": 100,
                "observed_at": observed_at,
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Evidence without source must be rejected"
        )

    # --------------------------------------------------------------
    # TEST 9: Batch normalization preserves valid evidence
    # --------------------------------------------------------------

    batch = normalize_evidence_many(
        [
            {
                "evidence_id": "BATCH-001",
                "evidence_type": "price",
                "source": "feed",
                "value": 100,
                "observed_at": observed_at,
            },
            {
                "evidence_id": "BATCH-002",
                "evidence_type": "volume",
                "source": "feed",
                "value": 500,
                "observed_at": observed_at,
            },
            {
                "evidence_id": "BATCH-BAD",
                "evidence_type": "price",
                "value": 101,
                "observed_at": observed_at,
            },
        ]
    )

    assert batch.status == "PARTIAL"
    assert batch.normalized_count == 2
    assert batch.rejected_count == 1
    assert len(batch.items) == 2
    assert batch.is_valid()

    # --------------------------------------------------------------
    # TEST 10: No arbitrary confidence generation
    # --------------------------------------------------------------

    for evidence in batch.items:
        assert evidence.confidence is None

    print(
        "EvidenceNormalizer self-test: PASS"
    )


if __name__ == "__main__":
    _self_test()
