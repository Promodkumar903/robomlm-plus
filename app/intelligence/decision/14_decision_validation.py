"""
ROBOMLM_PLUS
D14 — DECISION VALIDATION ENGINE
Version: D14-2.0

Role:
D13 Decision
    ↓
D14 Decision Validation
    ↓
D15 Decision Learning
    ↓
D16 Decision Intelligence

D14 = VALIDATION ONLY

D14 MUST NOT:
- create decisions
- modify D13
- learn
- execute
- change risk
- change position size
- generate BUY/SELL authority
- generate universal probability
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional, Sequence
import hashlib
import json


# ============================================================================
# IDENTITY
# ============================================================================

D14_ENGINE_NAME = "D14_DecisionValidation"
D14_ENGINE_VERSION = "D14-2.0"

D14_AUTHORITY = "VALIDATION"

D14_DECISION_AUTHORITY = False
D14_EXECUTION_AUTHORITY = False
D14_LEARNING_AUTHORITY = False
D14_PROBABILITY_AUTHORITY = False

D14_D13_SOURCE = "D13"
D14_D15_TARGET = "D15"
D14_D16_TARGET = "D16"

D14_FUTURE_DATA_REQUIRED = True
D14_FUTURE_DATA_ALLOWED_BEFORE_DECISION = False


# ============================================================================
# ENUMS
# ============================================================================

class D14Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"
    UNDETERMINED = "UNDETERMINED"


class ValidationResult(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    UNDETERMINED = "UNDETERMINED"


class ValidationComponentResult(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    UNDETERMINED = "UNDETERMINED"


class ValidationDisposition(str, Enum):
    ACCEPTED = "ACCEPTED"
    PARTIAL = "PARTIAL"
    REJECTED = "REJECTED"
    BLOCKED = "BLOCKED"


class D14ConflictType(str, Enum):
    NONE = "NONE"
    IDENTITY_CONFLICT = "IDENTITY_CONFLICT"
    TIMESTAMP_CONFLICT = "TIMESTAMP_CONFLICT"
    PROVENANCE_CONFLICT = "PROVENANCE_CONFLICT"
    LEAKAGE_CONFLICT = "LEAKAGE_CONFLICT"
    OUTCOME_CONFLICT = "OUTCOME_CONFLICT"
    SCENARIO_CONFLICT = "SCENARIO_CONFLICT"


class D14ValidationPhase(str, Enum):
    INPUT = "INPUT"
    TEMPORAL = "TEMPORAL"
    IDENTITY = "IDENTITY"
    PROVENANCE = "PROVENANCE"
    OUTCOME = "OUTCOME"
    FINAL = "FINAL"


# ============================================================================
# HELPERS
# ============================================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse datetime strictly.

    Invalid input returns None.
    No fabricated timestamp is ever created.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value

    elif isinstance(value, str):
        text = value.strip()

        if not text:
            return None

        try:
            dt = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    else:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def clean_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def normalize_id(value: Any) -> str:
    return clean_text(value)


def freeze_mapping(
    value: Mapping[str, Any],
) -> Mapping[str, Any]:

    return MappingProxyType(
        deepcopy(dict(value))
    )


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


# ============================================================================
# D13 IMMUTABLE DECISION SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class D14DecisionSnapshot:
    """
    Immutable snapshot of the D13 decision consumed by D14.
    """

    decision_id: str
    market_id: str
    decision_timestamp: datetime

    action: str
    expected_direction: str

    selected_scenario_id: str = ""
    selected_scenario_type: str = ""
    horizon: str = ""

    entry_level: Optional[float] = None
    stop_loss_level: Optional[float] = None
    take_profit_level: Optional[float] = None

    source_engine: str = "D13_Decision"
    source_engine_version: str = ""

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    # Compatibility aliases.
    @property
    def scenario_type(self) -> str:
        return self.selected_scenario_type

    @property
    def source_version(self) -> str:
        return self.source_engine_version

    @property
    def snapshot_hash(self) -> str:
        return stable_hash(
            {
                "decision_id": self.decision_id,
                "market_id": self.market_id,
                "decision_timestamp": (
                    self.decision_timestamp.isoformat()
                ),
                "action": self.action,
                "expected_direction": (
                    self.expected_direction
                ),
                "selected_scenario_id": (
                    self.selected_scenario_id
                ),
                "selected_scenario_type": (
                    self.selected_scenario_type
                ),
                "horizon": self.horizon,
                "entry_level": self.entry_level,
                "stop_loss_level": (
                    self.stop_loss_level
                ),
                "take_profit_level": (
                    self.take_profit_level
                ),
                "source_engine": self.source_engine,
                "source_engine_version": (
                    self.source_engine_version
                ),
                "metadata": dict(self.metadata),
            }
        )


# ============================================================================
# D14 OUTCOME OBSERVATION
# ============================================================================

@dataclass(frozen=True)
class D14OutcomeObservation:
    """
    Post-decision observation.

    Observation timestamp MUST be strictly after
    the original D13 decision timestamp.
    """

    observation_id: str
    market_id: str
    observation_timestamp: datetime

    observed_direction: str = ""
    observed_scenario_type: str = ""

    price_at_observation: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None

    invalidation_triggered: bool = False
    pnl_result: Optional[str] = None

    source: str = ""
    source_version: str = ""

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    # Compatibility aliases.
    @property
    def observed_scenario(self) -> str:
        return self.observed_scenario_type

    @property
    def price(self) -> Optional[float]:
        return self.price_at_observation

    @property
    def high(self) -> Optional[float]:
        return self.high_price

    @property
    def low(self) -> Optional[float]:
        return self.low_price

    @property
    def close(self) -> Optional[float]:
        return self.close_price


# ============================================================================
# D14 VALIDATION EVIDENCE
# ============================================================================

@dataclass(frozen=True)
class D14ValidationEvidence:
    """
    Final auditable D14 validation result.
    """

    validation_id: str
    decision_id: str
    market_id: str

    decision_timestamp: datetime
    validation_timestamp: datetime

    status: D14Status
    overall_result: ValidationResult

    direction_result: ValidationComponentResult
    scenario_result: ValidationComponentResult
    horizon_result: ValidationComponentResult
    invalidation_result: ValidationComponentResult
    pnl_result: ValidationComponentResult

    expected_direction: str
    observed_direction: str

    action: str
    selected_scenario_id: str
    selected_scenario_type: str
    horizon: str

    source_engine: str
    source_engine_version: str

    future_leakage: bool
    identity_mismatch: bool
    temporal_valid: bool
    provenance_valid: bool

    validation_reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    provenance: Mapping[str, Any] = field(
        default_factory=dict
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    validated_by_D14: bool = True
    D14_modified: bool = False
    D13_modified: bool = False
    learning_performed: bool = False
    execution_performed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            freeze_mapping(self.provenance),
        )

        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    # Compatibility aliases.
    @property
    def scenario_type(self) -> str:
        return self.selected_scenario_type

    @property
    def source_version(self) -> str:
        return self.source_engine_version

    @property
    def reasons(self) -> tuple[str, ...]:
        return self.validation_reasons

    def to_d15_payload(
        self,
    ) -> Mapping[str, Any]:

        return MappingProxyType(
            deepcopy(
                {
                    "validation_id": self.validation_id,
                    "decision_id": self.decision_id,
                    "market_id": self.market_id,

                    "decision_timestamp": (
                        self.decision_timestamp.isoformat()
                    ),

                    "validation_timestamp": (
                        self.validation_timestamp.isoformat()
                    ),

                    "result": (
                        self.overall_result.value
                    ),

                    "status": self.status.value,

                    "direction_result": (
                        self.direction_result.value
                    ),

                    "scenario_result": (
                        self.scenario_result.value
                    ),

                    "horizon_result": (
                        self.horizon_result.value
                    ),

                    "invalidation_result": (
                        self.invalidation_result.value
                    ),

                    "pnl_result": (
                        self.pnl_result.value
                    ),

                    "action": self.action,

                    "expected_direction": (
                        self.expected_direction
                    ),

                    "observed_direction": (
                        self.observed_direction
                    ),

                    "selected_scenario_id": (
                        self.selected_scenario_id
                    ),

                    "selected_scenario_type": (
                        self.selected_scenario_type
                    ),

                    "horizon": self.horizon,

                    "evidence_ids": list(
                        self.evidence_ids
                    ),

                    "validation_reasons": list(
                        self.validation_reasons
                    ),

                    "source": "D14",

                    "engine_version": (
                        self.source_engine_version
                    ),

                    "provenance": dict(
                        self.provenance
                    ),

                    "metadata": dict(
                        self.metadata
                    ),

                    "validated_by_D14": (
                        self.validated_by_D14
                    ),

                    "D14_modified": (
                        self.D14_modified
                    ),

                    "D13_modified": (
                        self.D13_modified
                    ),

                    "future_data_allowed": False,

                    "future_leakage": (
                        self.future_leakage
                    ),

                    "learning_performed": False,

                    "execution_performed": False,
                }
            )
        )


# ============================================================================
# D14 CONTRACT
# ============================================================================

@dataclass(frozen=True)
class D14ValidationContract:
    """
    Formal D14 authority boundary.
    """

    engine_name: str
    engine_version: str
    authority: str

    status: D14Status

    validation: Optional[
        D14ValidationEvidence
    ]

    d13_source: str
    d15_target: str

    decision_authority: bool
    execution_authority: bool
    learning_authority: bool
    probability_authority: bool

    future_data_required: bool
    future_data_allowed_before_decision: bool

    created_at: datetime

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    # Compatibility aliases.
    @property
    def can_create_decision(self) -> bool:
        return self.decision_authority

    @property
    def can_modify_d13(self) -> bool:
        return False

    @property
    def can_learn(self) -> bool:
        return self.learning_authority

    @property
    def can_execute(self) -> bool:
        return self.execution_authority

    @property
    def can_generate_probability(self) -> bool:
        return self.probability_authority

    @property
    def source_engine(self) -> str:
        return self.d13_source

    @property
    def target_learning_engine(self) -> str:
        return self.d15_target

    @property
    def target_intelligence_engine(self) -> str:
        return D14_D16_TARGET


# ============================================================================
# DECISION INPUT BUILDER
# ============================================================================

def build_d14_decision_snapshot(
    *,
    decision_id: Any,
    market_id: Any,
    decision_timestamp: Any,
    action: Any,
    expected_direction: Any,
    selected_scenario_id: Any = "",
    selected_scenario_type: Any = "",
    horizon: Any = "",
    entry_level: Optional[float] = None,
    stop_loss_level: Optional[float] = None,
    take_profit_level: Optional[float] = None,
    source_engine: Any = "D13_Decision",
    source_engine_version: Any = "",
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> D14DecisionSnapshot:

    dt = parse_datetime(
        decision_timestamp
    )

    if dt is None:
        raise ValueError(
            "D14 requires a valid D13 decision timestamp. "
            "Timestamp cannot be invented."
        )

    return D14DecisionSnapshot(
        decision_id=normalize_id(
            decision_id
        ),

        market_id=normalize_id(
            market_id
        ),

        decision_timestamp=dt,

        action=clean_text(
            action
        ).upper(),

        expected_direction=clean_text(
            expected_direction
        ).upper(),

        selected_scenario_id=normalize_id(
            selected_scenario_id
        ),

        selected_scenario_type=clean_text(
            selected_scenario_type
        ).upper(),

        horizon=clean_text(
            horizon
        ).upper(),

        entry_level=entry_level,
        stop_loss_level=stop_loss_level,
        take_profit_level=take_profit_level,

        source_engine=clean_text(
            source_engine
        ),

        source_engine_version=clean_text(
            source_engine_version
        ),

        metadata=metadata or {},
    )


# ============================================================================
# OUTCOME INPUT BUILDER
# ============================================================================

def build_d14_outcome_observation(
    *,
    observation_id: Any,
    market_id: Any,
    observation_timestamp: Any,
    observed_direction: Any = "",
    observed_scenario_type: Any = "",
    price_at_observation: Optional[float] = None,
    high_price: Optional[float] = None,
    low_price: Optional[float] = None,
    close_price: Optional[float] = None,
    invalidation_triggered: bool = False,
    pnl_result: Optional[str] = None,
    source: Any = "",
    source_version: Any = "",
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> D14OutcomeObservation:

    dt = parse_datetime(
        observation_timestamp
    )

    if dt is None:
        raise ValueError(
            "D14 requires a valid future observation timestamp. "
            "Timestamp cannot be invented."
        )

    return D14OutcomeObservation(
        observation_id=normalize_id(
            observation_id
        ),

        market_id=normalize_id(
            market_id
        ),

        observation_timestamp=dt,

        observed_direction=clean_text(
            observed_direction
        ).upper(),

        observed_scenario_type=clean_text(
            observed_scenario_type
        ).upper(),

        price_at_observation=(
            price_at_observation
        ),

        high_price=high_price,
        low_price=low_price,
        close_price=close_price,

        invalidation_triggered=bool(
            invalidation_triggered
        ),

        pnl_result=(
            clean_text(
                pnl_result
            ).upper()
            if pnl_result is not None
            else None
        ),

        source=clean_text(
            source
        ),

        source_version=clean_text(
            source_version
        ),

        metadata=metadata or {},
    )


# ============================================================================
# FUTURE LEAKAGE
# ============================================================================

FUTURE_LEAKAGE_MARKERS = (
    "future_leakage",
    "future_evidence",
    "future_data",
    "lookahead",
    "look_ahead",
    "leakage",
    "uses_future_information",
    "future_information_used",
)


def d14_detect_future_leakage(
    observation: D14OutcomeObservation,
) -> bool:

    metadata = dict(
        observation.metadata
    )

    for key in FUTURE_LEAKAGE_MARKERS:

        value = metadata.get(key)

        if value is True:
            return True

        if isinstance(value, str):

            if value.strip().lower() in {
                "true",
                "yes",
                "1",
                "leak",
                "leaked",
            }:
                return True

    return False


# ============================================================================
# TEMPORAL VALIDATION
# ============================================================================

def d14_validate_temporal_order(
    decision_timestamp: datetime,
    observation_timestamp: datetime,
) -> bool:

    return (
        observation_timestamp
        > decision_timestamp
    )


def d14_validate_observation_cutoff(
    decision: D14DecisionSnapshot,
    observation: D14OutcomeObservation,
) -> tuple[bool, tuple[str, ...]]:

    reasons: list[str] = []

    if not d14_validate_temporal_order(
        decision.decision_timestamp,
        observation.observation_timestamp,
    ):
        reasons.append(
            "OBSERVATION_NOT_STRICTLY_AFTER_DECISION"
        )

    if d14_detect_future_leakage(
        observation
    ):
        reasons.append(
            "FUTURE_LEAKAGE_MARKER_DETECTED"
        )

    return (
        len(reasons) == 0,
        tuple(reasons),
    )


# ============================================================================
# IDENTITY VALIDATION
# ============================================================================

def d14_validate_identity(
    decision: D14DecisionSnapshot,
    observation: D14OutcomeObservation,
) -> tuple[bool, tuple[str, ...]]:

    reasons: list[str] = []

    if not decision.decision_id:
        reasons.append(
            "MISSING_DECISION_ID"
        )

    if not observation.observation_id:
        reasons.append(
            "MISSING_OBSERVATION_ID"
        )

    if not decision.market_id:
        reasons.append(
            "MISSING_DECISION_MARKET_ID"
        )

    if not observation.market_id:
        reasons.append(
            "MISSING_OBSERVATION_MARKET_ID"
        )

    if decision.market_id != observation.market_id:
        reasons.append(
            "MARKET_ID_MISMATCH"
        )

    return (
        len(reasons) == 0,
        tuple(reasons),
    )


# ============================================================================
# PROVENANCE VALIDATION
# ============================================================================

def d14_validate_provenance(
    decision: D14DecisionSnapshot,
    observation: D14OutcomeObservation,
) -> tuple[bool, tuple[str, ...]]:

    reasons: list[str] = []

    if decision.source_engine:

        if not decision.source_engine.upper().startswith(
            "D13"
        ):
            reasons.append(
                "INVALID_D13_SOURCE_ENGINE"
            )

    if not observation.source:
        reasons.append(
            "MISSING_OBSERVATION_SOURCE"
        )

    if not observation.source_version:
        reasons.append(
            "MISSING_OBSERVATION_SOURCE_VERSION"
        )

    return (
        len(reasons) == 0,
        tuple(reasons),
    )


# ============================================================================
# COMPONENT VALIDATION
# ============================================================================

def d14_validate_direction(
    expected_direction: str,
    observed_direction: str,
) -> ValidationComponentResult:

    expected = clean_text(
        expected_direction
    ).upper()

    observed = clean_text(
        observed_direction
    ).upper()

    if not expected or not observed:
        return (
            ValidationComponentResult.UNDETERMINED
        )

    if expected == observed:
        return (
            ValidationComponentResult.CORRECT
        )

    return (
        ValidationComponentResult.INCORRECT
    )


def d14_validate_scenario(
    expected_scenario: str,
    observed_scenario: str,
) -> ValidationComponentResult:

    expected = clean_text(
        expected_scenario
    ).upper()

    observed = clean_text(
        observed_scenario
    ).upper()

    if not expected or not observed:
        return (
            ValidationComponentResult.UNDETERMINED
        )

    if expected == observed:
        return (
            ValidationComponentResult.CORRECT
        )

    return (
        ValidationComponentResult.INCORRECT
    )


def d14_validate_horizon(
    horizon: str,
    observation: D14OutcomeObservation,
) -> ValidationComponentResult:

    metadata = dict(
        observation.metadata
    )

    if "horizon_result" in metadata:

        value = clean_text(
            metadata["horizon_result"]
        ).upper()

        if value in {
            "CORRECT",
            "INCORRECT",
            "PARTIAL",
            "UNDETERMINED",
        }:
            return ValidationComponentResult(
                value
            )

    if "horizon_match" in metadata:

        value = metadata["horizon_match"]

        if value is True:
            return (
                ValidationComponentResult.CORRECT
            )

        if value is False:
            return (
                ValidationComponentResult.INCORRECT
            )

    # D14 does not invent horizon semantics.
    return (
        ValidationComponentResult.UNDETERMINED
    )


def d14_validate_invalidation(
    observation: D14OutcomeObservation,
) -> ValidationComponentResult:

    metadata = dict(
        observation.metadata
    )

    if "invalidation_result" in metadata:

        value = clean_text(
            metadata["invalidation_result"]
        ).upper()

        if value in {
            "CORRECT",
            "INCORRECT",
            "PARTIAL",
            "UNDETERMINED",
        }:
            return ValidationComponentResult(
                value
            )

    if observation.invalidation_triggered:
        return (
            ValidationComponentResult.INCORRECT
        )

    return (
        ValidationComponentResult.CORRECT
    )


def d14_validate_pnl(
    action: str,
    observation: D14OutcomeObservation,
) -> ValidationComponentResult:

    metadata = dict(
        observation.metadata
    )

    if "pnl_result" in metadata:

        explicit = clean_text(
            metadata["pnl_result"]
        ).upper()

        if explicit in {
            "CORRECT",
            "INCORRECT",
            "PARTIAL",
            "UNDETERMINED",
        }:
            return ValidationComponentResult(
                explicit
            )

    if observation.pnl_result is None:
        return (
            ValidationComponentResult.UNDETERMINED
        )

    pnl = clean_text(
        observation.pnl_result
    ).upper()

    if pnl in {
        "PROFIT",
        "POSITIVE",
        "WIN",
        "CORRECT",
    }:
        return (
            ValidationComponentResult.CORRECT
        )

    if pnl in {
        "LOSS",
        "NEGATIVE",
        "LOSS_MADE",
        "INCORRECT",
    }:
        return (
            ValidationComponentResult.INCORRECT
        )

    if pnl in {
        "PARTIAL",
        "MIXED",
    }:
        return (
            ValidationComponentResult.PARTIAL
        )

    return (
        ValidationComponentResult.UNDETERMINED
    )


# ============================================================================
# OVERALL RESULT
# ============================================================================

def d14_aggregate_result(
    *,
    direction_result: ValidationComponentResult,
    scenario_result: ValidationComponentResult,
    horizon_result: ValidationComponentResult,
    invalidation_result: ValidationComponentResult,
    pnl_result: ValidationComponentResult,
) -> ValidationResult:

    results = (
        direction_result,
        scenario_result,
        horizon_result,
        invalidation_result,
        pnl_result,
    )

    if all(
        result == ValidationComponentResult.CORRECT
        for result in results
    ):
        return ValidationResult.CORRECT

    if (
        direction_result
        == ValidationComponentResult.INCORRECT
    ):
        return ValidationResult.INCORRECT

    if any(
        result == ValidationComponentResult.INCORRECT
        for result in results
    ):

        correct_or_partial = any(
            result in (
                ValidationComponentResult.CORRECT,
                ValidationComponentResult.PARTIAL,
            )
            for result in results
        )

        if correct_or_partial:
            return ValidationResult.PARTIAL

        return ValidationResult.INCORRECT

    if any(
        result == ValidationComponentResult.PARTIAL
        for result in results
    ):
        return ValidationResult.PARTIAL

    return ValidationResult.UNDETERMINED


# ============================================================================
# VALIDATION ID
# ============================================================================

def d14_build_validation_id(
    decision_id: str,
    observation_ids: Sequence[str],
) -> str:

    seed = (
        normalize_id(decision_id)
        + "|"
        + "|".join(
            sorted(
                normalize_id(item)
                for item in observation_ids
            )
        )
    )

    digest = hashlib.sha256(
        seed.encode("utf-8")
    ).hexdigest()[:20]

    return f"D14-{digest}"


# ============================================================================
# D14 ENGINE
# ============================================================================

class D14DecisionValidationEngine:
    """
    D14 validation authority.

    D14 does not:
    - make decisions
    - execute trades
    - learn
    - modify D13
    - generate probability authority
    """

    NAME = D14_ENGINE_NAME
    VERSION = D14_ENGINE_VERSION
    AUTHORITY = D14_AUTHORITY

    DECISION_AUTHORITY = False
    EXECUTION_AUTHORITY = False
    LEARNING_AUTHORITY = False
    PROBABILITY_AUTHORITY = False

    def __init__(self) -> None:

        self._validation_history: list[
            D14ValidationEvidence
        ] = []

    # ------------------------------------------------------------------
    # PUBLIC VALIDATE
    # ------------------------------------------------------------------

    def validate(
        self,
        decision: D14DecisionSnapshot,
        observations: Sequence[
            D14OutcomeObservation
        ],
        *,
        validation_id: Optional[str] = None,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> D14ValidationEvidence:

        if not isinstance(
            decision,
            D14DecisionSnapshot,
        ):
            raise TypeError(
                "D14 requires D14DecisionSnapshot."
            )

        observations = tuple(
            observations
        )

        if not observations:

            return self._build_undetermined(
                decision,
                validation_id=validation_id,
                reasons=(
                    "NO_FUTURE_OBSERVATION_PROVIDED",
                ),
                metadata=metadata,
            )

        # --------------------------------------------------------------
        # INPUT VALIDATION
        # --------------------------------------------------------------

        identity_results = [
            d14_validate_identity(
                decision,
                observation,
            )
            for observation in observations
        ]

        temporal_results = [
            d14_validate_observation_cutoff(
                decision,
                observation,
            )
            for observation in observations
        ]

        provenance_results = [
            d14_validate_provenance(
                decision,
                observation,
            )
            for observation in observations
        ]

        identity_valid = all(
            result[0]
            for result in identity_results
        )

        temporal_valid = all(
            result[0]
            for result in temporal_results
        )

        provenance_valid = all(
            result[0]
            for result in provenance_results
        )

        future_leakage = any(
            "FUTURE_LEAKAGE_MARKER_DETECTED"
            in result[1]
            for result in temporal_results
        )

        all_reasons: list[str] = []

        for group in (
            identity_results,
            temporal_results,
            provenance_results,
        ):
            for _, reasons in group:
                all_reasons.extend(
                    reasons
                )

        # --------------------------------------------------------------
        # HARD BLOCK: IDENTITY
        # --------------------------------------------------------------

        if not identity_valid:

            return self._build_blocked(
                decision,
                observations,
                validation_id,
                (
                    "IDENTITY_VALIDATION_FAILED",
                    *all_reasons,
                ),
                D14ConflictType.IDENTITY_CONFLICT,
                metadata,
            )

        # --------------------------------------------------------------
        # HARD BLOCK: TEMPORAL
        # --------------------------------------------------------------

        if not temporal_valid:

            return self._build_blocked(
                decision,
                observations,
                validation_id,
                (
                    "TEMPORAL_VALIDATION_FAILED",
                    *all_reasons,
                ),
                D14ConflictType.TIMESTAMP_CONFLICT,
                metadata,
            )

        # --------------------------------------------------------------
        # HARD BLOCK: FUTURE LEAKAGE
        # --------------------------------------------------------------

        if future_leakage:

            return self._build_blocked(
                decision,
                observations,
                validation_id,
                (
                    "FUTURE_LEAKAGE_BLOCKED",
                    *all_reasons,
                ),
                D14ConflictType.LEAKAGE_CONFLICT,
                metadata,
            )

        # --------------------------------------------------------------
        # HARD BLOCK: PROVENANCE
        # --------------------------------------------------------------

        if not provenance_valid:

            return self._build_blocked(
                decision,
                observations,
                validation_id,
                (
                    "PROVENANCE_VALIDATION_FAILED",
                    *all_reasons,
                ),
                D14ConflictType.PROVENANCE_CONFLICT,
                metadata,
            )

        # --------------------------------------------------------------
        # COMPONENT VALIDATION
        # --------------------------------------------------------------

        last = observations[-1]

        direction_result = d14_validate_direction(
            decision.expected_direction,
            last.observed_direction,
        )

        scenario_result = d14_validate_scenario(
            decision.selected_scenario_type,
            last.observed_scenario_type,
        )

        horizon_result = d14_validate_horizon(
            decision.horizon,
            last,
        )

        invalidation_result = d14_validate_invalidation(
            last,
        )

        pnl_result = d14_validate_pnl(
            decision.action,
            last,
        )

        overall_result = d14_aggregate_result(
            direction_result=direction_result,
            scenario_result=scenario_result,
            horizon_result=horizon_result,
            invalidation_result=invalidation_result,
            pnl_result=pnl_result,
        )

        component_reasons: list[str] = []

        if direction_result == ValidationComponentResult.CORRECT:
            component_reasons.append(
                "DIRECTION_VALIDATED"
            )
        elif direction_result == ValidationComponentResult.INCORRECT:
            component_reasons.append(
                "DIRECTION_MISMATCH"
            )

        if scenario_result == ValidationComponentResult.CORRECT:
            component_reasons.append(
                "SCENARIO_VALIDATED"
            )
        elif scenario_result == ValidationComponentResult.INCORRECT:
            component_reasons.append(
                "SCENARIO_MISMATCH"
            )

        if horizon_result == ValidationComponentResult.CORRECT:
            component_reasons.append(
                "HORIZON_VALIDATED"
            )
        elif horizon_result == ValidationComponentResult.UNDETERMINED:
            component_reasons.append(
                "HORIZON_NOT_DETERMINED"
            )

        if invalidation_result == ValidationComponentResult.CORRECT:
            component_reasons.append(
                "INVALIDATION_NOT_TRIGGERED"
            )
        elif invalidation_result == ValidationComponentResult.INCORRECT:
            component_reasons.append(
                "INVALIDATION_TRIGGERED"
            )

        if pnl_result == ValidationComponentResult.CORRECT:
            component_reasons.append(
                "PNL_VALIDATED"
            )
        elif pnl_result == ValidationComponentResult.INCORRECT:
            component_reasons.append(
                "PNL_LOSS"
            )
        elif pnl_result == ValidationComponentResult.UNDETERMINED:
            component_reasons.append(
                "PNL_NOT_DETERMINED"
            )

        resolved_validation_id = (
            validation_id
            or d14_build_validation_id(
                decision.decision_id,
                [
                    observation.observation_id
                    for observation in observations
                ],
            )
        )

        evidence = D14ValidationEvidence(
            validation_id=resolved_validation_id,
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=(
                decision.decision_timestamp
            ),

            validation_timestamp=max(
                observation.observation_timestamp
                for observation in observations
            ),

            status=self._status_from_result(
                overall_result
            ),

            overall_result=overall_result,

            direction_result=direction_result,
            scenario_result=scenario_result,
            horizon_result=horizon_result,
            invalidation_result=invalidation_result,
            pnl_result=pnl_result,

            expected_direction=(
                decision.expected_direction
            ),

            observed_direction=(
                last.observed_direction
            ),

            action=decision.action,

            selected_scenario_id=(
                decision.selected_scenario_id
            ),

            selected_scenario_type=(
                decision.selected_scenario_type
            ),

            horizon=decision.horizon,

            source_engine=(
                decision.source_engine
            ),

            source_engine_version=(
                decision.source_engine_version
            ),

            future_leakage=False,
            identity_mismatch=False,
            temporal_valid=True,
            provenance_valid=True,

            validation_reasons=tuple(
                component_reasons
            ),

            evidence_ids=tuple(
                observation.observation_id
                for observation in observations
            ),

            provenance={
                "d13_decision_id": (
                    decision.decision_id
                ),
                "d13_snapshot_hash": (
                    decision.snapshot_hash
                ),
                "d14_engine": (
                    D14_ENGINE_NAME
                ),
                "d14_version": (
                    D14_ENGINE_VERSION
                ),
                "future_data_allowed": False,
                "future_data_before_decision": False,
                "future_leakage": False,
                "learning_authority": False,
                "execution_authority": False,
            },

            metadata={
                **(
                    dict(metadata)
                    if metadata is not None
                    else {}
                ),
                "component_reason_count": len(
                    component_reasons
                ),
            },

            validated_by_D14=True,
            D14_modified=False,
            D13_modified=False,
            learning_performed=False,
            execution_performed=False,
        )

        self._validation_history.append(
            evidence
        )

        return evidence

    # ------------------------------------------------------------------
    # AGGREGATE
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate_component(
        results: tuple[
            ValidationComponentResult,
            ...,
        ],
    ) -> ValidationResult:

        if not results:
            return ValidationResult.UNDETERMINED

        return d14_aggregate_result(
            direction_result=results[0],
            scenario_result=results[1],
            horizon_result=results[2],
            invalidation_result=results[3],
            pnl_result=results[4],
        )

    # ------------------------------------------------------------------
    # TEXT AGGREGATION
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate_text(
        *groups: tuple[str, ...],
    ) -> tuple[str, ...]:

        output: list[str] = []

        for group in groups:

            for item in group:

                value = clean_text(item)

                if value and value not in output:
                    output.append(value)

        return tuple(output)

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def _status_from_result(
        result: ValidationResult,
    ) -> D14Status:

        if result == ValidationResult.CORRECT:
            return D14Status.READY

        if result == ValidationResult.PARTIAL:
            return D14Status.LIMITED

        if result == ValidationResult.INCORRECT:
            return D14Status.LIMITED

        return D14Status.UNDETERMINED

    # ------------------------------------------------------------------
    # UNDETERMINED
    # ------------------------------------------------------------------

    def _build_undetermined(
        self,
        decision: D14DecisionSnapshot,
        validation_id: Optional[str] = None,
        reasons: tuple[str, ...] = (),
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> D14ValidationEvidence:

        resolved_validation_id = (
            validation_id
            or d14_build_validation_id(
                decision.decision_id,
                (),
            )
        )

        evidence = D14ValidationEvidence(
            validation_id=resolved_validation_id,
            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=(
                decision.decision_timestamp
            ),

            validation_timestamp=(
                decision.decision_timestamp
            ),

            status=D14Status.UNDETERMINED,

            overall_result=(
                ValidationResult.UNDETERMINED
            ),

            direction_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            scenario_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            horizon_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            invalidation_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            pnl_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            expected_direction=(
                decision.expected_direction
            ),

            observed_direction="",

            action=decision.action,

            selected_scenario_id=(
                decision.selected_scenario_id
            ),

            selected_scenario_type=(
                decision.selected_scenario_type
            ),

            horizon=decision.horizon,

            source_engine=(
                decision.source_engine
            ),

            source_engine_version=(
                decision.source_engine_version
            ),

            future_leakage=False,
            identity_mismatch=False,
            temporal_valid=False,
            provenance_valid=False,

            validation_reasons=self._aggregate_text(
                reasons,
                (
                    "VALIDATION_UNDETERMINED",
                ),
            ),

            evidence_ids=(),

            provenance={
                "d13_decision_id": (
                    decision.decision_id
                ),
                "d13_snapshot_hash": (
                    decision.snapshot_hash
                ),
                "d14_engine": (
                    D14_ENGINE_NAME
                ),
                "d14_version": (
                    D14_ENGINE_VERSION
                ),
                "future_data_allowed": False,
                "future_data_before_decision": False,
                "future_leakage": False,
                "authority_isolation": True,
                "learning_authority": False,
                "execution_authority": False,
                "undetermined": True,
            },

            metadata={
                **(
                    dict(metadata)
                    if metadata is not None
                    else {}
                ),
                "undetermined_reason": (
                    reasons
                    if reasons
                    else (
                        "NO_VALIDATED_OUTCOME",
                    )
                ),
            },

            validated_by_D14=False,
            D14_modified=False,
            D13_modified=False,
            learning_performed=False,
            execution_performed=False,
        )

        self._validation_history.append(
            evidence
        )

        return evidence

    # ------------------------------------------------------------------
    # BLOCKED
    # ------------------------------------------------------------------

    def _build_blocked(
        self,
        decision: D14DecisionSnapshot,
        observations: tuple[
            D14OutcomeObservation,
            ...,
        ],
        validation_id: Optional[str],
        reasons: tuple[str, ...],
        conflict: D14ConflictType,
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> D14ValidationEvidence:

        reason_set = set(
            reasons
        )

        future_leakage = (
            "FUTURE_LEAKAGE_MARKER_DETECTED"
            in reason_set
            or "FUTURE_LEAKAGE_BLOCKED"
            in reason_set
        )

        identity_mismatch = (
            "MARKET_ID_MISMATCH"
            in reason_set
            or conflict
            == D14ConflictType.IDENTITY_CONFLICT
        )

        temporal_valid = not (
            "OBSERVATION_NOT_STRICTLY_AFTER_DECISION"
            in reason_set
            or conflict
            == D14ConflictType.TIMESTAMP_CONFLICT
        )

        provenance_valid = not (
            "MISSING_OBSERVATION_SOURCE"
            in reason_set
            or "MISSING_OBSERVATION_SOURCE_VERSION"
            in reason_set
            or conflict
            == D14ConflictType.PROVENANCE_CONFLICT
        )

        validation_timestamp = (
            max(
                observation.observation_timestamp
                for observation in observations
            )
            if observations
            else decision.decision_timestamp
        )

        resolved_validation_id = (
            validation_id
            or d14_build_validation_id(
                decision.decision_id,
                [
                    observation.observation_id
                    for observation in observations
                ],
            )
        )

        evidence = D14ValidationEvidence(
            validation_id=resolved_validation_id,

            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=(
                decision.decision_timestamp
            ),

            validation_timestamp=(
                validation_timestamp
            ),

            status=D14Status.BLOCKED,

            overall_result=(
                ValidationResult.UNDETERMINED
            ),

            direction_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            scenario_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            horizon_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            invalidation_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            pnl_result=(
                ValidationComponentResult.UNDETERMINED
            ),

            expected_direction=(
                decision.expected_direction
            ),

            observed_direction=(
                observations[-1].observed_direction
                if observations
                else ""
            ),

            action=decision.action,

            selected_scenario_id=(
                decision.selected_scenario_id
            ),

            selected_scenario_type=(
                decision.selected_scenario_type
            ),

            horizon=decision.horizon,

            source_engine=(
                decision.source_engine
            ),

            source_engine_version=(
                decision.source_engine_version
            ),

            future_leakage=future_leakage,

            identity_mismatch=identity_mismatch,

            temporal_valid=temporal_valid,

            provenance_valid=provenance_valid,

            validation_reasons=self._aggregate_text(
                reasons,
                (
                    "D14_VALIDATION_BLOCKED",
                ),
            ),

            evidence_ids=tuple(
                observation.observation_id
                for observation in observations
            ),

            provenance={
                "d13_decision_id": (
                    decision.decision_id
                ),
                "d13_snapshot_hash": (
                    decision.snapshot_hash
                ),
                "d14_engine": (
                    D14_ENGINE_NAME
                ),
                "d14_version": (
                    D14_ENGINE_VERSION
                ),
                "conflict_type": conflict.value,
                "future_data_allowed": False,
                "future_data_before_decision": False,
                "future_leakage": future_leakage,
                "identity_mismatch": identity_mismatch,
                "temporal_valid": temporal_valid,
                "provenance_valid": provenance_valid,
                "learning_authority": False,
                "execution_authority": False,
                "d13_modified": False,
            },

            metadata={
                **(
                    dict(metadata)
                    if metadata is not None
                    else {}
                ),
                "blocked": True,
                "conflict_type": conflict.value,
            },

            validated_by_D14=False,
            D14_modified=False,
            D13_modified=False,
            learning_performed=False,
            execution_performed=False,
        )

        self._validation_history.append(
            evidence
        )

        return evidence

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------

    def history(
        self,
    ) -> tuple[D14ValidationEvidence, ...]:

        return tuple(
            self._validation_history
        )


# ============================================================================
# D14 CONTRACT
# ============================================================================

def build_d14_contract() -> D14ValidationContract:

    return D14ValidationContract(
        engine_name=D14_ENGINE_NAME,
        engine_version=D14_ENGINE_VERSION,
        authority=D14_AUTHORITY,

        status=D14Status.READY,

        validation=None,

        d13_source=D14_D13_SOURCE,
        d15_target=D14_D15_TARGET,

        decision_authority=False,
        execution_authority=False,
        learning_authority=False,
        probability_authority=False,

        future_data_required=True,
        future_data_allowed_before_decision=False,

        created_at=utc_now(),

        metadata={
            "contract": "D14_TO_D15",
            "validation_only": True,
            "d13_mutation": False,
            "learning_isolation": True,
            "execution_isolation": True,
        },
    )


def validate_d14_contract(
    contract: D14ValidationContract,
) -> bool:

    if contract.engine_name != D14_ENGINE_NAME:
        return False

    if contract.engine_version != D14_ENGINE_VERSION:
        return False

    if contract.authority != D14_AUTHORITY:
        return False

    if contract.decision_authority:
        return False

    if contract.execution_authority:
        return False

    if contract.learning_authority:
        return False

    if contract.probability_authority:
        return False

    if contract.d13_source != D14_D13_SOURCE:
        return False

    if contract.d15_target != D14_D15_TARGET:
        return False

    if not contract.future_data_required:
        return False

    if contract.future_data_allowed_before_decision:
        return False

    return True


# ============================================================================
# D14 → D15 HANDOFF
# ============================================================================

def d14_to_d15_handoff(
    evidence: D14ValidationEvidence,
) -> Mapping[str, Any]:

    if evidence.status == D14Status.BLOCKED:
        raise ValueError(
            "BLOCKED D14 evidence cannot be handed to D15"
        )

    if not evidence.validated_by_D14:
        raise ValueError(
            "D14 evidence is not validated"
        )

    payload = evidence.to_d15_payload()

    return MappingProxyType(
        {
            **dict(payload),

            "handoff_authority": "D14",

            "learning_authority": False,

            "execution_authority": False,

            "future_data_allowed": False,
        }
    )


# ============================================================================
# FACTORY
# ============================================================================

def create_d14_engine() -> D14DecisionValidationEngine:
    return D14DecisionValidationEngine()


def create_d14_decision(
    **kwargs: Any,
) -> D14DecisionSnapshot:

    return D14DecisionSnapshot(
        **kwargs
    )


def create_d14_observation(
    **kwargs: Any,
) -> D14OutcomeObservation:

    return D14OutcomeObservation(
        **kwargs
    )


# ============================================================================
# SELF TEST
# ============================================================================

def _d14_self_test() -> None:

    engine = create_d14_engine()

    # ------------------------------------------------------------------
    # 1. D13 DECISION SNAPSHOT
    # ------------------------------------------------------------------

    decision = create_d14_decision(
        decision_id="D13-TEST-001",
        market_id="NIFTY",
        decision_timestamp=datetime.fromisoformat(
            "2026-09-08T09:15:00+00:00"
        ),
        action="BUY",
        expected_direction="UP",

        selected_scenario_id="SC-001",
        selected_scenario_type="BREAKOUT",

        horizon="INTRADAY",

        entry_level=25000,
        stop_loss_level=24900,
        take_profit_level=25100,

        source_engine="D13_DecisionEngine",
        source_engine_version="D13-2.0",

        metadata={
            "test": True,
        },
    )

    # ------------------------------------------------------------------
    # 2. CORRECT FUTURE OBSERVATION
    # ------------------------------------------------------------------

    observation = create_d14_observation(
        observation_id="OBS-001",
        market_id="NIFTY",

        observation_timestamp=datetime.fromisoformat(
            "2026-09-08T09:30:00+00:00"
        ),

        observed_direction="UP",
        observed_scenario_type="BREAKOUT",

        price_at_observation=25050,
        high_price=25100,
        low_price=24980,
        close_price=25050,

        invalidation_triggered=False,

        pnl_result="PROFIT",

        source="TEST_MARKET_SOURCE",
        source_version="1.0",

        metadata={
            "horizon_result": "CORRECT",
        },
    )

    original_hash = decision.snapshot_hash

    # ------------------------------------------------------------------
    # 3. D13 DECISION ACCEPTED
    # ------------------------------------------------------------------

    assert (
        decision.decision_id
        == "D13-TEST-001"
    )

    # ------------------------------------------------------------------
    # 4. CORRECT VALIDATION
    # ------------------------------------------------------------------

    result = engine.validate(
        decision,
        (observation,),
    )

    assert (
        result.overall_result
        == ValidationResult.CORRECT
    )

    assert (
        result.status
        == D14Status.READY
    )

    # ------------------------------------------------------------------
    # 5. D13 IMMUTABILITY
    # ------------------------------------------------------------------

    assert (
        decision.snapshot_hash
        == original_hash
    )

    # ------------------------------------------------------------------
    # 6. D14 → D15 HANDOFF
    # ------------------------------------------------------------------

    handoff = d14_to_d15_handoff(
        result
    )

    assert (
        handoff["handoff_authority"]
        == "D14"
    )

    assert (
        handoff["learning_authority"]
        is False
    )

    # ------------------------------------------------------------------
    # Helper for block tests
    # ------------------------------------------------------------------

    def make_observation(
        observation_id: str,
        timestamp: str,
        market_id: str = "NIFTY",
        metadata: Optional[
            Mapping[str, Any]
        ] = None,
    ) -> D14OutcomeObservation:

        return create_d14_observation(
            observation_id=observation_id,
            market_id=market_id,

            observation_timestamp=datetime.fromisoformat(
                timestamp
            ),

            observed_direction="UP",
            observed_scenario_type="BREAKOUT",

            price_at_observation=25000,
            high_price=25000,
            low_price=25000,
            close_price=25000,

            invalidation_triggered=False,

            pnl_result="PROFIT",

            source="TEST_MARKET_SOURCE",
            source_version="1.0",

            metadata=metadata or {},
        )

    # ------------------------------------------------------------------
    # 7. SAME TIMESTAMP MUST BLOCK
    # ------------------------------------------------------------------

    same_time = make_observation(
        "OBS-002",
        "2026-09-08T09:15:00+00:00",
    )

    blocked_same = engine.validate(
        decision,
        (same_time,),
    )

    assert (
        blocked_same.status
        == D14Status.BLOCKED
    )

    # ------------------------------------------------------------------
    # 8. EARLIER TIMESTAMP MUST BLOCK
    # ------------------------------------------------------------------

    earlier = make_observation(
        "OBS-003",
        "2026-09-08T09:00:00+00:00",
    )

    blocked_earlier = engine.validate(
        decision,
        (earlier,),
    )

    assert (
        blocked_earlier.status
        == D14Status.BLOCKED
    )

    # ------------------------------------------------------------------
    # 9. FUTURE LEAKAGE MUST BLOCK
    # ------------------------------------------------------------------

    leakage = make_observation(
        "OBS-004",
        "2026-09-08T09:30:00+00:00",
        metadata={
            "future_leakage": True,
        },
    )

    blocked_leakage = engine.validate(
        decision,
        (leakage,),
    )

    assert (
        blocked_leakage.status
        == D14Status.BLOCKED
    )

    assert (
        blocked_leakage.future_leakage
        is True
    )

    # ------------------------------------------------------------------
    # 10. WRONG MARKET MUST BLOCK
    # ------------------------------------------------------------------

    wrong_market = make_observation(
        "OBS-005",
        "2026-09-08T09:30:00+00:00",
        market_id="BANKNIFTY",
    )

    blocked_market = engine.validate(
        decision,
        (wrong_market,),
    )

    assert (
        blocked_market.status
        == D14Status.BLOCKED
    )

    assert (
        blocked_market.identity_mismatch
        is True
    )

    # ------------------------------------------------------------------
    # 11. PARTIAL VALIDATION
    # ------------------------------------------------------------------

    partial_observation = create_d14_observation(
        observation_id="OBS-006",
        market_id="NIFTY",

        observation_timestamp=datetime.fromisoformat(
            "2026-09-08T09:30:00+00:00"
        ),

        observed_direction="UP",
        observed_scenario_type="REVERSAL",

        price_at_observation=25050,
        high_price=25100,
        low_price=24980,
        close_price=25050,

        invalidation_triggered=False,

        pnl_result="PROFIT",

        source="TEST_MARKET_SOURCE",
        source_version="1.0",

        metadata={
            "horizon_result": "CORRECT",
        },
    )

    partial = engine.validate(
        decision,
        (partial_observation,),
    )

    assert (
        partial.overall_result
        == ValidationResult.PARTIAL
    )

    # ------------------------------------------------------------------
    # 12. NO OBSERVATION
    # ------------------------------------------------------------------

    no_observation = engine.validate(
        decision,
        (),
    )

    assert (
        no_observation.overall_result
        == ValidationResult.UNDETERMINED
    )

    assert (
        no_observation.validated_by_D14
        is False
    )

    # ------------------------------------------------------------------
    # 13. INVALID PROVENANCE
    # ------------------------------------------------------------------

    invalid_source = make_observation(
        "OBS-007",
        "2026-09-08T09:30:00+00:00",
    )

    invalid_source = D14OutcomeObservation(
        observation_id=(
            invalid_source.observation_id
        ),
        market_id=(
            invalid_source.market_id
        ),
        observation_timestamp=(
            invalid_source.observation_timestamp
        ),
        observed_direction=(
            invalid_source.observed_direction
        ),
        observed_scenario_type=(
            invalid_source.observed_scenario_type
        ),
        price_at_observation=(
            invalid_source.price_at_observation
        ),
        high_price=(
            invalid_source.high_price
        ),
        low_price=(
            invalid_source.low_price
        ),
        close_price=(
            invalid_source.close_price
        ),
        invalidation_triggered=(
            invalid_source.invalidation_triggered
        ),
        pnl_result=(
            invalid_source.pnl_result
        ),
        source="",
        source_version="",
        metadata=invalid_source.metadata,
    )

    blocked_provenance = engine.validate(
        decision,
        (invalid_source,),
    )

    assert (
        blocked_provenance.status
        == D14Status.BLOCKED
    )

    assert (
        blocked_provenance.provenance_valid
        is False
    )

    # ------------------------------------------------------------------
    # 14. CONTRACT
    # ------------------------------------------------------------------

    contract = build_d14_contract()

    assert (
        validate_d14_contract(contract)
        is True
    )

    assert (
        contract.can_modify_d13
        is False
    )

    assert (
        contract.can_learn
        is False
    )

    assert (
        contract.can_execute
        is False
    )

    assert (
        contract.can_generate_probability
        is False
    )

    # ------------------------------------------------------------------
    # 15. D14 NEVER LEARNS
    # ------------------------------------------------------------------

    assert (
        contract.can_learn
        is False
    )

    # ------------------------------------------------------------------
    # 16. D14 NEVER EXECUTES
    # ------------------------------------------------------------------

    assert (
        contract.can_execute
        is False
    )

    # ------------------------------------------------------------------
    # 17. D13 NEVER MODIFIED
    # ------------------------------------------------------------------

    assert (
        contract.can_modify_d13
        is False
    )

    assert (
        decision.snapshot_hash
        == original_hash
    )

    # ------------------------------------------------------------------
    # FINAL
    # ------------------------------------------------------------------

    print(
        "D14 V2.0 SELF-TEST: PASS"
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    _d14_self_test()