# ============================================================
# ROBOMLM CAS AUDIT
# Part 1: Audit Contracts / Metadata / Core Models
# ============================================================

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple


# ============================================================
# ENGINE INFO
# ============================================================

CAS_AUDIT_ENGINE = "ROBOMLM_CAS_AUDIT"
CAS_AUDIT_VERSION = "1.0"


# ============================================================
# HELPERS
# ============================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def safe_text(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# AUDIT SEVERITY
# ============================================================

class CASAuditSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ============================================================
# AUDIT EVENT TYPE
# ============================================================

class CASAuditEventType(str, Enum):
    REQUEST_CREATED = "REQUEST_CREATED"

    GATE_STARTED = "GATE_STARTED"
    GATE_COMPLETED = "GATE_COMPLETED"

    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    RESTRICTED = "RESTRICTED"
    BLOCKED = "BLOCKED"

    AUTHORIZED = "AUTHORIZED"
    CONTRACT_CREATED = "CONTRACT_CREATED"

    AUDIT_CREATED = "AUDIT_CREATED"
    ERROR = "ERROR"


# ============================================================
# AUDIT ENTRY
# ============================================================

@dataclass(frozen=True)
class CASAuditEntry:
    """
    Immutable audit event.

    Audit records what happened.
    Audit does not change CAS state.
    """

    event_type: CASAuditEventType
    severity: CASAuditSeverity

    message: str

    request_id: Optional[str] = None
    decision_id: Optional[str] = None

    gate: Optional[str] = None

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    timestamp: datetime = field(
        default_factory=utc_now
    )


# ============================================================
# AUDIT SUMMARY
# ============================================================

@dataclass(frozen=True)
class CASAuditSummary:
    total_events: int

    info_events: int
    warning_events: int
    critical_events: int

    blocked_events: int
    restricted_events: int
    review_events: int

    first_event_at: Optional[datetime] = None
    last_event_at: Optional[datetime] = None


# ============================================================
# AUDIT RECORD
# ============================================================

@dataclass(frozen=True)
class CASAuditRecord:
    """
    Final immutable CAS audit record.

    Mirrors orchestration output.
    Does not redefine CAS contracts.
    """

    audit_id: str

    request_id: Optional[str]
    decision_id: Optional[str]

    status: str
    decision: str

    pathway: str

    allowed: bool
    restricted: bool
    review_required: bool
    blocked: bool

    gates_executed: Tuple[str, ...] = ()

    blocking_gates: Tuple[str, ...] = ()
    review_gates: Tuple[str, ...] = ()

    flags: Tuple[str, ...] = ()
    restrictions: Tuple[str, ...] = ()

    score: Optional[float] = None
    confidence: Optional[float] = None

    reason: str = ""

    entries: Tuple[CASAuditEntry, ...] = ()

    created_at: datetime = field(
        default_factory=utc_now
    )


# ============================================================
# AUDIT VALIDATION
# ============================================================

def validate_audit_entry(
    entry: CASAuditEntry,
) -> bool:

    if not isinstance(
        entry,
        CASAuditEntry,
    ):
        return False

    if not safe_text(entry.message):
        return False

    return True


def validate_audit_record(
    record: CASAuditRecord,
) -> bool:

    if not isinstance(
        record,
        CASAuditRecord,
    ):
        return False

    if not safe_text(record.audit_id):
        return False

    for entry in record.entries:
        if not validate_audit_entry(entry):
            return False

    return True


# ============================================================
# ENTRY BUILDERS
# ============================================================

def create_audit_entry(
    event_type: CASAuditEventType,
    severity: CASAuditSeverity,
    message: str,
    *,
    request_id: Optional[str] = None,
    decision_id: Optional[str] = None,
    gate: Optional[str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> CASAuditEntry:

    return CASAuditEntry(
        event_type=event_type,
        severity=severity,
        message=message,

        request_id=request_id,
        decision_id=decision_id,

        gate=gate,

        metadata=dict(metadata or {}),
    )


# ============================================================
# EMPTY SUMMARY
# ============================================================

def empty_audit_summary() -> CASAuditSummary:

    return CASAuditSummary(
        total_events=0,

        info_events=0,
        warning_events=0,
        critical_events=0,

        blocked_events=0,
        restricted_events=0,
        review_events=0,

        first_event_at=None,
        last_event_at=None,
    )
# ============================================================
# ROBOMLM CAS AUDIT
# Part 2: Collector / Timeline / Summary Engine
# ============================================================


# ============================================================
# AUDIT COLLECTOR
# ============================================================

class CASAuditCollector:
    """
    In-memory immutable-style audit collector.

    Audit records events.
    Audit does not modify CAS outcomes.
    """

    def __init__(self) -> None:

        self._entries: list[
            CASAuditEntry
        ] = []

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def empty(self) -> bool:
        return len(self._entries) == 0

    def clear(self) -> None:
        self._entries.clear()

    def add(
        self,
        entry: CASAuditEntry,
    ) -> CASAuditEntry:

        if not validate_audit_entry(
            entry
        ):
            raise ValueError(
                "Invalid CASAuditEntry."
            )

        self._entries.append(entry)

        return entry

    def extend(
        self,
        entries: Tuple[
            CASAuditEntry,
            ...
        ],
    ) -> None:

        for entry in entries:
            self.add(entry)

    def entries(
        self,
    ) -> Tuple[
        CASAuditEntry,
        ...
    ]:

        return tuple(
            self._entries
        )

    def last(
        self,
    ) -> Optional[
        CASAuditEntry
    ]:

        if not self._entries:
            return None

        return self._entries[-1]


# ============================================================
# ENTRY FILTERS
# ============================================================

def filter_entries_by_severity(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
    severity: CASAuditSeverity,
) -> Tuple[
    CASAuditEntry,
    ...
]:

    return tuple(
        entry
        for entry in entries
        if entry.severity == severity
    )


def filter_entries_by_event(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
    event_type: CASAuditEventType,
) -> Tuple[
    CASAuditEntry,
    ...
]:

    return tuple(
        entry
        for entry in entries
        if entry.event_type
        == event_type
    )


def filter_entries_by_gate(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
    gate: str,
) -> Tuple[
    CASAuditEntry,
    ...
]:

    gate = safe_text(gate)

    return tuple(
        entry
        for entry in entries
        if safe_text(
            entry.gate
        ) == gate
    )


# ============================================================
# TIMELINE HELPERS
# ============================================================

def sort_audit_entries(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> Tuple[
    CASAuditEntry,
    ...
]:

    return tuple(
        sorted(
            entries,
            key=lambda x: x.timestamp,
        )
    )


def first_audit_event(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> Optional[
    CASAuditEntry
]:

    ordered = sort_audit_entries(
        entries
    )

    if not ordered:
        return None

    return ordered[0]


def last_audit_event(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> Optional[
    CASAuditEntry
]:

    ordered = sort_audit_entries(
        entries
    )

    if not ordered:
        return None

    return ordered[-1]


# ============================================================
# EVENT COUNTERS
# ============================================================

def count_info_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_severity(
            entries,
            CASAuditSeverity.INFO,
        )
    )


def count_warning_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_severity(
            entries,
            CASAuditSeverity.WARNING,
        )
    )


def count_critical_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_severity(
            entries,
            CASAuditSeverity.CRITICAL,
        )
    )


# ============================================================
# SPECIAL EVENT COUNTERS
# ============================================================

def count_blocked_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_event(
            entries,
            CASAuditEventType.BLOCKED,
        )
    )


def count_restricted_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_event(
            entries,
            CASAuditEventType.RESTRICTED,
        )
    )


def count_review_events(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> int:

    return len(
        filter_entries_by_event(
            entries,
            CASAuditEventType.REVIEW_REQUIRED,
        )
    )


# ============================================================
# AUDIT SUMMARY
# ============================================================

def build_audit_summary(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> CASAuditSummary:

    first_event = first_audit_event(
        entries
    )

    last_event = last_audit_event(
        entries
    )

    return CASAuditSummary(
        total_events=len(entries),

        info_events=
            count_info_events(
                entries
            ),

        warning_events=
            count_warning_events(
                entries
            ),

        critical_events=
            count_critical_events(
                entries
            ),

        blocked_events=
            count_blocked_events(
                entries
            ),

        restricted_events=
            count_restricted_events(
                entries
            ),

        review_events=
            count_review_events(
                entries
            ),

        first_event_at=(
            first_event.timestamp
            if first_event
            else None
        ),

        last_event_at=(
            last_event.timestamp
            if last_event
            else None
        ),
    )


# ============================================================
# SUMMARY VALIDATION
# ============================================================

def validate_audit_summary(
    summary: CASAuditSummary,
) -> bool:

    if not isinstance(
        summary,
        CASAuditSummary,
    ):
        return False

    if summary.total_events < 0:
        return False

    if summary.info_events < 0:
        return False

    if summary.warning_events < 0:
        return False

    if summary.critical_events < 0:
        return False

    return True


# ============================================================
# QUICK STATISTICS
# ============================================================

def audit_statistics(
    entries: Tuple[
        CASAuditEntry,
        ...
    ],
) -> Dict[str, Any]:

    summary = build_audit_summary(
        entries
    )

    return {
        "total_events":
            summary.total_events,

        "info_events":
            summary.info_events,

        "warning_events":
            summary.warning_events,

        "critical_events":
            summary.critical_events,

        "blocked_events":
            summary.blocked_events,

        "restricted_events":
            summary.restricted_events,

        "review_events":
            summary.review_events,

        "first_event_at":
            summary.first_event_at,

        "last_event_at":
            summary.last_event_at,
    }


# ============================================================
# COLLECTOR FACTORY
# ============================================================

def create_audit_collector(
) -> CASAuditCollector:

    return CASAuditCollector()


# ============================================================
# HEALTH CHECK
# ============================================================

def audit_collector_operational(
    collector: CASAuditCollector,
) -> bool:

    if not isinstance(
        collector,
        CASAuditCollector,
    ):
        return False

    try:
        _ = collector.entries()
        return True
    except Exception:
        return False
# ============================================================
# ROBOMLM CAS AUDIT
# Part 3: CAS Contract Integration / Traceability
# ============================================================


# ============================================================
# CONTRACT EVENT BUILDERS
# ============================================================

def create_request_created_event(
    request_id: Optional[str],
    decision_id: Optional[str],
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.REQUEST_CREATED,

        severity=
            CASAuditSeverity.INFO,

        message=
            "CAS request created.",

        request_id=request_id,
        decision_id=decision_id,
    )


def create_contract_created_event(
    request_id: Optional[str],
    decision_id: Optional[str],
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.CONTRACT_CREATED,

        severity=
            CASAuditSeverity.INFO,

        message=
            "CAS contract created.",

        request_id=request_id,
        decision_id=decision_id,
    )


# ============================================================
# GATE EVENTS
# ============================================================

def create_gate_started_event(
    gate: str,
    request_id: Optional[str],
    decision_id: Optional[str],
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.GATE_STARTED,

        severity=
            CASAuditSeverity.INFO,

        message=
            f"Gate started: {gate}",

        request_id=request_id,
        decision_id=decision_id,
        gate=gate,
    )


def create_gate_completed_event(
    gate_execution: Any,
    request_id: Optional[str],
    decision_id: Optional[str],
) -> CASAuditEntry:

    gate_name = safe_text(
        getattr(
            gate_execution.gate,
            "value",
            gate_execution.gate,
        )
    )

    severity = (
        CASAuditSeverity.INFO
    )

    if getattr(
        gate_execution,
        "review_required",
        False,
    ):
        severity = (
            CASAuditSeverity.WARNING
        )

    if getattr(
        gate_execution,
        "blocked",
        False,
    ):
        severity = (
            CASAuditSeverity.CRITICAL
        )

    return create_audit_entry(
        event_type=
            CASAuditEventType.GATE_COMPLETED,

        severity=severity,

        message=
            f"Gate completed: {gate_name}",

        request_id=request_id,
        decision_id=decision_id,
        gate=gate_name,

        metadata={
            "status":
                getattr(
                    gate_execution,
                    "status",
                    None,
                ),
            "decision":
                getattr(
                    gate_execution,
                    "decision",
                    None,
                ),
            "allowed":
                getattr(
                    gate_execution,
                    "allowed",
                    False,
                ),
            "blocked":
                getattr(
                    gate_execution,
                    "blocked",
                    False,
                ),
            "review_required":
                getattr(
                    gate_execution,
                    "review_required",
                    False,
                ),
            "restricted":
                getattr(
                    gate_execution,
                    "restricted",
                    False,
                ),
        },
    )


# ============================================================
# FINAL RESULT EVENTS
# ============================================================

def create_blocked_event(
    result: Any,
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.BLOCKED,

        severity=
            CASAuditSeverity.CRITICAL,

        message=
            result.reason,

        request_id=
            result.request_id,

        metadata={
            "blocking_gates":
                list(
                    result.blocking_gates
                )
        },
    )


def create_review_event(
    result: Any,
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.REVIEW_REQUIRED,

        severity=
            CASAuditSeverity.WARNING,

        message=
            result.reason,

        request_id=
            result.request_id,

        metadata={
            "review_gates":
                list(
                    result.review_gates
                )
        },
    )


def create_restricted_event(
    result: Any,
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.RESTRICTED,

        severity=
            CASAuditSeverity.WARNING,

        message=
            result.reason,

        request_id=
            result.request_id,

        metadata={
            "restrictions":
                list(
                    result.restrictions
                )
        },
    )


def create_authorized_event(
    result: Any,
) -> CASAuditEntry:

    return create_audit_entry(
        event_type=
            CASAuditEventType.AUTHORIZED,

        severity=
            CASAuditSeverity.INFO,

        message=
            result.reason,

        request_id=
            result.request_id,
    )


# ============================================================
# RESULT → EVENT
# ============================================================

def create_result_event(
    result: Any,
) -> CASAuditEntry:

    if getattr(
        result,
        "blocked",
        False,
    ):
        return create_blocked_event(
            result
        )

    if getattr(
        result,
        "review_required",
        False,
    ):
        return create_review_event(
            result
        )

    if getattr(
        result,
        "restricted",
        False,
    ):
        return create_restricted_event(
            result
        )

    return create_authorized_event(
        result
    )


# ============================================================
# GATE EXECUTIONS → AUDIT ENTRIES
# ============================================================

def build_gate_audit_entries(
    contract: Any,
) -> Tuple[
    CASAuditEntry,
    ...
]:

    entries = []

    request = contract.request

    request_id = getattr(
        request,
        "request_id",
        None,
    )

    decision_id = getattr(
        request,
        "decision_id",
        None,
    )

    for execution in (
        contract.gate_executions
    ):

        gate_name = safe_text(
            getattr(
                execution.gate,
                "value",
                execution.gate,
            )
        )

        entries.append(
            create_gate_started_event(
                gate_name,
                request_id,
                decision_id,
            )
        )

        entries.append(
            create_gate_completed_event(
                execution,
                request_id,
                decision_id,
            )
        )

    return tuple(entries)


# ============================================================
# CONTRACT → AUDIT ENTRIES
# ============================================================

def build_contract_audit_entries(
    contract: Any,
) -> Tuple[
    CASAuditEntry,
    ...
]:

    entries = []

    request = contract.request

    request_id = getattr(
        request,
        "request_id",
        None,
    )

    decision_id = getattr(
        request,
        "decision_id",
        None,
    )

    entries.append(
        create_request_created_event(
            request_id,
            decision_id,
        )
    )

    entries.extend(
        build_gate_audit_entries(
            contract
        )
    )

    entries.append(
        create_result_event(
            contract.result
        )
    )

    entries.append(
        create_contract_created_event(
            request_id,
            decision_id,
        )
    )

    return tuple(entries)


# ============================================================
# TRACE CHAIN
# ============================================================

def build_trace_chain(
    contract: Any,
) -> Dict[str, Any]:

    result = contract.result

    return {
        "request_id":
            result.request_id,

        "decision":
            safe_text(
                getattr(
                    result.decision,
                    "value",
                    result.decision,
                )
            ),

        "status":
            safe_text(
                getattr(
                    result.status,
                    "value",
                    result.status,
                )
            ),

        "pathway":
            safe_text(
                getattr(
                    result.pathway,
                    "value",
                    result.pathway,
                )
            ),

        "gate_count":
            len(
                contract.gate_executions
            ),

        "gates_executed":
            list(
                result.gates_executed
            ),

        "blocked":
            result.blocked,

        "review_required":
            result.review_required,

        "restricted":
            result.restricted,

        "allowed":
            result.allowed,
    }


# ============================================================
# TRACE VALIDATION
# ============================================================

def validate_trace_chain(
    trace: Mapping[str, Any],
) -> bool:

    if not isinstance(
        trace,
        Mapping,
    ):
        return False

    if not trace.get(
        "decision"
    ):
        return False

    if not trace.get(
        "status"
    ):
        return False

    return True


# ============================================================
# AUDIT COLLECTOR POPULATION
# ============================================================

def populate_collector_from_contract(
    collector: CASAuditCollector,
    contract: Any,
) -> CASAuditCollector:

    entries = (
        build_contract_audit_entries(
            contract
        )
    )

    collector.extend(
        entries
    )

    return collector


# ============================================================
# CONTRACT AUDIT SUMMARY
# ============================================================

def build_contract_audit_summary(
    contract: Any,
) -> CASAuditSummary:

    collector = (
        create_audit_collector()
    )

    populate_collector_from_contract(
        collector,
        contract,
    )

    return build_audit_summary(
        collector.entries()
    )
# ============================================================
# ROBOMLM CAS AUDIT
# Part 4: Audit Record / Serialization / Integrity
# ============================================================


# ============================================================
# AUDIT ID
# ============================================================

def build_audit_id(
    request_id: Optional[str],
) -> str:

    request_part = (
        safe_text(request_id)
        or "UNKNOWN"
    )

    ts = utc_now().strftime(
        "%Y%m%d%H%M%S%f"
    )

    return (
        f"CAS_AUDIT_"
        f"{request_part}_"
        f"{ts}"
    )


# ============================================================
# CONTRACT → AUDIT RECORD
# ============================================================

def build_audit_record(
    contract: Any,
) -> CASAuditRecord:

    result = contract.result

    entries = (
        build_contract_audit_entries(
            contract
        )
    )

    return CASAuditRecord(
        audit_id=build_audit_id(
            result.request_id
        ),

        request_id=
            result.request_id,

        decision_id=
            getattr(
                contract.request,
                "decision_id",
                None,
            ),

        status=safe_text(
            getattr(
                result.status,
                "value",
                result.status,
            )
        ),

        decision=safe_text(
            getattr(
                result.decision,
                "value",
                result.decision,
            )
        ),

        pathway=safe_text(
            getattr(
                result.pathway,
                "value",
                result.pathway,
            )
        ),

        allowed=result.allowed,
        restricted=result.restricted,
        review_required=
            result.review_required,
        blocked=result.blocked,

        gates_executed=
            tuple(
                result.gates_executed
            ),

        blocking_gates=
            tuple(
                result.blocking_gates
            ),

        review_gates=
            tuple(
                result.review_gates
            ),

        flags=tuple(
            result.flags
        ),

        restrictions=tuple(
            result.restrictions
        ),

        score=result.score,
        confidence=
            result.confidence,

        reason=result.reason,

        entries=entries,
    )


# ============================================================
# RECORD VALIDATION
# ============================================================

def validate_audit_record_integrity(
    record: CASAuditRecord,
) -> bool:

    if not validate_audit_record(
        record
    ):
        return False

    if (
        record.allowed
        and record.blocked
    ):
        return False

    if (
        record.allowed
        and record.review_required
    ):
        return False

    if (
        record.blocked
        and record.restricted
    ):
        return False

    return True


# ============================================================
# ENTRY SERIALIZATION
# ============================================================

def audit_entry_to_dict(
    entry: CASAuditEntry,
) -> Dict[str, Any]:

    return {
        "event_type":
            entry.event_type.value,

        "severity":
            entry.severity.value,

        "message":
            entry.message,

        "request_id":
            entry.request_id,

        "decision_id":
            entry.decision_id,

        "gate":
            entry.gate,

        "metadata":
            dict(
                entry.metadata
            ),

        "timestamp":
            entry.timestamp.isoformat(),
    }


# ============================================================
# SUMMARY SERIALIZATION
# ============================================================

def audit_summary_to_dict(
    summary: CASAuditSummary,
) -> Dict[str, Any]:

    return {
        "total_events":
            summary.total_events,

        "info_events":
            summary.info_events,

        "warning_events":
            summary.warning_events,

        "critical_events":
            summary.critical_events,

        "blocked_events":
            summary.blocked_events,

        "restricted_events":
            summary.restricted_events,

        "review_events":
            summary.review_events,

        "first_event_at":
            (
                summary.first_event_at
                .isoformat()
                if summary.first_event_at
                else None
            ),

        "last_event_at":
            (
                summary.last_event_at
                .isoformat()
                if summary.last_event_at
                else None
            ),
    }


# ============================================================
# RECORD SERIALIZATION
# ============================================================

def audit_record_to_dict(
    record: CASAuditRecord,
) -> Dict[str, Any]:

    return {
        "audit_id":
            record.audit_id,

        "request_id":
            record.request_id,

        "decision_id":
            record.decision_id,

        "status":
            record.status,

        "decision":
            record.decision,

        "pathway":
            record.pathway,

        "allowed":
            record.allowed,

        "restricted":
            record.restricted,

        "review_required":
            record.review_required,

        "blocked":
            record.blocked,

        "gates_executed":
            list(
                record.gates_executed
            ),

        "blocking_gates":
            list(
                record.blocking_gates
            ),

        "review_gates":
            list(
                record.review_gates
            ),

        "flags":
            list(
                record.flags
            ),

        "restrictions":
            list(
                record.restrictions
            ),

        "score":
            record.score,

        "confidence":
            record.confidence,

        "reason":
            record.reason,

        "entries": [
            audit_entry_to_dict(
                entry
            )
            for entry
            in record.entries
        ],

        "created_at":
            record.created_at
            .isoformat(),
    }


# ============================================================
# SNAPSHOT
# ============================================================

def build_audit_snapshot(
    contract: Any,
) -> Dict[str, Any]:

    record = (
        build_audit_record(
            contract
        )
    )

    summary = (
        build_contract_audit_summary(
            contract
        )
    )

    trace = (
        build_trace_chain(
            contract
        )
    )

    return {
        "record":
            audit_record_to_dict(
                record
            ),

        "summary":
            audit_summary_to_dict(
                summary
            ),

        "trace":
            trace,
    }


# ============================================================
# AUTHORITY BOUNDARY AUDIT
# ============================================================

def build_authority_boundary_audit(
) -> Dict[str, Any]:

    return {
        "audit_modifies_d13":
            False,

        "audit_overrides_d13":
            False,

        "audit_generates_alpha":
            False,

        "audit_places_orders":
            False,

        "audit_changes_position":
            False,

        "audit_overrides_risk":
            False,

        "audit_bypasses_gate":
            False,

        "audit_is_observer":
            True,
    }


# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_authority_boundary(
    boundary: Mapping[str, Any],
) -> bool:

    if boundary.get(
        "audit_modifies_d13"
    ):
        return False

    if boundary.get(
        "audit_overrides_d13"
    ):
        return False

    if boundary.get(
        "audit_generates_alpha"
    ):
        return False

    if boundary.get(
        "audit_places_orders"
    ):
        return False

    if boundary.get(
        "audit_changes_position"
    ):
        return False

    if boundary.get(
        "audit_overrides_risk"
    ):
        return False

    if boundary.get(
        "audit_bypasses_gate"
    ):
        return False

    return True


# ============================================================
# AUDIT HEALTH
# ============================================================

def audit_health(
    contract: Any,
) -> Dict[str, Any]:

    record = (
        build_audit_record(
            contract
        )
    )

    summary = (
        build_contract_audit_summary(
            contract
        )
    )

    boundary = (
        build_authority_boundary_audit()
    )

    return {
        "record_valid":
            validate_audit_record_integrity(
                record
            ),

        "summary_valid":
            validate_audit_summary(
                summary
            ),

        "authority_valid":
            validate_authority_boundary(
                boundary
            ),

        "trace_valid":
            validate_trace_chain(
                build_trace_chain(
                    contract
                )
            ),
    }


# ============================================================
# IMMUTABLE EXPORT
# ============================================================

def export_audit_snapshot(
    contract: Any,
) -> Dict[str, Any]:

    snapshot = (
        build_audit_snapshot(
            contract
        )
    )

    return dict(snapshot)
# ============================================================
# ROBOMLM CAS AUDIT
# Part 5: Audit Service / Query API / Health / Exports
# ============================================================


# ============================================================
# AUDIT SERVICE
# ============================================================

class CASAuditService:
    """
    Central CAS audit service.

    Stores immutable audit records.
    Does not modify CAS outcomes.
    """

    def __init__(self) -> None:

        self._records: list[
            CASAuditRecord
        ] = []

    # --------------------------------------------------------
    # RECORD MANAGEMENT
    # --------------------------------------------------------

    def add_record(
        self,
        record: CASAuditRecord,
    ) -> CASAuditRecord:

        if not validate_audit_record_integrity(
            record
        ):
            raise ValueError(
                "Invalid CAS audit record."
            )

        self._records.append(
            record
        )

        return record

    def add_contract(
        self,
        contract: Any,
    ) -> CASAuditRecord:

        record = (
            build_audit_record(
                contract
            )
        )

        return self.add_record(
            record
        )

    # --------------------------------------------------------
    # ACCESS
    # --------------------------------------------------------

    def records(
        self,
    ) -> Tuple[
        CASAuditRecord,
        ...
    ]:

        return tuple(
            self._records
        )

    def count(
        self,
    ) -> int:

        return len(
            self._records
        )

    def empty(
        self,
    ) -> bool:

        return (
            len(
                self._records
            ) == 0
        )

    def latest(
        self,
    ) -> Optional[
        CASAuditRecord
    ]:

        if not self._records:
            return None

        return self._records[-1]

    def clear(
        self,
    ) -> None:

        self._records.clear()


# ============================================================
# RECORD SEARCH
# ============================================================

def find_audit_by_id(
    service: CASAuditService,
    audit_id: str,
) -> Optional[
    CASAuditRecord
]:

    audit_id = safe_text(
        audit_id
    )

    for record in service.records():

        if (
            record.audit_id
            == audit_id
        ):
            return record

    return None


def find_audit_by_request(
    service: CASAuditService,
    request_id: str,
) -> Tuple[
    CASAuditRecord,
    ...
]:

    request_id = safe_text(
        request_id
    )

    return tuple(
        record
        for record in service.records()
        if (
            safe_text(
                record.request_id
            )
            == request_id
        )
    )


# ============================================================
# STATUS FILTERS
# ============================================================

def blocked_audits(
    service: CASAuditService,
) -> Tuple[
    CASAuditRecord,
    ...
]:

    return tuple(
        record
        for record in service.records()
        if record.blocked
    )


def restricted_audits(
    service: CASAuditService,
) -> Tuple[
    CASAuditRecord,
    ...
]:

    return tuple(
        record
        for record in service.records()
        if record.restricted
    )


def review_audits(
    service: CASAuditService,
) -> Tuple[
    CASAuditRecord,
    ...
]:

    return tuple(
        record
        for record in service.records()
        if record.review_required
    )


def authorized_audits(
    service: CASAuditService,
) -> Tuple[
    CASAuditRecord,
    ...
]:

    return tuple(
        record
        for record in service.records()
        if (
            record.allowed
            and not record.blocked
            and not record.review_required
        )
    )


# ============================================================
# GLOBAL SUMMARY
# ============================================================

def build_service_summary(
    service: CASAuditService,
) -> Dict[str, Any]:

    records = service.records()

    return {
        "total_records":
            len(records),

        "authorized":
            len(
                authorized_audits(
                    service
                )
            ),

        "blocked":
            len(
                blocked_audits(
                    service
                )
            ),

        "restricted":
            len(
                restricted_audits(
                    service
                )
            ),

        "review":
            len(
                review_audits(
                    service
                )
            ),
    }


# ============================================================
# ENGINE INFO
# ============================================================

def audit_engine_info(
) -> Dict[str, Any]:

    return {
        "engine":
            CAS_AUDIT_ENGINE,

        "version":
            CAS_AUDIT_VERSION,

        "role":
            (
                "CAS forensic "
                "audit subsystem"
            ),

        "immutable_records":
            True,

        "decision_authority":
            False,

        "risk_authority":
            False,

        "execution_authority":
            False,

        "observer_only":
            True,
    }


# ============================================================
# ENGINE HEALTH
# ============================================================

def audit_engine_health(
    service: Optional[
        CASAuditService
    ] = None,
) -> Dict[str, Any]:

    boundary = (
        build_authority_boundary_audit()
    )

    return {
        "engine":
            CAS_AUDIT_ENGINE,

        "version":
            CAS_AUDIT_VERSION,

        "authority_boundary_ok":
            validate_authority_boundary(
                boundary
            ),

        "service_available":
            service is not None,

        "record_count":
            (
                service.count()
                if service
                else 0
            ),

        "healthy":
            validate_authority_boundary(
                boundary
            ),
    }


# ============================================================
# SINGLETON
# ============================================================

_AUDIT_SERVICE: Optional[
    CASAuditService
] = None


def get_audit_service(
) -> CASAuditService:

    global _AUDIT_SERVICE

    if _AUDIT_SERVICE is None:

        _AUDIT_SERVICE = (
            CASAuditService()
        )

    return _AUDIT_SERVICE


# ============================================================
# PUBLIC API
# ============================================================

def audit_contract(
    contract: Any,
) -> CASAuditRecord:

    service = (
        get_audit_service()
    )

    return service.add_contract(
        contract
    )


def audit_record_count(
) -> int:

    return (
        get_audit_service()
        .count()
    )


def latest_audit(
) -> Optional[
    CASAuditRecord
]:

    return (
        get_audit_service()
        .latest()
    )


def audit_summary(
) -> Dict[str, Any]:

    return build_service_summary(
        get_audit_service()
    )


# ============================================================
# OPERATIONAL CHECK
# ============================================================

def audit_operational(
) -> bool:

    try:

        service = (
            get_audit_service()
        )

        return (
            validate_authority_boundary(
                build_authority_boundary_audit()
            )
            and service is not None
        )

    except Exception:
        return False


# ============================================================
# FINAL EXPORTS
# ============================================================

__all__ = [

    # Engine
    "CAS_AUDIT_ENGINE",
    "CAS_AUDIT_VERSION",

    # Enums
    "CASAuditSeverity",
    "CASAuditEventType",

    # Contracts
    "CASAuditEntry",
    "CASAuditSummary",
    "CASAuditRecord",

    # Collector
    "CASAuditCollector",
    "create_audit_collector",

    # Validation
    "validate_audit_entry",
    "validate_audit_record",
    "validate_audit_record_integrity",
    "validate_audit_summary",

    # Builders
    "create_audit_entry",
    "build_audit_summary",
    "build_audit_record",
    "build_audit_snapshot",
    "build_trace_chain",

    # Serialization
    "audit_entry_to_dict",
    "audit_summary_to_dict",
    "audit_record_to_dict",
    "export_audit_snapshot",

    # Authority
    "build_authority_boundary_audit",
    "validate_authority_boundary",

    # Service
    "CASAuditService",
    "get_audit_service",

    # Queries
    "find_audit_by_id",
    "find_audit_by_request",

    # Filters
    "blocked_audits",
    "restricted_audits",
    "review_audits",
    "authorized_audits",

    # Public API
    "audit_contract",
    "audit_record_count",
    "latest_audit",
    "audit_summary",

    # Health
    "audit_engine_info",
    "audit_engine_health",
    "audit_operational",
]