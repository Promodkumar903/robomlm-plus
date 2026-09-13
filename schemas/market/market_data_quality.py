from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class DataQualityStatus(str, Enum):
    """
    Descriptive state of the supplied market-data observation.

    This is NOT an intelligence/confidence score.
    """

    VALID = "valid"
    DEGRADED = "degraded"
    INVALID = "invalid"


class DataQualityFlag(str, Enum):
    """
    Explicit, machine-readable data-quality conditions.
    """

    NONE = "none"

    MISSING_REQUIRED_FIELD = "missing_required_field"
    INVALID_VALUE = "invalid_value"
    INVALID_TIMESTAMP = "invalid_timestamp"
    SOURCE_DELAY = "source_delay"
    RECEIPT_DELAY = "receipt_delay"
    STALE = "stale"
    SEQUENCE_GAP = "sequence_gap"
    DUPLICATE = "duplicate"
    OUT_OF_ORDER = "out_of_order"
    SOURCE_ERROR = "source_error"
    PARTIAL = "partial"


@dataclass(frozen=True, slots=True)
class DataQuality:
    """
    Canonical market-data quality contract.

    Responsibilities:
        source identity
        observation/receipt timing
        latency
        completeness
        sequencing
        explicit quality flags
        deterministic validity classification

    Does NOT:
        calculate market intelligence
        calculate confidence
        calculate direction
        authorize decisions
        authorize execution
    """

    source: str
    observed_at: datetime
    received_at: datetime

    status: DataQualityStatus = DataQualityStatus.VALID

    sequence: Optional[int] = None

    required_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    present_fields: tuple[str, ...] = field(
        default_factory=tuple
    )

    flags: tuple[DataQualityFlag, ...] = field(
        default_factory=tuple
    )

    max_age_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        source = self.source.strip()

        if not source:
            raise ValueError(
                "source must not be empty"
            )

        object.__setattr__(
            self,
            "source",
            source,
        )

        if self.observed_at.tzinfo is None:
            raise ValueError(
                "observed_at must be timezone-aware"
            )

        if self.received_at.tzinfo is None:
            raise ValueError(
                "received_at must be timezone-aware"
            )

        observed = self.observed_at.astimezone(
            timezone.utc
        )
        received = self.received_at.astimezone(
            timezone.utc
        )

        if received < observed:
            raise ValueError(
                "received_at cannot precede observed_at"
            )

        object.__setattr__(
            self,
            "observed_at",
            observed,
        )

        object.__setattr__(
            self,
            "received_at",
            received,
        )

        if self.sequence is not None:
            if self.sequence < 0:
                raise ValueError(
                    "sequence must not be negative"
                )

        if self.max_age_seconds is not None:
            if self.max_age_seconds < 0:
                raise ValueError(
                    "max_age_seconds must not be negative"
                )

        required = tuple(
            dict.fromkeys(
                str(value).strip()
                for value in self.required_fields
                if str(value).strip()
            )
        )

        present = tuple(
            dict.fromkeys(
                str(value).strip()
                for value in self.present_fields
                if str(value).strip()
            )
        )

        flags = tuple(
            dict.fromkeys(
                self.flags
            )
        )

        object.__setattr__(
            self,
            "required_fields",
            required,
        )

        object.__setattr__(
            self,
            "present_fields",
            present,
        )

        object.__setattr__(
            self,
            "flags",
            flags,
        )

        # Structural invariant:
        # VALID cannot coexist with explicit invalidity flags.
        invalid_flags = {
            DataQualityFlag.INVALID_VALUE,
            DataQualityFlag.INVALID_TIMESTAMP,
            DataQualityFlag.SOURCE_ERROR,
            DataQualityFlag.MISSING_REQUIRED_FIELD,
        }

        if (
            self.status is DataQualityStatus.VALID
            and invalid_flags.intersection(flags)
        ):
            raise ValueError(
                "VALID quality cannot contain invalidity flags"
            )

    @property
    def latency_seconds(self) -> float:
        """
        Source observation -> system receipt delay.

        This is a measured quantity.
        """

        return max(
            (
                self.received_at
                - self.observed_at
            ).total_seconds(),
            0.0,
        )

    @property
    def latency_ms(self) -> float:
        return self.latency_seconds * 1000.0

    @property
    def missing_required_fields(
        self,
    ) -> tuple[str, ...]:
        """
        Required fields declared by the producer but not present
        in the received observation.

        Missing fields remain explicit; they are never converted to 0.
        """

        present = set(self.present_fields)

        return tuple(
            field_name
            for field_name in self.required_fields
            if field_name not in present
        )

    @property
    def is_complete(self) -> bool:
        return not self.missing_required_fields

    @property
    def is_stale(self) -> bool:
        return DataQualityFlag.STALE in self.flags

    @property
    def is_sequence_valid(self) -> bool:
        return not (
            DataQualityFlag.SEQUENCE_GAP in self.flags
            or DataQualityFlag.OUT_OF_ORDER in self.flags
            or DataQualityFlag.DUPLICATE in self.flags
        )

    @property
    def is_usable(self) -> bool:
        """
        Deterministic data admissibility property.

        VALID data is usable only when required fields,
        timestamps and sequencing are structurally valid.
        """

        if self.status is not DataQualityStatus.VALID:
            return False

        if not self.is_complete:
            return False

        if not self.is_sequence_valid:
            return False

        if DataQualityFlag.INVALID_VALUE in self.flags:
            return False

        if DataQualityFlag.INVALID_TIMESTAMP in self.flags:
            return False

        if DataQualityFlag.SOURCE_ERROR in self.flags:
            return False

        return True

    def with_flags(
        self,
        *new_flags: DataQualityFlag,
    ) -> DataQuality:
        """
        Return a new immutable quality object with additional flags.

        Existing object is never mutated.
        """

        merged = tuple(
            dict.fromkeys(
                (*self.flags, *new_flags)
            )
        )

        status = self.status

        invalid_flags = {
            DataQualityFlag.INVALID_VALUE,
            DataQualityFlag.INVALID_TIMESTAMP,
            DataQualityFlag.SOURCE_ERROR,
            DataQualityFlag.MISSING_REQUIRED_FIELD,
        }

        if invalid_flags.intersection(merged):
            status = DataQualityStatus.INVALID
        elif merged:
            status = DataQualityStatus.DEGRADED

        return DataQuality(
            source=self.source,
            observed_at=self.observed_at,
            received_at=self.received_at,
            status=status,
            sequence=self.sequence,
            required_fields=self.required_fields,
            present_fields=self.present_fields,
            flags=merged,
            max_age_seconds=self.max_age_seconds,
        )

    def evaluate_completeness(self) -> DataQuality:
        """
        Apply the required-field invariant deterministically.
        """

        missing = self.missing_required_fields

        if not missing:
            return self

        return self.with_flags(
            DataQualityFlag.MISSING_REQUIRED_FIELD
        )

    def evaluate_age(self) -> DataQuality:
        """
        Mark data stale only when an explicit maximum age has
        been supplied.

        No arbitrary freshness threshold is invented here.
        """

        if self.max_age_seconds is None:
            return self

        age = self.latency_seconds

        if age <= self.max_age_seconds:
            return self

        return self.with_flags(
            DataQualityFlag.STALE
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "observed_at": self.observed_at.isoformat(),
            "received_at": self.received_at.isoformat(),
            "status": self.status.value,
            "sequence": self.sequence,
            "required_fields": list(
                self.required_fields
            ),
            "present_fields": list(
                self.present_fields
            ),
            "missing_required_fields": list(
                self.missing_required_fields
            ),
            "flags": [
                flag.value
                for flag in self.flags
            ],
            "latency_seconds": self.latency_seconds,
            "latency_ms": self.latency_ms,
            "is_complete": self.is_complete,
            "is_stale": self.is_stale,
            "is_sequence_valid":
                self.is_sequence_valid,
            "is_usable": self.is_usable,
            "max_age_seconds":
                self.max_age_seconds,
        }


__all__ = [
    "DataQualityStatus",
    "DataQualityFlag",
    "DataQuality",
]
        return {
            "source": self.source,
            "observed_at": self.observed_at.isoformat(),
            "received_at": self.received_at.isoformat(),
            "status": self.status.value,
            "sequence": self.sequence,
            "required_fields": list(self.required_fields),
            "present_fields": list(self.present_fields),
            "missing_required_fields": list(
                self.missing_required_fields
            ),
            "flags": [
                flag.value
                for flag in self.flags
            ],
            "latency_seconds": self.latency_seconds,
            "latency_ms": self.latency_ms,
            "is_complete": self.is_complete,
            "is_stale": self.is_stale,
            "is_sequence_valid": self.is_sequence_valid,
            "is_usable": self.is_usable,
            "max_age_seconds": self.max_age_seconds,
        }


__all__ = [
    "DataQualityStatus",
    "DataQualityFlag",
    "DataQuality",
]