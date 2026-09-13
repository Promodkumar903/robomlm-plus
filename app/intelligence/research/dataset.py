# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/dataset.py
# RESEARCH DATASET MANAGEMENT — PART 1
# FOUNDATION + CONTRACTS
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Optional
from uuid import uuid4


# ============================================================
# CONSTANTS
# ============================================================

DATASET_MANAGER_ENGINE = "ROBOMLM_RESEARCH_DATASET_MANAGER"
DATASET_MANAGER_VERSION = "1.0"


# ============================================================
# ENUMS
# ============================================================

class DatasetStatus(str, Enum):
    NEW = "NEW"
    REGISTERED = "REGISTERED"
    INGESTING = "INGESTING"
    READY = "READY"
    VALIDATING = "VALIDATING"
    INVALID = "INVALID"
    ARCHIVED = "ARCHIVED"


class DatasetType(str, Enum):
    MARKET = "MARKET"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"
    FEATURE = "FEATURE"
    EXPERIMENT = "EXPERIMENT"
    RESEARCH = "RESEARCH"
    SYNTHETIC = "SYNTHETIC"
    UNKNOWN = "UNKNOWN"


class DatasetPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class DatasetContractStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


# ============================================================
# REQUEST CONTRACT
# ============================================================

@dataclass(frozen=True)
class DatasetRequest:
    """
    Entry contract for the Research Dataset Manager.

    The manager registers and evaluates dataset state.
    It does not invent dataset content or research conclusions.
    """

    dataset: Any

    dataset_type: DatasetType = DatasetType.UNKNOWN

    source: Optional[Any] = None
    schema: Optional[Any] = None
    provenance: Optional[Any] = None

    priority: DatasetPriority = DatasetPriority.UNKNOWN

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    request_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if self.dataset is None:
            errors.append("Dataset is required.")

        if not self.request_id:
            errors.append("request_id is required.")

        if not isinstance(self.metadata, Mapping):
            errors.append("metadata must be a Mapping.")

        return tuple(errors)


# ============================================================
# DATASET REFERENCE
# ============================================================

@dataclass(frozen=True)
class DatasetReference:
    """
    Normalized identity reference for a research dataset.
    """

    dataset_id: str
    name: str

    dataset_type: DatasetType
    status: DatasetStatus
    priority: DatasetPriority

    source_id: str = ""
    schema_id: str = ""
    provenance_id: str = ""

    version: str = ""

    raw_dataset: Any = None


@dataclass(frozen=True)
class DatasetSourceReference:
    """
    Provenance/source reference.

    No source credibility score is invented here.
    """

    source_id: str
    source_type: str = ""
    source_name: str = ""
    source_version: str = ""
    source_location: str = ""

    raw_source: Any = None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

@dataclass(frozen=True)
class DatasetContractValidation:
    status: DatasetContractStatus

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return (
            self.status == DatasetContractStatus.VALID
            and not self.errors
        )


# ============================================================
# SAFE READ HELPERS
# ============================================================

def _ds_read_value(
    obj: Any,
    *names: str,
    default: Any = None,
) -> Any:
    """
    Read explicit values from mappings or objects.

    No calculations or inferred values are performed.
    """
    if obj is None:
        return default

    if isinstance(obj, Mapping):
        for name in names:
            if name in obj:
                return obj[name]
        return default

    for name in names:
        if hasattr(obj, name):
            try:
                return getattr(obj, name)
            except Exception:
                continue

    return default


def _ds_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text if text else default


def _ds_enum(
    value: Any,
    enum_type: type[Enum],
    default: Enum,
) -> Enum:
    if isinstance(value, enum_type):
        return value

    if value is None:
        return default

    text = str(value).strip().upper()

    for member in enum_type:
        if text in {
            member.name.upper(),
            str(member.value).upper(),
        }:
            return member

    return default


# ============================================================
# DATASET REFERENCE BUILDER
# ============================================================

def build_dataset_reference(
    dataset: Any,
    dataset_type: DatasetType = DatasetType.UNKNOWN,
    priority: DatasetPriority = DatasetPriority.UNKNOWN,
) -> DatasetReference:
    """
    Build a normalized dataset identity reference.

    Only explicitly supplied fields are consumed.
    """

    dataset_id = _ds_text(
        _ds_read_value(
            dataset,
            "dataset_id",
            "id",
            "uuid",
        )
    )

    name = _ds_text(
        _ds_read_value(
            dataset,
            "name",
            "dataset_name",
            "title",
        )
    )

    status = _ds_enum(
        _ds_read_value(
            dataset,
            "status",
            "state",
        ),
        DatasetStatus,
        DatasetStatus.NEW,
    )

    resolved_type = _ds_enum(
        _ds_read_value(
            dataset,
            "dataset_type",
            "type",
        ),
        DatasetType,
        dataset_type,
    )

    resolved_priority = _ds_enum(
        _ds_read_value(
            dataset,
            "priority",
        ),
        DatasetPriority,
        priority,
    )

    source_id = _ds_text(
        _ds_read_value(
            dataset,
            "source_id",
            "source",
        )
    )

    schema_id = _ds_text(
        _ds_read_value(
            dataset,
            "schema_id",
            "schema",
        )
    )

    provenance_id = _ds_text(
        _ds_read_value(
            dataset,
            "provenance_id",
            "provenance",
        )
    )

    version = _ds_text(
        _ds_read_value(
            dataset,
            "version",
            "dataset_version",
        )
    )

    return DatasetReference(
        dataset_id=dataset_id,
        name=name,
        dataset_type=resolved_type,
        status=status,
        priority=resolved_priority,
        source_id=source_id,
        schema_id=schema_id,
        provenance_id=provenance_id,
        version=version,
        raw_dataset=dataset,
    )


# ============================================================
# SOURCE REFERENCE BUILDER
# ============================================================

def build_dataset_source_reference(
    source: Any,
) -> Optional[DatasetSourceReference]:
    if source is None:
        return None

    return DatasetSourceReference(
        source_id=_ds_text(
            _ds_read_value(
                source,
                "source_id",
                "id",
                "uuid",
            )
        ),
        source_type=_ds_text(
            _ds_read_value(
                source,
                "source_type",
                "type",
            )
        ),
        source_name=_ds_text(
            _ds_read_value(
                source,
                "source_name",
                "name",
                "title",
            )
        ),
        source_version=_ds_text(
            _ds_read_value(
                source,
                "source_version",
                "version",
            )
        ),
        source_location=_ds_text(
            _ds_read_value(
                source,
                "source_location",
                "location",
                "uri",
            )
        ),
        raw_source=source,
    )


# ============================================================
# REQUEST VALIDATION
# ============================================================

def validate_dataset_request(
    request: DatasetRequest,
) -> DatasetContractValidation:
    errors = list(request.validate())
    warnings: list[str] = []

    if not errors:
        reference = build_dataset_reference(
            request.dataset,
            request.dataset_type,
            request.priority,
        )

        if not reference.dataset_id:
            warnings.append(
                "Dataset identity is not explicitly available."
            )

        if not reference.name:
            warnings.append(
                "Dataset name is not explicitly available."
            )

        if reference.dataset_type == DatasetType.UNKNOWN:
            warnings.append(
                "Dataset type is UNKNOWN."
            )

        if reference.priority == DatasetPriority.UNKNOWN:
            warnings.append(
                "Dataset priority is UNKNOWN."
            )

    return DatasetContractValidation(
        status=(
            DatasetContractStatus.VALID
            if not errors
            else DatasetContractStatus.INVALID
        ),
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/dataset.py
# RESEARCH DATASET MANAGEMENT — PART 2
# REQUIREMENTS + CONSISTENCY + ASSESSMENT
# ============================================================


# ============================================================
# ENUMS
# ============================================================

class DatasetConsistency(str, Enum):
    CONSISTENT = "CONSISTENT"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"


class DatasetDataState(str, Enum):
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"


class DatasetDisposition(str, Enum):
    ADVANCE = "ADVANCE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"
    UNKNOWN = "UNKNOWN"


# ============================================================
# REQUIREMENTS
# ============================================================

@dataclass(frozen=True)
class DatasetRequirements:
    dataset_available: bool
    dataset_id_available: bool
    name_available: bool
    type_available: bool
    status_available: bool
    source_available: bool
    schema_available: bool
    provenance_available: bool
    version_available: bool
    priority_available: bool

    identity_consistent: bool = True
    provenance_consistent: bool = True


# ============================================================
# INTELLIGENCE
# ============================================================

@dataclass(frozen=True)
class DatasetIntelligence:
    consistency: DatasetConsistency
    data_state: DatasetDataState

    status: DatasetStatus
    dataset_type: DatasetType
    priority: DatasetPriority
    disposition: DatasetDisposition

    dataset_id: str
    name: str
    source_id: str
    schema_id: str
    provenance_id: str
    version: str

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    source: str = DATASET_MANAGER_ENGINE


# ============================================================
# ASSESSMENT
# ============================================================

@dataclass(frozen=True)
class DatasetAssessment:
    intelligence: DatasetIntelligence
    requirements: DatasetRequirements

    dataset: Optional[DatasetReference]
    source: Optional[DatasetSourceReference]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


# ============================================================
# STATUS HELPERS
# ============================================================

def _ds_status_is_invalid(
    status: Any,
) -> bool:
    value = _ds_text(status).upper()

    return value in {
        "INVALID",
        "CORRUPT",
        "ERROR",
        "FAILED",
    }


def _ds_status_is_blocking(
    status: Any,
) -> bool:
    value = _ds_text(status).upper()

    return value in {
        "INVALID",
        "CORRUPT",
        "ERROR",
        "FAILED",
        "BLOCKED",
        "REJECTED",
    }


def _ds_status_is_unknown(
    status: Any,
) -> bool:
    value = _ds_text(status).upper()

    return value in {
        "",
        "UNKNOWN",
        "UNSPECIFIED",
        "N/A",
        "NA",
        "NONE",
    }


# ============================================================
# REQUIREMENT EVALUATION
# ============================================================

def evaluate_dataset_requirements(
    request: DatasetRequest,
) -> DatasetRequirements:
    reference = build_dataset_reference(
        request.dataset,
        request.dataset_type,
        request.priority,
    )

    source = build_dataset_source_reference(
        request.source
    )

    return DatasetRequirements(
        dataset_available=request.dataset is not None,
        dataset_id_available=bool(reference.dataset_id),
        name_available=bool(reference.name),
        type_available=(
            reference.dataset_type != DatasetType.UNKNOWN
        ),
        status_available=(
            not _ds_status_is_unknown(reference.status.value)
        ),
        source_available=(
            source is not None
            or bool(reference.source_id)
        ),
        schema_available=(
            request.schema is not None
            or bool(reference.schema_id)
        ),
        provenance_available=(
            request.provenance is not None
            or bool(reference.provenance_id)
        ),
        version_available=bool(reference.version),
        priority_available=(
            reference.priority != DatasetPriority.UNKNOWN
        ),
    )


# ============================================================
# DATA STATE EVALUATION
# ============================================================

def evaluate_dataset_data_state(
    requirements: DatasetRequirements,
) -> DatasetDataState:
    if not requirements.dataset_available:
        return DatasetDataState.MISSING

    if not requirements.dataset_id_available:
        return DatasetDataState.PARTIAL

    if not requirements.name_available:
        return DatasetDataState.PARTIAL

    if not requirements.type_available:
        return DatasetDataState.PARTIAL

    if not requirements.status_available:
        return DatasetDataState.PARTIAL

    return DatasetDataState.COMPLETE


# ============================================================
# CONSISTENCY EVALUATION
# ============================================================

def evaluate_dataset_consistency(
    dataset: Optional[DatasetReference],
    source: Optional[DatasetSourceReference],
    requirements: DatasetRequirements,
) -> DatasetConsistency:

    if not requirements.dataset_available:
        return DatasetConsistency.INSUFFICIENT

    if (
        not requirements.dataset_id_available
        or not requirements.name_available
        or not requirements.type_available
    ):
        return DatasetConsistency.INSUFFICIENT

    if _ds_status_is_invalid(dataset.status.value):
        return DatasetConsistency.CONFLICTING

    if (
        source is not None
        and dataset.source_id
        and source.source_id
        and dataset.source_id != source.source_id
    ):
        return DatasetConsistency.CONFLICTING

    if not requirements.identity_consistent:
        return DatasetConsistency.CONFLICTING

    if not requirements.provenance_consistent:
        return DatasetConsistency.CONFLICTING

    return DatasetConsistency.CONSISTENT


# ============================================================
# DISPOSITION
# ============================================================

def evaluate_dataset_disposition(
    status: DatasetStatus,
    consistency: DatasetConsistency,
    data_state: DatasetDataState,
    priority: DatasetPriority,
) -> DatasetDisposition:

    if consistency == DatasetConsistency.CONFLICTING:
        return DatasetDisposition.INVALIDATE

    if data_state == DatasetDataState.MISSING:
        return DatasetDisposition.HOLD

    if data_state == DatasetDataState.PARTIAL:
        return DatasetDisposition.REVIEW

    if status in {
        DatasetStatus.INVALID,
    }:
        return DatasetDisposition.INVALIDATE

    if status == DatasetStatus.ARCHIVED:
        return DatasetDisposition.ARCHIVE

    if status == DatasetStatus.READY:
        return DatasetDisposition.ADVANCE

    if status in {
        DatasetStatus.NEW,
        DatasetStatus.REGISTERED,
        DatasetStatus.INGESTING,
        DatasetStatus.VALIDATING,
    }:
        if priority in {
            DatasetPriority.HIGH,
            DatasetPriority.CRITICAL,
        }:
            return DatasetDisposition.REVIEW

        return DatasetDisposition.HOLD

    return DatasetDisposition.UNKNOWN


# ============================================================
# INTELLIGENCE BUILDER
# ============================================================

def build_dataset_intelligence(
    dataset: DatasetReference,
    requirements: DatasetRequirements,
    source: Optional[DatasetSourceReference] = None,
) -> DatasetIntelligence:

    data_state = evaluate_dataset_data_state(
        requirements
    )

    consistency = evaluate_dataset_consistency(
        dataset,
        source,
        requirements,
    )

    disposition = evaluate_dataset_disposition(
        dataset.status,
        consistency,
        data_state,
        dataset.priority,
    )

    rationale: list[str] = []
    warnings: list[str] = []

    if consistency == DatasetConsistency.CONSISTENT:
        rationale.append(
            "Dataset identity and supplied references are consistent."
        )

    if consistency == DatasetConsistency.CONFLICTING:
        rationale.append(
            "Dataset contains a detected identity or state conflict."
        )
        warnings.append(
            "Dataset must not advance while consistency is conflicting."
        )

    if consistency == DatasetConsistency.INSUFFICIENT:
        warnings.append(
            "Insufficient dataset information for controlled advancement."
        )

    if data_state == DatasetDataState.PARTIAL:
        warnings.append(
            "Dataset contract is partially populated."
        )

    if data_state == DatasetDataState.MISSING:
        warnings.append(
            "Dataset is unavailable."
        )

    if not requirements.schema_available:
        warnings.append(
            "Dataset schema reference is not explicitly available."
        )

    if not requirements.provenance_available:
        warnings.append(
            "Dataset provenance reference is not explicitly available."
        )

    if dataset.status == DatasetStatus.READY:
        rationale.append(
            "Dataset explicitly reports READY state."
        )

    return DatasetIntelligence(
        consistency=consistency,
        data_state=data_state,
        status=dataset.status,
        dataset_type=dataset.dataset_type,
        priority=dataset.priority,
        disposition=disposition,
        dataset_id=dataset.dataset_id,
        name=dataset.name,
        source_id=dataset.source_id,
        schema_id=dataset.schema_id,
        provenance_id=dataset.provenance_id,
        version=dataset.version,
        rationale=tuple(rationale),
        warnings=tuple(warnings),
        source=DATASET_MANAGER_ENGINE,
    )


# ============================================================
# ASSESSMENT BUILDER
# ============================================================

def build_dataset_assessment(
    request: DatasetRequest,
) -> DatasetAssessment:

    dataset = build_dataset_reference(
        request.dataset,
        request.dataset_type,
        request.priority,
    )

    source = build_dataset_source_reference(
        request.source
    )

    requirements = evaluate_dataset_requirements(
        request
    )

    intelligence = build_dataset_intelligence(
        dataset,
        requirements,
        source,
    )

    rationale = tuple(
        dict.fromkeys(
            intelligence.rationale
        )
    )

    warnings = tuple(
        dict.fromkeys(
            intelligence.warnings
        )
    )

    return DatasetAssessment(
        intelligence=intelligence,
        requirements=requirements,
        dataset=dataset,
        source=source,
        rationale=rationale,
        warnings=warnings,
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/dataset.py
# RESEARCH DATASET MANAGEMENT — PART 3
# RESULT + CONTRACT + ADVANCEMENT GATE
# ============================================================


# ============================================================
# ACTION / CONTRACT STATES
# ============================================================

class DatasetActionState(str, Enum):
    NONE = "NONE"
    ADVANCE = "ADVANCE"
    REVIEW = "REVIEW"
    HOLD = "HOLD"
    INVALIDATE = "INVALIDATE"
    ARCHIVE = "ARCHIVE"


class DatasetContractState(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


# ============================================================
# DATASET ACTION
# ============================================================

@dataclass(frozen=True)
class DatasetAction:
    action: DatasetDisposition
    dataset_id: str
    reason: str
    source: str = DATASET_MANAGER_ENGINE


# ============================================================
# RESULT
# ============================================================

@dataclass(frozen=True)
class DatasetResult:
    request_id: str
    result_id: str

    status: DatasetStatus
    dataset_state: DatasetStatus

    consistency: DatasetConsistency
    data_state: DatasetDataState
    disposition: DatasetDisposition
    action_state: DatasetActionState

    dataset: Optional[DatasetReference]
    source: Optional[DatasetSourceReference]

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.request_id
            and self.result_id
            and self.consistency
            and self.data_state
        )

    @property
    def requires_review(self) -> bool:
        return self.disposition == DatasetDisposition.REVIEW

    @property
    def requires_hold(self) -> bool:
        return self.disposition == DatasetDisposition.HOLD

    @property
    def requires_invalidation(self) -> bool:
        return self.disposition == DatasetDisposition.INVALIDATE

    @property
    def can_advance(self) -> bool:
        return bool(
            self.is_valid
            and self.status == DatasetStatus.READY
            and self.dataset_state == DatasetStatus.READY
            and self.consistency == DatasetConsistency.CONSISTENT
            and self.data_state == DatasetDataState.COMPLETE
            and self.disposition == DatasetDisposition.ADVANCE
            and self.action_state == DatasetActionState.ADVANCE
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# CONTRACT
# ============================================================

@dataclass(frozen=True)
class DatasetContract:
    dataset_id: str
    request_id: str

    state: DatasetContractState

    result: DatasetResult

    action_state: DatasetActionState

    rationale: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_valid(self) -> bool:
        return bool(
            self.dataset_id
            and self.request_id
            and self.result is not None
            and self.result.is_valid
            and self.state == DatasetContractState.VALID
        )

    @property
    def is_action_request(self) -> bool:
        return False


# ============================================================
# ACTION STATE
# ============================================================

def _ds_action_state(
    disposition: DatasetDisposition,
) -> DatasetActionState:

    mapping = {
        DatasetDisposition.ADVANCE:
            DatasetActionState.ADVANCE,
        DatasetDisposition.REVIEW:
            DatasetActionState.REVIEW,
        DatasetDisposition.HOLD:
            DatasetActionState.HOLD,
        DatasetDisposition.INVALIDATE:
            DatasetActionState.INVALIDATE,
        DatasetDisposition.ARCHIVE:
            DatasetActionState.ARCHIVE,
    }

    return mapping.get(
        disposition,
        DatasetActionState.NONE,
    )


# ============================================================
# RESULT STATUS
# ============================================================

def _ds_result_status(
    intelligence: DatasetIntelligence,
) -> DatasetStatus:

    if (
        intelligence.consistency
        == DatasetConsistency.CONFLICTING
    ):
        return DatasetStatus.INVALID

    if (
        intelligence.data_state
        == DatasetDataState.MISSING
    ):
        return DatasetStatus.INVALID

    if _ds_status_is_invalid(
        intelligence.status.value
    ):
        return DatasetStatus.INVALID

    return intelligence.status


# ============================================================
# RESULT BUILDER
# ============================================================

def build_dataset_result(
    request: DatasetRequest,
    assessment: DatasetAssessment,
) -> DatasetResult:

    intelligence = assessment.intelligence

    status = _ds_result_status(
        intelligence
    )

    action_state = _ds_action_state(
        intelligence.disposition
    )

    rationale = list(
        assessment.rationale
    )

    warnings = list(
        assessment.warnings
    )

    if intelligence.consistency == DatasetConsistency.CONFLICTING:
        rationale.append(
            "Dataset advancement withheld because consistency is conflicting."
        )

    if intelligence.data_state != DatasetDataState.COMPLETE:
        warnings.append(
            "Dataset is not complete for controlled advancement."
        )

    if intelligence.disposition == DatasetDisposition.ADVANCE:
        rationale.append(
            "Dataset satisfies the current controlled advancement gate."
        )

    return DatasetResult(
        request_id=request.request_id,
        result_id=str(uuid4()),
        status=status,
        dataset_state=intelligence.status,
        consistency=intelligence.consistency,
        data_state=intelligence.data_state,
        disposition=intelligence.disposition,
        action_state=action_state,
        dataset=assessment.dataset,
        source=assessment.source,
        rationale=tuple(
            dict.fromkeys(rationale)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# CONTRACT STATE
# ============================================================

def _ds_contract_state(
    result: DatasetResult,
) -> DatasetContractState:

    if not result.is_valid:
        return DatasetContractState.INVALID

    if (
        result.consistency
        == DatasetConsistency.CONFLICTING
    ):
        return DatasetContractState.BLOCKED

    if (
        result.data_state
        == DatasetDataState.MISSING
    ):
        return DatasetContractState.INCOMPLETE

    if (
        result.data_state
        == DatasetDataState.PARTIAL
    ):
        return DatasetContractState.INCOMPLETE

    if result.status == DatasetStatus.INVALID:
        return DatasetContractState.INVALID

    if result.disposition == DatasetDisposition.INVALIDATE:
        return DatasetContractState.BLOCKED

    return DatasetContractState.VALID


# ============================================================
# CONTRACT BUILDER
# ============================================================

def build_dataset_contract(
    request: DatasetRequest,
    result: DatasetResult,
) -> DatasetContract:

    state = _ds_contract_state(
        result
    )

    dataset_id = ""

    if result.dataset is not None:
        dataset_id = result.dataset.dataset_id

    warnings = list(
        result.warnings
    )

    if state == DatasetContractState.BLOCKED:
        warnings.append(
            "Dataset contract is blocked."
        )

    if state == DatasetContractState.INCOMPLETE:
        warnings.append(
            "Dataset contract is incomplete."
        )

    if state == DatasetContractState.INVALID:
        warnings.append(
            "Dataset contract is invalid."
        )

    return DatasetContract(
        dataset_id=dataset_id,
        request_id=request.request_id,
        state=state,
        result=result,
        action_state=result.action_state,
        rationale=result.rationale,
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# SAFE ADVANCEMENT GATE
# ============================================================

def is_dataset_safe_to_advance(
    contract: DatasetContract,
) -> bool:
    """
    Controlled research advancement gate.

    A dataset may advance only when:
        - contract is valid
        - result is valid
        - no action request exists
        - consistency is consistent
        - data state is complete
        - dataset explicitly reports READY
        - disposition is ADVANCE
        - action state is ADVANCE

    No implicit promotion is allowed.
    """

    if not contract.is_valid:
        return False

    if contract.is_action_request:
        return False

    result = contract.result

    if not result.is_valid:
        return False

    if result.consistency != DatasetConsistency.CONSISTENT:
        return False

    if result.data_state != DatasetDataState.COMPLETE:
        return False

    if result.status != DatasetStatus.READY:
        return False

    if result.dataset_state != DatasetStatus.READY:
        return False

    if result.disposition != DatasetDisposition.ADVANCE:
        return False

    if result.action_state != DatasetActionState.ADVANCE:
        return False

    return True


# ============================================================
# RESULT VALIDATION
# ============================================================

def validate_dataset_result(
    result: DatasetResult,
) -> DatasetContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not result.request_id:
        errors.append("Missing request_id.")

    if not result.result_id:
        errors.append("Missing result_id.")

    if result.dataset is None:
        errors.append("Missing dataset reference.")

    if result.consistency is None:
        errors.append("Missing dataset consistency.")

    if result.data_state is None:
        errors.append("Missing dataset data state.")

    if result.is_action_request:
        errors.append(
            "Dataset result must not be an action request."
        )

    if result.consistency == DatasetConsistency.CONFLICTING:
        warnings.append(
            "Dataset consistency is conflicting."
        )

    if result.data_state == DatasetDataState.MISSING:
        warnings.append(
            "Dataset data is missing."
        )

    if result.data_state == DatasetDataState.PARTIAL:
        warnings.append(
            "Dataset data is partial."
        )

    if result.status == DatasetStatus.INVALID:
        warnings.append(
            "Dataset status is INVALID."
        )

    if result.disposition == DatasetDisposition.HOLD:
        warnings.append(
            "Dataset advancement is on HOLD."
        )

    if result.disposition == DatasetDisposition.INVALIDATE:
        warnings.append(
            "Dataset has been marked for invalidation."
        )

    status = (
        DatasetContractStatus.VALID
        if not errors
        else DatasetContractStatus.INVALID
    )

    return DatasetContractValidation(
        status=status,
        errors=tuple(
            dict.fromkeys(errors)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/dataset.py
# RESEARCH DATASET MANAGEMENT — PART 4
# ENGINE + LIFECYCLE
# ============================================================


class DatasetManagerEngine:
    """
    Research Dataset Management Engine.

    Flow:
        Dataset Request
            ↓
        Contract Validation
            ↓
        Dataset Assessment
            ↓
        Dataset Result
            ↓
        Dataset Contract
            ↓
        Controlled Dataset Advancement

    Boundaries:
        - does not invent dataset content
        - does not invent research formulas
        - does not modify source data
        - does not create research conclusions
        - does not execute trades
        - does not create broker orders
        - does not create CAS authorization
        - does not override D13 or Risk
    """

    ENGINE_NAME = DATASET_MANAGER_ENGINE
    ENGINE_VERSION = DATASET_MANAGER_VERSION

    def validate_request(
        self,
        request: DatasetRequest,
    ) -> DatasetContractValidation:
        return validate_dataset_request(request)

    def _invalid_contract(
        self,
        request: DatasetRequest,
        errors: tuple[str, ...],
    ) -> DatasetContract:

        now = datetime.now(timezone.utc)

        result = DatasetResult(
            request_id=request.request_id,
            result_id=str(uuid4()),
            status=DatasetStatus.INVALID,
            dataset_state=DatasetStatus.INVALID,
            consistency=DatasetConsistency.INSUFFICIENT,
            data_state=DatasetDataState.MISSING,
            disposition=DatasetDisposition.HOLD,
            action_state=DatasetActionState.NONE,
            dataset=None,
            source=None,
            rationale=("Dataset request validation failed.",),
            warnings=errors,
            created_at=now,
        )

        return DatasetContract(
            dataset_id="INVALID",
            request_id=request.request_id,
            state=DatasetContractState.INVALID,
            result=result,
            action_state=DatasetActionState.NONE,
            rationale=("Invalid dataset contract.",),
            warnings=errors,
            created_at=now,
        )

    def process(
        self,
        request: DatasetRequest,
    ) -> DatasetContract:
        """
        Full dataset lifecycle.

        Fail-closed:
            invalid or incomplete datasets never become
            advanceable through implicit promotion.
        """
        try:
            validation = self.validate_request(request)

            if not validation.is_valid:
                return self._invalid_contract(
                    request,
                    validation.errors,
                )

            assessment = build_dataset_assessment(
                request
            )

            result = build_dataset_result(
                request,
                assessment,
            )

            result_validation = validate_dataset_result(
                result
            )

            if not result_validation.is_valid:
                warnings = tuple(
                    dict.fromkeys(
                        result.warnings
                        + result_validation.errors
                    )
                )

                result = DatasetResult(
                    request_id=result.request_id,
                    result_id=result.result_id,
                    status=DatasetStatus.INVALID,
                    dataset_state=DatasetStatus.INVALID,
                    consistency=result.consistency,
                    data_state=result.data_state,
                    disposition=DatasetDisposition.HOLD,
                    action_state=DatasetActionState.NONE,
                    dataset=result.dataset,
                    source=result.source,
                    rationale=(
                        result.rationale
                        + (
                            "Dataset result validation failed.",
                        )
                    ),
                    warnings=warnings,
                    created_at=result.created_at,
                )

            return build_dataset_contract(
                request,
                result,
            )

        except Exception as exc:
            return self._invalid_contract(
                request,
                (f"Dataset processing failed: {exc}",),
            )

    def evaluate(
        self,
        request: DatasetRequest,
    ) -> DatasetAssessment:
        """
        Read-only dataset assessment.

        No mutation or automatic promotion.
        """
        validation = self.validate_request(request)

        if not validation.is_valid:
            requirements = DatasetRequirements(
                dataset_available=False,
                dataset_id_available=False,
                name_available=False,
                type_available=False,
                status_available=False,
                source_available=False,
                schema_available=False,
                provenance_available=False,
                version_available=False,
                priority_available=False,
            )

            intelligence = DatasetIntelligence(
                consistency=DatasetConsistency.INSUFFICIENT,
                data_state=DatasetDataState.MISSING,
                status=DatasetStatus.INVALID,
                dataset_type=request.dataset_type,
                priority=request.priority,
                disposition=DatasetDisposition.HOLD,
                dataset_id="",
                name="",
                source_id="",
                schema_id="",
                provenance_id="",
                version="",
                rationale=("Invalid dataset request.",),
                warnings=validation.errors,
                source=DATASET_MANAGER_ENGINE,
            )

            return DatasetAssessment(
                intelligence=intelligence,
                requirements=requirements,
                dataset=None,
                source=None,
                rationale=validation.errors,
                warnings=validation.errors,
            )

        return build_dataset_assessment(request)

    def is_ready(
        self,
        contract: DatasetContract,
    ) -> bool:
        return contract.is_valid

    def can_advance(
        self,
        contract: DatasetContract,
    ) -> bool:
        return is_dataset_safe_to_advance(contract)

    def dataset_status(
        self,
        contract: DatasetContract,
    ) -> DatasetStatus:
        return contract.result.status

    def dataset_disposition(
        self,
        contract: DatasetContract,
    ) -> DatasetDisposition:
        return contract.result.disposition

    def audit_summary(
        self,
        contract: DatasetContract,
    ) -> dict[str, Any]:

        result = contract.result

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,

            "dataset_id": contract.dataset_id,
            "request_id": contract.request_id,

            "contract_state": contract.state.value,
            "contract_valid": contract.is_valid,
            "result_valid": result.is_valid,

            "status": result.status.value,
            "dataset_state": result.dataset_state.value,
            "consistency": result.consistency.value,
            "data_state": result.data_state.value,
            "disposition": result.disposition.value,
            "action_state": result.action_state.value,

            "can_advance": result.can_advance,
            "safe_to_advance": is_dataset_safe_to_advance(
                contract
            ),

            # Hard research safety boundaries
            "dataset_mutated": False,
            "source_modified": False,
            "research_conclusion_created": False,
            "execution_created": False,
            "order_created": False,
            "authorization_created": False,
            "d13_overridden": False,
            "risk_overridden": False,
            "cas_overridden": False,
        }


# ============================================================
# PUBLIC ENGINE
# ============================================================

dataset_manager_engine = DatasetManagerEngine()


# ============================================================
# PUBLIC API
# ============================================================

def manage_dataset(
    request: DatasetRequest,
) -> DatasetContract:
    return dataset_manager_engine.process(request)


def evaluate_dataset(
    request: DatasetRequest,
) -> DatasetAssessment:
    return dataset_manager_engine.evaluate(request)


def dataset_ready(
    contract: DatasetContract,
) -> bool:
    return dataset_manager_engine.is_ready(contract)


def dataset_can_advance(
    contract: DatasetContract,
) -> bool:
    return dataset_manager_engine.can_advance(contract)


def dataset_status(
    contract: DatasetContract,
) -> DatasetStatus:
    return dataset_manager_engine.dataset_status(contract)


def dataset_disposition(
    contract: DatasetContract,
) -> DatasetDisposition:
    return dataset_manager_engine.dataset_disposition(contract)


def dataset_audit(
    contract: DatasetContract,
) -> dict[str, Any]:
    return dataset_manager_engine.audit_summary(contract)


def dataset_health_check() -> dict[str, Any]:
    return {
        "engine": DATASET_MANAGER_ENGINE,
        "version": DATASET_MANAGER_VERSION,
        "status": "HEALTHY",

        "contract_layer": True,
        "assessment_layer": True,
        "result_layer": True,
        "advancement_gate": True,
        "fail_closed": True,

        "dataset_mutated": False,
        "source_modified": False,
        "research_conclusion_created": False,
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,

        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,
    }


def run_dataset_manager_health_check() -> dict[str, Any]:
    return dataset_health_check()


def get_dataset_manager_engine_info() -> dict[str, Any]:
    return {
        "engine": DATASET_MANAGER_ENGINE,
        "version": DATASET_MANAGER_VERSION,
        "role": "Research Dataset Lifecycle Management",
        "authority": "Research Dataset Lifecycle",

        "supports": (
            "dataset registration",
            "dataset assessment",
            "dataset validation",
            "dataset readiness",
            "controlled dataset advancement",
        ),

        "does_not_support": (
            "dataset mutation",
            "research conclusion generation",
            "trade execution",
            "order creation",
            "CAS authorization",
            "D13 override",
            "Risk override",
        ),
    }


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

DatasetManager = DatasetManagerEngine
# ============================================================
# ROBOMLM_PLUS
# app/intelligence/research/dataset.py
# RESEARCH DATASET MANAGEMENT — PART 5
# SERIALIZATION + INTEGRITY + EXPORTS
# ============================================================


# ============================================================
# SERIALIZATION HELPERS
# ============================================================

def _ds_enum_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    return value


def _ds_safe_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}

    if isinstance(value, Mapping):
        return dict(value)

    if hasattr(value, "to_dict"):
        try:
            result = value.to_dict()
            return dict(result) if isinstance(result, Mapping) else {}
        except Exception:
            return {}

    if hasattr(value, "__dict__"):
        try:
            return dict(value.__dict__)
        except Exception:
            return {}

    return {}


def _ds_reference_to_dict(
    reference: Any,
) -> dict[str, Any]:

    if reference is None:
        return {}

    if hasattr(reference, "__dataclass_fields__"):
        return {
            key: _ds_enum_value(value)
            for key, value in reference.__dict__.items()
        }

    return _ds_safe_dict(reference)


# ============================================================
# RESULT SERIALIZATION
# ============================================================

def dataset_result_to_dict(
    result: DatasetResult,
) -> dict[str, Any]:
    """
    Stable external representation of DatasetResult.
    """

    return {
        "request_id": result.request_id,
        "result_id": result.result_id,

        "status": _ds_enum_value(result.status),
        "dataset_state": _ds_enum_value(
            result.dataset_state
        ),
        "consistency": _ds_enum_value(
            result.consistency
        ),
        "data_state": _ds_enum_value(
            result.data_state
        ),
        "disposition": _ds_enum_value(
            result.disposition
        ),
        "action_state": _ds_enum_value(
            result.action_state
        ),

        "dataset": _ds_reference_to_dict(
            result.dataset
        ),
        "source": _ds_reference_to_dict(
            result.source
        ),

        "rationale": list(result.rationale),
        "warnings": list(result.warnings),

        "created_at": result.created_at.isoformat(),

        "is_valid": result.is_valid,
        "requires_review": result.requires_review,
        "requires_hold": result.requires_hold,
        "requires_invalidation": (
            result.requires_invalidation
        ),
        "can_advance": result.can_advance,
        "is_action_request": result.is_action_request,
    }


# ============================================================
# CONTRACT SERIALIZATION
# ============================================================

def dataset_manager_to_dict(
    contract: DatasetContract,
) -> dict[str, Any]:
    """
    Stable external representation of DatasetContract.
    """

    return {
        "engine": DATASET_MANAGER_ENGINE,
        "version": DATASET_MANAGER_VERSION,

        "dataset_id": contract.dataset_id,
        "request_id": contract.request_id,

        "state": _ds_enum_value(
            contract.state
        ),
        "action_state": _ds_enum_value(
            contract.action_state
        ),

        "rationale": list(contract.rationale),
        "warnings": list(contract.warnings),

        "created_at": contract.created_at.isoformat(),

        "result": dataset_result_to_dict(
            contract.result
        ),

        "contract_valid": contract.is_valid,
        "safe_to_advance": (
            is_dataset_safe_to_advance(contract)
        ),

        # Hard safety invariants
        "dataset_mutated": False,
        "source_modified": False,
        "research_conclusion_created": False,
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,
        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,
    }


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_dataset_contract(
    contract: DatasetContract,
) -> DatasetContractValidation:

    errors: list[str] = []
    warnings: list[str] = []

    if not contract.dataset_id:
        errors.append(
            "Missing dataset_id."
        )

    if not contract.request_id:
        errors.append(
            "Missing request_id."
        )

    if contract.result is None:
        errors.append(
            "Missing dataset result."
        )
    else:
        result_validation = validate_dataset_result(
            contract.result
        )

        errors.extend(
            result_validation.errors
        )
        warnings.extend(
            result_validation.warnings
        )

        if contract.result.request_id != contract.request_id:
            errors.append(
                "Contract/result request_id mismatch."
            )

        if contract.result.dataset is not None:
            result_dataset_id = (
                contract.result.dataset.dataset_id
            )

            if (
                result_dataset_id
                and contract.dataset_id
                and result_dataset_id != contract.dataset_id
            ):
                errors.append(
                    "Contract/result dataset_id mismatch."
                )

        if contract.result.is_action_request:
            errors.append(
                "Dataset result must not be an action request."
            )

    if contract.is_action_request:
        errors.append(
            "Dataset contract must not be an action request."
        )

    if contract.state == DatasetContractState.INVALID:
        warnings.append(
            "Dataset contract is INVALID."
        )

    if contract.state == DatasetContractState.BLOCKED:
        warnings.append(
            "Dataset advancement is BLOCKED."
        )

    if contract.state == DatasetContractState.INCOMPLETE:
        warnings.append(
            "Dataset contract is INCOMPLETE."
        )

    status = (
        DatasetContractStatus.VALID
        if not errors
        else DatasetContractStatus.INVALID
    )

    return DatasetContractValidation(
        status=status,
        errors=tuple(
            dict.fromkeys(errors)
        ),
        warnings=tuple(
            dict.fromkeys(warnings)
        ),
    )


# ============================================================
# FINAL INTEGRITY CHECK
# ============================================================

def dataset_manager_integrity_check(
    contract: DatasetContract,
) -> dict[str, Any]:
    """
    Final dataset lifecycle integrity audit.

    This function only evaluates state.
    It does not mutate or promote the dataset.
    """

    validation = validate_dataset_contract(
        contract
    )

    safe_to_advance = (
        is_dataset_safe_to_advance(contract)
    )

    return {
        "engine": DATASET_MANAGER_ENGINE,
        "version": DATASET_MANAGER_VERSION,

        "dataset_id": contract.dataset_id,
        "request_id": contract.request_id,

        "contract_state": _ds_enum_value(
            contract.state
        ),
        "contract_valid": contract.is_valid,

        "validation_status": _ds_enum_value(
            validation.status
        ),

        "errors": list(validation.errors),
        "warnings": list(validation.warnings),

        "dataset_status": _ds_enum_value(
            contract.result.status
        ),
        "dataset_state": _ds_enum_value(
            contract.result.dataset_state
        ),
        "consistency": _ds_enum_value(
            contract.result.consistency
        ),
        "data_state": _ds_enum_value(
            contract.result.data_state
        ),
        "disposition": _ds_enum_value(
            contract.result.disposition
        ),
        "action_state": _ds_enum_value(
            contract.result.action_state
        ),

        "can_advance": contract.result.can_advance,
        "safe_to_advance": safe_to_advance,

        # Research safety
        "dataset_mutated": False,
        "source_modified": False,
        "research_conclusion_created": False,

        # Execution safety
        "execution_created": False,
        "order_created": False,
        "authorization_created": False,

        # Authority protection
        "d13_overridden": False,
        "risk_overridden": False,
        "cas_overridden": False,

        "integrity_pass": bool(
            validation.is_valid
            and not contract.is_action_request
        ),
    }


def verify_dataset_manager_integrity(
    contract: DatasetContract,
) -> bool:
    return bool(
        dataset_manager_integrity_check(
            contract
        )["integrity_pass"]
    )


# ============================================================
# FINAL HEALTH CHECK
# ============================================================

def run_dataset_manager_health_check() -> dict[str, Any]:
    health = dataset_health_check()

    health.update(
        {
            "serialization_layer": True,
            "integrity_layer": True,
            "lifecycle_engine": True,
            "safe_advance_gate": True,
        }
    )

    return health


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Constants
    "DATASET_MANAGER_ENGINE",
    "DATASET_MANAGER_VERSION",

    # Enums
    "DatasetStatus",
    "DatasetType",
    "DatasetPriority",
    "DatasetContractStatus",
    "DatasetConsistency",
    "DatasetDataState",
    "DatasetDisposition",
    "DatasetActionState",
    "DatasetContractState",

    # Contracts / References
    "DatasetRequest",
    "DatasetReference",
    "DatasetSourceReference",
    "DatasetContractValidation",
    "DatasetRequirements",
    "DatasetIntelligence",
    "DatasetAssessment",
    "DatasetAction",
    "DatasetResult",
    "DatasetContract",

    # Builders
    "build_dataset_reference",
    "build_dataset_source_reference",
    "validate_dataset_request",
    "evaluate_dataset_requirements",
    "evaluate_dataset_data_state",
    "evaluate_dataset_consistency",
    "evaluate_dataset_disposition",
    "build_dataset_intelligence",
    "build_dataset_assessment",
    "build_dataset_result",
    "build_dataset_contract",
    "is_dataset_safe_to_advance",
    "validate_dataset_result",
    "validate_dataset_contract",

    # Engine
    "DatasetManagerEngine",
    "DatasetManager",
    "dataset_manager_engine",

    # Public API
    "manage_dataset",
    "evaluate_dataset",
    "dataset_ready",
    "dataset_can_advance",
    "dataset_status",
    "dataset_disposition",
    "dataset_audit",
    "dataset_health_check",
    "run_dataset_manager_health_check",
    "get_dataset_manager_engine_info",

    # Serialization
    "dataset_result_to_dict",
    "dataset_manager_to_dict",

    # Integrity
    "dataset_manager_integrity_check",
    "verify_dataset_manager_integrity",
]
def run_dataset_manager_integrity_check() -> dict[str, Any]:
    """
    Backward compatibility wrapper.

    __init__.py expects this symbol.
    Route to the current integrity implementation.
    """
    return dataset_manager_integrity_check()