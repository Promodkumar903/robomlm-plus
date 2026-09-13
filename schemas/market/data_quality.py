"""
ROBOMLM PLUS
V6 Market Data Quality Schema

Purpose:
    Structural representation of market-data quality and provenance.

Rules:
    - Data quality only.
    - No trading decisions.
    - No intelligence generation.
    - No execution logic.
    - No V7+ dependency.
    - Does not alter the original market observation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
from numbers import Real
from typing import Any, Mapping, Optional


DATA_QUALITY_SCHEMA_VERSION = "1.0.0"
DATA_QUALITY_SCHEMA = "V6_DATA_QUALITY"


@dataclass(frozen=True)
class DataQuality:
    """
    Immutable quality descriptor for a market-data observation.
    """

    # ---------------------------------------------------------
    # Overall Quality
    # ---------------------------------------------------------
    score: Optional[float] = None
    status: str = "UNKNOWN"

    # ---------------------------------------------------------
    # Source / Provenance
    # ---------------------------------------------------------
    source: Optional[str] = None
    source_type: Optional[str] = None

    # ---------------------------------------------------------
    # Freshness / Timing
    # ---------------------------------------------------------
    is_live: Optional[bool] = None
    stale: Optional[bool] = None
    latency_ms: Optional[float] = None

    # ---------------------------------------------------------
    # Completeness / Consistency
    # ---------------------------------------------------------
    completeness_pct: Optional[float] = None
    consistency: Optional[bool] = None

    # ---------------------------------------------------------
    # Missing / Invalid Information
    # ---------------------------------------------------------
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    invalid_fields: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    # ---------------------------------------------------------
    # Additional Metadata
    # ---------------------------------------------------------
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural quality information."""

        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------
        if self.score is not None:
            if isinstance(self.score, bool):
                raise TypeError("DataQuality.score must be numeric.")

            if not isinstance(self.score, Real):
                raise TypeError(
                    "DataQuality.score must be numeric or None."
                )

            if not isfinite(float(self.score)):
                raise ValueError(
                    "DataQuality.score must be finite when provided."
                )

            if not 0 <= self.score <= 100:
                raise ValueError(
                    "DataQuality.score must be between 0 and 100."
                )

        # -----------------------------------------------------
        # Completeness
        # -----------------------------------------------------
        if self.completeness_pct is not None:
            if isinstance(self.completeness_pct, bool):
                raise TypeError(
                    "DataQuality.completeness_pct must be numeric."
                )

            if not isinstance(self.completeness_pct, Real):
                raise TypeError(
                    "DataQuality.completeness_pct must be numeric or None."
                )

            if not isfinite(float(self.completeness_pct)):
                raise ValueError(
                    "DataQuality.completeness_pct "
                    "must be finite when provided."
                )

            if not 0 <= self.completeness_pct <= 100:
                raise ValueError(
                    "DataQuality.completeness_pct "
                    "must be between 0 and 100."
                )

        # -----------------------------------------------------
        # Latency
        # -----------------------------------------------------
        if self.latency_ms is not None:
            if isinstance(self.latency_ms, bool):
                raise TypeError(
                    "DataQuality.latency_ms must be numeric."
                )

            if not isinstance(self.latency_ms, Real):
                raise TypeError(
                    "DataQuality.latency_ms must be numeric or None."
                )

            if not isfinite(float(self.latency_ms)):
                raise ValueError(
                    "DataQuality.latency_ms "
                    "must be finite when provided."
                )

            if self.latency_ms < 0:
                raise ValueError(
                    "DataQuality.latency_ms cannot be negative."
                )

        # -----------------------------------------------------
        # Issue Collections
        # -----------------------------------------------------
        if not isinstance(self.missing_fields, tuple):
            raise TypeError(
                "DataQuality.missing_fields must be a tuple."
            )

        if not isinstance(self.invalid_fields, tuple):
            raise TypeError(
                "DataQuality.invalid_fields must be a tuple."
            )

        if not isinstance(self.warnings, tuple):
            raise TypeError(
                "DataQuality.warnings must be a tuple."
            )

        # -----------------------------------------------------
        # Metadata
        # -----------------------------------------------------
        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "DataQuality.metadata must be a mapping."
            )

    # ---------------------------------------------------------
    # Quality State
    # ---------------------------------------------------------

    def is_usable(self) -> bool:
        """
        Return whether the data is structurally usable.

        This does not determine whether a trade or decision
        should be made.
        """

        if self.status.upper() in {
            "INVALID",
            "UNUSABLE",
            "REJECTED",
        }:
            return False

        if self.score is not None and self.score < 50:
            return False

        return True

    # ---------------------------------------------------------
    # Issue Detection
    # ---------------------------------------------------------

    def has_issues(self) -> bool:
        """Return True when quality warnings or field problems exist."""

        return bool(
            self.missing_fields
            or self.invalid_fields
            or self.warnings
        )

    def issue_count(self) -> int:
        """Return total number of recorded quality issues."""

        return (
            len(self.missing_fields)
            + len(self.invalid_fields)
            + len(self.warnings)
        )

    # ---------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize quality information into a JSON-safe mapping."""

        data = asdict(self)

        data["missing_fields"] = list(self.missing_fields)
        data["invalid_fields"] = list(self.invalid_fields)
        data["warnings"] = list(self.warnings)
        data["metadata"] = dict(self.metadata)

        return data

    # ---------------------------------------------------------
    # Schema Information
    # ---------------------------------------------------------

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": DATA_QUALITY_SCHEMA,
            "version": DATA_QUALITY_SCHEMA_VERSION,
        }


def data_quality_health() -> dict[str, Any]:
    """Return structural health information for the V6 schema."""

    return {
        "schema": DATA_QUALITY_SCHEMA,
        "version": DATA_QUALITY_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "quality_logic_only": True,
        "decision_logic": False,
        "execution_logic": False,
        "intelligence_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "DATA_QUALITY_SCHEMA_VERSION",
    "DATA_QUALITY_SCHEMA",
    "DataQuality",
    "data_quality_health",
]