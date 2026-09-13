"""
ROBOMLM_PLUS
Evidence Cortex — MDIL

MDIL — Market Data Integrity & Lineage Engine

Layer:
    L001/L002 boundary feeding validated evidence into the
    downstream Evidence Cortex.

Purpose
-------
MDIL validates whether market observations / derived evidence
are structurally admissible for downstream intelligence.

MDIL does NOT:
    - create a trading signal
    - create BUY/SELL decisions
    - manufacture missing values
    - assign arbitrary confidence scores
    - treat UNKNOWN as negative evidence
    - silently repair contradictory observations
    - overwrite source provenance
    - mix units or instruments
    - accept invalid timestamps

MDIL DOES:
    - validate identity
    - validate numeric integrity
    - validate units
    - validate timestamps
    - validate source/provenance
    - detect duplicate observations
    - detect internal conflicts
    - preserve lineage
    - calculate freshness when a reference time is supplied
    - produce deterministic integrity state

Integrity chain
---------------

    Observation
        ↓
    Identity validation
        ↓
    Value validation
        ↓
    Unit validation
        ↓
    Timestamp validation
        ↓
    Provenance validation
        ↓
    Duplicate/conflict detection
        ↓
    Freshness determination
        ↓
    Integrity Result
        ↓
    Evidence Cortex

Important:
    Freshness is an observation property.

    It is NOT converted into a fake confidence score.

Unknown != Invalid
------------------
Missing optional information remains UNKNOWN.

Example:
    missing source timestamp
        -> PARTIAL / UNKNOWN

    negative depth volume
        -> INVALID

    NaN price
        -> INVALID

    crossed book observation
        -> INVALID when both quotes are present and contradictory

    duplicate identical observation
        -> VALID with duplicate_count > 0

    duplicate conflicting observation
        -> INVALID
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Iterable, Mapping, Optional, Sequence

from .evidence_engine_base import (
    CalculationStep,
    Evidence,
    EvidenceEngineBase,
    EvidenceStatus,
)


class MDILInputError(ValueError):
    """Raised when MDIL input violates the integrity contract."""


class IntegrityState(str, Enum):
    """
    Deterministic integrity classification.
    """

    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class DuplicateState(str, Enum):
    """
    Duplicate observation classification.
    """

    NONE = "NONE"
    IDENTICAL = "IDENTICAL"
    CONFLICTING = "CONFLICTING"


@dataclass(frozen=True)
class MDILObservation:
    """
    Canonical market observation.

    identity
    --------
    instrument_id:
        Exact instrument identity.

    market_id:
        Market/asset-class identity.

    venue_id:
        Venue/source venue identity.

    observation_type:
        e.g. PRICE, BID, ASK, TRADE_VOLUME, OI, DEPTH.

    value
        Numeric observation.

    unit
        Explicit unit of measurement.

    timestamp
        Observation/capture timestamp.

    source
        Data source.

    source_type
        LIVE, HISTORICAL, DERIVED, SIMULATION, etc.

    sequence_id
        Optional source sequence/event identifier.

    metadata
        Additional provenance fields.
    """

    instrument_id: str
    market_id: str
    venue_id: str

    observation_type: str

    value: Optional[float]
    unit: str

    timestamp: Optional[datetime]

    source: Optional[str]
    source_type: Optional[str]

    sequence_id: Optional[str] = None

    metadata: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True)
class MDILResult:
    """
    Complete MDIL integrity result.
    """

    status: EvidenceStatus
    integrity_state: IntegrityState

    observation_id: str

    instrument_id: Optional[str]
    market_id: Optional[str]
    venue_id: Optional[str]

    observation_type: Optional[str]
    value: Optional[float]
    unit: Optional[str]

    timestamp: Optional[datetime]
    source: Optional[str]
    source_type: Optional[str]

    freshness_age_seconds: Optional[float]
    freshness_state: str

    duplicate_state: DuplicateState
    duplicate_count: int

    identity_valid: bool
    value_valid: bool
    unit_valid: bool
    timestamp_valid: bool
    provenance_valid: bool

    content_hash: Optional[str]

    lineage: tuple[str, ...]

    calculation: tuple[CalculationStep, ...]

    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    reason: Optional[str]

    @property
    def is_valid(self) -> bool:
        return self.status == EvidenceStatus.VALID

    @property
    def is_partial(self) -> bool:
        return self.status == EvidenceStatus.PARTIAL


class MDILEngine(EvidenceEngineBase):
    """
    Market Data Integrity & Lineage Engine.

    MDIL is intentionally deterministic.

    No probabilistic confidence is produced here.
    """

    ENGINE_NAME = "MDIL"

    # Integrity / provenance boundary.
    LAYER = "L001-L002"

    METRIC = "market_data_integrity"

    # ---------------------------------------------------------------
    # CONSTRUCTION
    # ---------------------------------------------------------------

    def __init__(
        self,
        *,
        allowed_source_types: Optional[Iterable[str]] = None,
        freshness_limit: Optional[timedelta] = None,
    ) -> None:
        super().__init__()

        if freshness_limit is not None:
            if freshness_limit.total_seconds() < 0:
                raise MDILInputError(
                    "freshness_limit cannot be negative."
                )

        self.allowed_source_types = (
            frozenset(
                str(value).strip().upper()
                for value in allowed_source_types
                if str(value).strip()
            )
            if allowed_source_types is not None
            else None
        )

        self.freshness_limit = freshness_limit

    # ---------------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------------

    def process(
        self,
        data: Any,
        *,
        reference_time: Optional[datetime] = None,
        prior_observations: Optional[
            Iterable[Any]
        ] = None,
    ) -> MDILResult:
        """
        Validate one observation.

        prior_observations is optional and is used only for
        deterministic duplicate/conflict detection.
        """

        observation = self._normalize_observation(data)

        prior = [
            self._normalize_observation(item)
            for item in (
                prior_observations
                if prior_observations is not None
                else ()
            )
        ]

        return self.calculate(
            observation,
            reference_time=reference_time,
            prior_observations=prior,
        )

    def calculate(
        self,
        observation: MDILObservation,
        *,
        reference_time: Optional[datetime] = None,
        prior_observations: Optional[
            Sequence[MDILObservation]
        ] = None,
    ) -> MDILResult:
        """
        Perform complete integrity calculation.
        """

        if not isinstance(
            observation,
            MDILObservation,
        ):
            raise MDILInputError(
                "calculate() requires MDILObservation."
            )

        errors: list[str] = []
        warnings: list[str] = []
        calculation: list[CalculationStep] = []

        # -----------------------------------------------------------
        # 1. IDENTITY
        # -----------------------------------------------------------

        identity_valid = True

        identity_fields = {
            "instrument_id": observation.instrument_id,
            "market_id": observation.market_id,
            "venue_id": observation.venue_id,
            "observation_type": observation.observation_type,
        }

        for field_name, value in identity_fields.items():
            if not self._valid_identifier(value):
                identity_valid = False
                errors.append(
                    f"Missing or invalid {field_name}."
                )

        # -----------------------------------------------------------
        # 2. UNIT
        # -----------------------------------------------------------

        unit_valid = self._valid_unit(
            observation.unit
        )

        if not unit_valid:
            errors.append(
                "Observation unit is missing or invalid."
            )

        # -----------------------------------------------------------
        # 3. VALUE
        # -----------------------------------------------------------

        value_valid = self._valid_value(
            observation.value
        )

        if not value_valid:
            errors.append(
                "Observation value is not finite."
            )

        # -----------------------------------------------------------
        # 4. SEMANTIC VALUE VALIDATION
        # -----------------------------------------------------------

        semantic_errors = self._semantic_value_errors(
            observation
        )

        if semantic_errors:
            value_valid = False
            errors.extend(semantic_errors)

        # -----------------------------------------------------------
        # 5. TIMESTAMP
        # -----------------------------------------------------------

        timestamp_valid = self._valid_timestamp(
            observation.timestamp
        )

        if not timestamp_valid:
            warnings.append(
                "Observation timestamp is unavailable or invalid."
            )

        # -----------------------------------------------------------
        # 6. PROVENANCE
        # -----------------------------------------------------------

        provenance_valid = self._valid_provenance(
            observation
        )

        if not provenance_valid:
            errors.append(
                "Required provenance information is incomplete."
            )

        # -----------------------------------------------------------
        # 7. FRESHNESS
        # -----------------------------------------------------------

        (
            freshness_age_seconds,
            freshness_state,
        ) = self._calculate_freshness(
            observation.timestamp,
            reference_time,
        )

        if freshness_state == "UNKNOWN":
            warnings.append(
                "Freshness cannot be determined because "
                "reference time or observation timestamp is missing."
            )

        elif freshness_state == "STALE":
            warnings.append(
                "Observation exceeds configured freshness limit."
            )

        calculation.append(
            CalculationStep(
                name="freshness_age",
                formula="reference_time - observation_timestamp",
                inputs={
                    "reference_time": reference_time,
                    "observation_timestamp": (
                        observation.timestamp
                    ),
                },
                output=freshness_age_seconds,
            )
        )

        # -----------------------------------------------------------
        # 8. DUPLICATE / CONFLICT DETECTION
        # -----------------------------------------------------------

        (
            duplicate_state,
            duplicate_count,
            duplicate_errors,
        ) = self._detect_duplicates(
            observation,
            prior_observations or (),
        )

        if duplicate_errors:
            errors.extend(duplicate_errors)

        # -----------------------------------------------------------
        # 9. CONTENT HASH
        # -----------------------------------------------------------

        content_hash = self._content_hash(
            observation
        )

        calculation.append(
            CalculationStep(
                name="content_hash",
                formula="SHA-256(canonical_observation)",
                inputs={
                    "instrument_id": observation.instrument_id,
                    "market_id": observation.market_id,
                    "venue_id": observation.venue_id,
                    "observation_type": (
                        observation.observation_type
                    ),
                    "value": observation.value,
                    "unit": observation.unit,
                    "timestamp": self._timestamp_string(
                        observation.timestamp
                    ),
                },
                output=content_hash,
            )
        )

        # -----------------------------------------------------------
        # 10. LINEAGE
        # -----------------------------------------------------------

        lineage = self._build_lineage(
            observation,
            content_hash,
        )

        # -----------------------------------------------------------
        # 11. FINAL STATE
        # -----------------------------------------------------------

        if errors:
            status = EvidenceStatus.INVALID
            integrity_state = IntegrityState.INVALID

            reason = (
                "One or more mandatory integrity checks failed."
            )

        elif not identity_valid:
            status = EvidenceStatus.INVALID
            integrity_state = IntegrityState.INVALID
            reason = "Observation identity is invalid."

        elif not value_valid:
            status = EvidenceStatus.INVALID
            integrity_state = IntegrityState.INVALID
            reason = "Observation value is invalid."

        elif not unit_valid:
            status = EvidenceStatus.INVALID
            integrity_state = IntegrityState.INVALID
            reason = "Observation unit is invalid."

        elif not provenance_valid:
            status = EvidenceStatus.PARTIAL
            integrity_state = IntegrityState.PARTIAL
            reason = (
                "Observation is usable but provenance is incomplete."
            )

        elif (
            timestamp_valid is False
            or freshness_state == "UNKNOWN"
        ):
            status = EvidenceStatus.PARTIAL
            integrity_state = IntegrityState.PARTIAL
            reason = (
                "Observation is structurally valid but "
                "temporal integrity is incomplete."
            )

        else:
            status = EvidenceStatus.VALID
            integrity_state = IntegrityState.VALID
            reason = None

        # Freshness does not invalidate the observation by itself.
        # It remains a separate state.
        if freshness_state == "STALE":
            if status == EvidenceStatus.VALID:
                warnings.append(
                    "Observation is valid but stale."
                )

        return MDILResult(
            status=status,
            integrity_state=integrity_state,
            observation_id=self._observation_id(
                observation
            ),
            instrument_id=observation.instrument_id,
            market_id=observation.market_id,
            venue_id=observation.venue_id,
            observation_type=(
                observation.observation_type
            ),
            value=observation.value,
            unit=observation.unit,
            timestamp=observation.timestamp,
            source=observation.source,
            source_type=observation.source_type,
            freshness_age_seconds=freshness_age_seconds,
            freshness_state=freshness_state,
            duplicate_state=duplicate_state,
            duplicate_count=duplicate_count,
            identity_valid=identity_valid,
            value_valid=value_valid,
            unit_valid=unit_valid,
            timestamp_valid=timestamp_valid,
            provenance_valid=provenance_valid,
            content_hash=content_hash,
            lineage=lineage,
            calculation=tuple(calculation),
            errors=tuple(errors),
            warnings=tuple(warnings),
            reason=reason,
        )

    # ---------------------------------------------------------------
    # EVIDENCE
    # ---------------------------------------------------------------

    def build_evidence(
        self,
        result: MDILResult,
        *,
        source: str = "MDIL",
        source_type: str = "validation",
    ) -> list[Evidence]:
        """
        Convert MDIL integrity outputs into auditable evidence.
        """

        evidence: list[Evidence] = []

        evidence.append(
            self.make_evidence(
                metric="mdil.integrity_state",
                value=result.integrity_state.value,
                unit="categorical",
                status=result.status,
                source=source,
                source_type=source_type,
                inputs={
                    "observation_id": result.observation_id,
                    "instrument_id": result.instrument_id,
                    "market_id": result.market_id,
                    "venue_id": result.venue_id,
                    "observation_type": (
                        result.observation_type
                    ),
                },
                calculation=list(result.calculation),
                lineage=list(result.lineage),
                reason=result.reason,
            )
        )

        evidence.append(
            self.make_evidence(
                metric="mdil.freshness_state",
                value=result.freshness_state,
                unit="categorical",
                status=result.status,
                source=source,
                source_type=source_type,
                inputs={
                    "freshness_age_seconds": (
                        result.freshness_age_seconds
                    ),
                },
                calculation=list(result.calculation),
                lineage=list(result.lineage),
                reason=result.reason,
            )
        )

        if result.freshness_age_seconds is not None:
            evidence.append(
                self.make_evidence(
                    metric="mdil.freshness_age_seconds",
                    value=result.freshness_age_seconds,
                    unit="seconds",
                    status=result.status,
                    source=source,
                    source_type=source_type,
                    inputs={
                        "timestamp": result.timestamp,
                    },
                    calculation=list(result.calculation),
                    lineage=list(result.lineage),
                    reason=result.reason,
                )
            )

        evidence.append(
            self.make_evidence(
                metric="mdil.duplicate_state",
                value=result.duplicate_state.value,
                unit="categorical",
                status=result.status,
                source=source,
                source_type=source_type,
                inputs={
                    "duplicate_count": result.duplicate_count,
                },
                calculation=list(result.calculation),
                lineage=list(result.lineage),
                reason=result.reason,
            )
        )

        evidence.append(
            self.make_evidence(
                metric="mdil.content_hash",
                value=result.content_hash,
                unit="sha256",
                status=result.status,
                source=source,
                source_type=source_type,
                inputs={
                    "observation_id": result.observation_id,
                },
                calculation=list(result.calculation),
                lineage=list(result.lineage),
                reason=result.reason,
            )
        )

        return evidence

    # ---------------------------------------------------------------
    # NORMALIZATION
    # ---------------------------------------------------------------

    def _normalize_observation(
        self,
        data: Any,
    ) -> MDILObservation:
        if isinstance(data, MDILObservation):
            return self._validate_observation(data)

        if isinstance(data, Mapping):
            return self._validate_observation(
                MDILObservation(
                    instrument_id=str(
                        data.get(
                            "instrument_id",
                            data.get("symbol", ""),
                        )
                    ).strip(),

                    market_id=str(
                        data.get(
                            "market_id",
                            data.get("market", ""),
                        )
                    ).strip(),

                    venue_id=str(
                        data.get(
                            "venue_id",
                            data.get("venue", ""),
                        )
                    ).strip(),

                    observation_type=str(
                        data.get(
                            "observation_type",
                            data.get("type", ""),
                        )
                    ).strip().upper(),

                    value=(
                        self._optional_float(
                            data.get("value")
                        )
                    ),

                    unit=str(
                        data.get("unit", "")
                    ).strip(),

                    timestamp=data.get(
                        "timestamp",
                        data.get("observed_at"),
                    ),

                    source=self._optional_string(
                        data.get("source")
                    ),

                    source_type=(
                        self._optional_upper_string(
                            data.get("source_type")
                        )
                    ),

                    sequence_id=(
                        self._optional_string(
                            data.get("sequence_id")
                        )
                    ),

                    metadata=data.get("metadata"),
                )
            )

        raise MDILInputError(
            f"Unsupported MDIL input type: "
            f"{type(data).__name__}"
        )

    def _validate_observation(
        self,
        observation: MDILObservation,
    ) -> MDILObservation:
        if not isinstance(
            observation.instrument_id,
            str,
        ):
            raise MDILInputError(
                "instrument_id must be a string."
            )

        if not isinstance(
            observation.market_id,
            str,
        ):
            raise MDILInputError(
                "market_id must be a string."
            )

        if not isinstance(
            observation.venue_id,
            str,
        ):
            raise MDILInputError(
                "venue_id must be a string."
            )

        if observation.value is not None:
            if not isinstance(
                observation.value,
                (int, float),
            ):
                raise MDILInputError(
                    "Observation value must be numeric."
                )

            if not math.isfinite(
                float(observation.value)
            ):
                raise MDILInputError(
                    "Observation value must be finite."
                )

        if observation.timestamp is not None:
            if not isinstance(
                observation.timestamp,
                datetime,
            ):
                raise MDILInputError(
                    "timestamp must be datetime."
                )

        return observation

    # ---------------------------------------------------------------
    # VALUE VALIDATION
    # ---------------------------------------------------------------

    @staticmethod
    def _valid_value(
        value: Optional[float],
    ) -> bool:
        if value is None:
            return True

        return (
            isinstance(value, (int, float))
            and math.isfinite(float(value))
        )

    @staticmethod
    def _semantic_value_errors(
        observation: MDILObservation,
    ) -> list[str]:
        """
        Apply only semantic constraints that are intrinsic to the
        observation type.

        Directional variables are allowed to be negative.

        Quantities that cannot physically be negative are rejected.
        """

        if observation.value is None:
            return []

        value = float(observation.value)

        observation_type = (
            observation.observation_type.upper()
        )

        nonnegative_types = {
            "VOLUME",
            "TRADE_VOLUME",
            "BUY_VOLUME",
            "SELL_VOLUME",
            "OI",
            "OPEN_INTEREST",
            "BID_DEPTH",
            "ASK_DEPTH",
            "DEPTH",
            "QUANTITY",
            "QTY",
            "LIQUIDITY",
            "SPREAD",
        }

        if (
            observation_type in nonnegative_types
            and value < 0
        ):
            return [
                (
                    f"{observation.observation_type} "
                    "cannot be negative."
                )
            ]

        price_types = {
            "PRICE",
            "LAST_PRICE",
            "BID",
            "ASK",
            "BEST_BID",
            "BEST_ASK",
            "MARK_PRICE",
        }

        if (
            observation_type in price_types
            and value <= 0
        ):
            return [
                (
                    f"{observation.observation_type} "
                    "must be strictly positive."
                )
            ]

        return []

    # ---------------------------------------------------------------
    # IDENTITY / UNIT / PROVENANCE
    # ---------------------------------------------------------------

    @staticmethod
    def _valid_identifier(
        value: Any,
    ) -> bool:
        return (
            isinstance(value, str)
            and bool(value.strip())
        )

    @staticmethod
    def _valid_unit(
        value: Any,
    ) -> bool:
        return (
            isinstance(value, str)
            and bool(value.strip())
        )

    def _valid_provenance(
        self,
        observation: MDILObservation,
    ) -> bool:
        if (
            observation.source is None
            or not observation.source.strip()
        ):
            return False

        if (
            observation.source_type is None
            or not observation.source_type.strip()
        ):
            return False

        if self.allowed_source_types is not None:
            if (
                observation.source_type.upper()
                not in self.allowed_source_types
            ):
                return False

        return True

    @staticmethod
    def _valid_timestamp(
        timestamp: Optional[datetime],
    ) -> bool:
        if timestamp is None:
            return False

        return isinstance(
            timestamp,
            datetime,
        )

    # ---------------------------------------------------------------
    # FRESHNESS
    # ---------------------------------------------------------------

    def _calculate_freshness(
        self,
        timestamp: Optional[datetime],
        reference_time: Optional[datetime],
    ) -> tuple[Optional[float], str]:
        """
        Calculate observation age.

        Freshness is unknown if either timestamp is absent.

        Future timestamps are rejected as temporally inconsistent
        only when the difference is negative beyond exact equality.
        """

        if (
            timestamp is None
            or reference_time is None
        ):
            return None, "UNKNOWN"

        if not isinstance(
            timestamp,
            datetime,
        ):
            return None, "UNKNOWN"

        if not isinstance(
            reference_time,
            datetime,
        ):
            return None, "UNKNOWN"

        ts = self._align_datetime(
            timestamp
        )

        ref = self._align_datetime(
            reference_time
        )

        age = (
            ref - ts
        ).total_seconds()

        if age < 0:
            return age, "FUTURE"

        if (
            self.freshness_limit is None
        ):
            return age, "KNOWN"

        if age <= self.freshness_limit.total_seconds():
            return age, "FRESH"

        return age, "STALE"

    @staticmethod
    def _align_datetime(
        value: datetime,
    ) -> datetime:
        """
        Normalize naive timestamps as UTC without inventing a
        different instant.

        Timezone-aware timestamps are converted to UTC.
        """

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    # ---------------------------------------------------------------
    # DUPLICATE / CONFLICT
    # ---------------------------------------------------------------

    def _detect_duplicates(
        self,
        observation: MDILObservation,
        prior_observations: Sequence[
            MDILObservation
        ],
    ) -> tuple[
        DuplicateState,
        int,
        list[str],
    ]:
        identical = 0
        conflicting = 0

        for prior in prior_observations:
            if not self._same_identity(
                observation,
                prior,
            ):
                continue

            if self._same_observation(
                observation,
                prior,
            ):
                identical += 1
            else:
                conflicting += 1

        if conflicting > 0:
            return (
                DuplicateState.CONFLICTING,
                identical + conflicting,
                [
                    (
                        "Conflicting duplicate observation detected "
                        "for the same observation identity."
                    )
                ],
            )

        if identical > 0:
            return (
                DuplicateState.IDENTICAL,
                identical,
                [],
            )

        return (
            DuplicateState.NONE,
            0,
            [],
        )

    @staticmethod
    def _same_identity(
        left: MDILObservation,
        right: MDILObservation,
    ) -> bool:
        return (
            left.instrument_id
            == right.instrument_id
            and left.market_id
            == right.market_id
            and left.venue_id
            == right.venue_id
            and left.observation_type
            == right.observation_type
            and left.unit
            == right.unit
            and left.timestamp
            == right.timestamp
            and left.sequence_id
            == right.sequence_id
        )

    @staticmethod
    def _same_observation(
        left: MDILObservation,
        right: MDILObservation,
    ) -> bool:
        return (
            MDILEngine._same_identity(
                left,
                right,
            )
            and left.value == right.value
            and left.source == right.source
            and left.source_type == right.source_type
        )

    # ---------------------------------------------------------------
    # HASH / LINEAGE
    # ---------------------------------------------------------------

    @classmethod
    def _canonical_observation(
        cls,
        observation: MDILObservation,
    ) -> str:
        payload = {
            "instrument_id": observation.instrument_id,
            "market_id": observation.market_id,
            "venue_id": observation.venue_id,
            "observation_type": (
                observation.observation_type
            ),
            "value": observation.value,
            "unit": observation.unit,
            "timestamp": cls._timestamp_string(
                observation.timestamp
            ),
            "source": observation.source,
            "source_type": observation.source_type,
            "sequence_id": observation.sequence_id,
        }

        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    @classmethod
    def _content_hash(
        cls,
        observation: MDILObservation,
    ) -> str:
        canonical = cls._canonical_observation(
            observation
        )

        return hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()

    @classmethod
    def _observation_id(
        cls,
        observation: MDILObservation,
    ) -> str:
        return (
            "MDIL-"
            + cls._content_hash(observation)[:24]
        )

    @classmethod
    def _build_lineage(
        cls,
        observation: MDILObservation,
        content_hash: str,
    ) -> tuple[str, ...]:
        lineage = [
            f"source:{observation.source}",
            f"source_type:{observation.source_type}",
            f"market:{observation.market_id}",
            f"venue:{observation.venue_id}",
            f"instrument:{observation.instrument_id}",
            (
                "observation_type:"
                f"{observation.observation_type}"
            ),
            f"unit:{observation.unit}",
            f"hash:sha256:{content_hash}",
        ]

        if observation.sequence_id:
            lineage.append(
                f"sequence:{observation.sequence_id}"
            )

        if observation.timestamp is not None:
            lineage.append(
                "timestamp:"
                + cls._timestamp_string(
                    observation.timestamp
                )
            )

        return tuple(lineage)

    @staticmethod
    def _timestamp_string(
        timestamp: Optional[datetime],
    ) -> Optional[str]:
        if timestamp is None:
            return None

        return timestamp.isoformat()

    # ---------------------------------------------------------------
    # SMALL HELPERS
    # ---------------------------------------------------------------

    @staticmethod
    def _optional_float(
        value: Any,
    ) -> Optional[float]:
        if value is None:
            return None

        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise MDILInputError(
                "Numeric value cannot be converted to float."
            ) from exc

        if not math.isfinite(result):
            raise MDILInputError(
                "Numeric value must be finite."
            )

        return result

    @staticmethod
    def _optional_string(
        value: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()

        return text if text else None

    @staticmethod
    def _optional_upper_string(
        value: Any,
    ) -> Optional[str]:
        value = MDILEngine._optional_string(
            value
        )

        return (
            value.upper()
            if value is not None
            else None
        )


# ----------------------------------------------------------------------
# COMPATIBILITY ALIASES
# ----------------------------------------------------------------------

MarketDataIntegrityEngine = MDILEngine
MarketDataIntegrityLineageEngine = MDILEngine
DataIntegrityEngine = MDILEngine
MarketDataIntegrityLayer = MDILEngine


__all__ = [
    "MDILInputError",
    "IntegrityState",
    "DuplicateState",
    "MDILObservation",
    "MDILResult",
    "MDILEngine",
    "MarketDataIntegrityEngine",
    "MarketDataIntegrityLineageEngine",
    "DataIntegrityEngine",
    "MarketDataIntegrityLayer",
]