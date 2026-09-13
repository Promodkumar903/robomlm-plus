```python
"""
ROBOMLM_PLUS
============

Memory Page — Part 1
---------------------

Purpose:
    Market Memory / Historical Intelligence UI foundation.

Architectural position:

    DATA
      ↓
    EVIDENCE
      ↓
    MEMORY / HISTORICAL CONTEXT
      ↓
    INTELLIGENCE
      ↓
    D13 DECISION

This page is a presentation / interaction layer.

The Memory UI MUST NOT:
    - issue trading decisions
    - place broker orders
    - modify production formulas
    - directly control intelligence engines
    - bypass D13
    - fabricate historical evidence
    - invent market-memory scores

Canonical principle:
    Memory provides historical context and learned evidence.
    It does not become the final decision authority.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# PAGE CONSTANTS
# ============================================================================

PAGE_TITLE = "Memory"
PAGE_SUBTITLE = "Historical Market Context & Intelligence Memory"

MEMORY_PAGE_VERSION = "1.0.0"
UI_SCHEMA_VERSION = "1.0.0"

DECISION_AUTHORITY = "D13"

PRODUCTION_MUTATION_ALLOWED = False
DIRECT_ENGINE_CONTROL_ALLOWED = False
DIRECT_BROKER_CONTROL_ALLOWED = False


# ============================================================================
# MEMORY STATUS
# ============================================================================

class MemoryStatus(str, Enum):
    """
    Lifecycle state of a memory record.

    This describes memory availability/state only.
    It is NOT a trading decision.
    """

    NEW = "NEW"
    CAPTURED = "CAPTURED"
    VERIFIED = "VERIFIED"
    INDEXED = "INDEXED"
    AVAILABLE = "AVAILABLE"
    STALE = "STALE"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# MEMORY TYPE
# ============================================================================

class MemoryType(str, Enum):
    """
    High-level category of stored market memory.

    These categories are descriptive. They do not contain formulas.
    """

    MARKET_STATE = "MARKET_STATE"
    MARKET_STRUCTURE = "MARKET_STRUCTURE"
    FLOW = "FLOW"
    LIQUIDITY = "LIQUIDITY"
    VOLATILITY = "VOLATILITY"
    PARTICIPATION = "PARTICIPATION"
    DERIVATIVES = "DERIVATIVES"
    RELATIONSHIP = "RELATIONSHIP"
    EVENT = "EVENT"
    SCENARIO = "SCENARIO"
    DECISION_CONTEXT = "DECISION_CONTEXT"
    TRADE_OUTCOME = "TRADE_OUTCOME"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# MEMORY RECORD
# ============================================================================

@dataclass
class MemoryRecord:
    """
    Canonical UI-level representation of a historical memory item.

    IMPORTANT:
        This is a transport/presentation model.

        It does not calculate intelligence.
        It does not create a trade.
        It does not replace canonical domain schemas.
    """

    memory_id: str

    timestamp: datetime

    memory_type: MemoryType = MemoryType.UNKNOWN

    market: str = ""
    instrument: str = ""
    timeframe: str = ""

    title: str = ""
    description: str = ""

    status: MemoryStatus = MemoryStatus.NEW

    source_engine: str = ""
    engine_version: str = ""

    # Historical/contextual references.
    input_reference: Optional[str] = None
    output_reference: Optional[str] = None

    # Evidence/context payload supplied by upstream systems.
    evidence: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    # Historical result / observation.
    outcome: Dict[str, Any] = field(default_factory=dict)

    # Search / classification metadata.
    tags: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable representation of the memory record."""

        return {
            "memory_id": self.memory_id,
            "timestamp": self.timestamp.isoformat(),
            "memory_type": self.memory_type.value,
            "market": self.market,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "source_engine": self.source_engine,
            "engine_version": self.engine_version,
            "input_reference": self.input_reference,
            "output_reference": self.output_reference,
            "evidence": dict(self.evidence),
            "context": dict(self.context),
            "outcome": dict(self.outcome),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# MEMORY QUERY
# ============================================================================

@dataclass
class MemoryQuery:
    """
    Query/filter contract for the Memory UI.

    No intelligence calculation happens here.
    """

    market: Optional[str] = None
    instrument: Optional[str] = None
    timeframe: Optional[str] = None

    memory_type: Optional[MemoryType] = None
    status: Optional[MemoryStatus] = None

    source_engine: Optional[str] = None

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    search_text: Optional[str] = None

    tags: List[str] = field(default_factory=list)

    limit: int = 100


# ============================================================================
# MEMORY PAGE STATE
# ============================================================================

@dataclass
class MemoryPageState:
    """
    UI state for the Memory page.

    The state intentionally contains no order/execution authority.
    """

    records: List[MemoryRecord] = field(default_factory=list)

    selected_memory_id: Optional[str] = None

    active_market: Optional[str] = None
    active_instrument: Optional[str] = None
    active_timeframe: Optional[str] = None

    total_records: int = 0
    visible_records: int = 0

    can_search: bool = True
    can_filter: bool = True
    can_view_evidence: bool = True
    can_view_history: bool = True

    production_mutation_allowed: bool = PRODUCTION_MUTATION_ALLOWED
    direct_engine_control_allowed: bool = DIRECT_ENGINE_CONTROL_ALLOWED
    direct_broker_control_allowed: bool = DIRECT_BROKER_CONTROL_ALLOWED

    decision_authority: str = DECISION_AUTHORITY

    messages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# MEMORY PAGE CONTROLLER
# ============================================================================

class MemoryPageController:
    """
    Lightweight UI controller.

    NOTE:
        This in-memory implementation is a page foundation only.

        In production, records MUST come from the canonical
        application/domain/memory service and persistence layer.

        The UI must not become the system of record.
    """

    def __init__(
        self,
        records: Optional[List[MemoryRecord]] = None,
    ) -> None:

        self._records: List[MemoryRecord] = list(records or [])

        self._selected_memory_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Record access
    # ------------------------------------------------------------------

    def list_records(self) -> List[MemoryRecord]:
        """Return all currently available memory records."""

        return list(self._records)

    def get_record(
        self,
        memory_id: str,
    ) -> Optional[MemoryRecord]:
        """Return a memory record by ID."""

        for record in self._records:
            if record.memory_id == memory_id:
                return record

        return None

    # ------------------------------------------------------------------
    # Record insertion
    # ------------------------------------------------------------------

    def add_record(
        self,
        record: MemoryRecord,
    ) -> MemoryRecord:
        """
        Add a memory record to the UI controller.

        This is NOT a production persistence operation.
        """

        if not record.memory_id:
            raise ValueError("memory_id is required")

        if self.get_record(record.memory_id) is not None:
            raise ValueError(
                f"Memory record already exists: {record.memory_id}"
            )

        self._records.append(record)

        return record

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def select_memory(
        self,
        memory_id: Optional[str],
    ) -> Optional[MemoryRecord]:

        if memory_id is None:
            self._selected_memory_id = None
            return None

        record = self.get_record(memory_id)

        if record is None:
            raise KeyError(
                f"Memory record not found: {memory_id}"
            )

        self._selected_memory_id = memory_id

        return record

    @property
    def selected_memory_id(self) -> Optional[str]:
        return self._selected_memory_id

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        query: Optional[MemoryQuery] = None,
    ) -> List[MemoryRecord]:

        query = query or MemoryQuery()

        records = list(self._records)

        if query.market:
            records = [
                r for r in records
                if r.market.lower() == query.market.lower()
            ]

        if query.instrument:
            records = [
                r for r in records
                if r.instrument.lower() == query.instrument.lower()
            ]

        if query.timeframe:
            records = [
                r for r in records
                if r.timeframe.lower() == query.timeframe.lower()
            ]

        if query.memory_type:
            records = [
                r for r in records
                if r.memory_type == query.memory_type
            ]

        if query.status:
            records = [
                r for r in records
                if r.status == query.status
            ]

        if query.source_engine:
            records = [
                r for r in records
                if r.source_engine.lower()
                == query.source_engine.lower()
            ]

        if query.start_time:
            records = [
                r for r in records
                if r.timestamp >= query.start_time
            ]

        if query.end_time:
            records = [
                r for r in records
                if r.timestamp <= query.end_time
            ]

        if query.search_text:
            text = query.search_text.lower()

            records = [
                r
                for r in records
                if (
                    text in r.title.lower()
                    or text in r.description.lower()
                    or text in r.instrument.lower()
                    or text in r.market.lower()
                    or text in r.memory_id.lower()
                )
            ]

        if query.tags:
            required_tags = {
                tag.lower()
                for tag in query.tags
            }

            records = [
                r
                for r in records
                if required_tags.issubset(
                    {tag.lower() for tag in r.tags}
                )
            ]

        return records[: max(1, query.limit)]

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def build_state(
        self,
        query: Optional[MemoryQuery] = None,
    ) -> MemoryPageState:

        visible = self.query(query)

        selected = self.get_record(
            self._selected_memory_id
        ) if self._selected_memory_id else None

        return MemoryPageState(
            records=visible,
            selected_memory_id=self._selected_memory_id,
            active_market=selected.market if selected else None,
            active_instrument=(
                selected.instrument if selected else None
            ),
            active_timeframe=(
                selected.timeframe if selected else None
            ),
            total_records=len(self._records),
            visible_records=len(visible),
            production_mutation_allowed=False,
            direct_engine_control_allowed=False,
            direct_broker_control_allowed=False,
            decision_authority=DECISION_AUTHORITY,
        )


# ============================================================================
# STREAMLIT IMPORT
# ============================================================================

def _safe_import_streamlit():
    """
    Import Streamlit lazily.

    This keeps the module importable in environments where Streamlit
    is not installed, such as unit-test or backend-only environments.
    """

    try:
        import streamlit as st

        return st

    except ImportError:
        return None


# ============================================================================
# UI HELPERS
# ============================================================================

def _render_header(st) -> None:
    """Render Memory page header."""

    st.title(PAGE_TITLE)
    st.caption(PAGE_SUBTITLE)

    st.caption(
        f"Memory UI v{MEMORY_PAGE_VERSION} | "
        f"Decision Authority: {DECISION_AUTHORITY}"
    )


def _render_architecture_notice(st) -> None:
    """
    Render architectural safety boundary.
    """

    st.info(
        "Memory provides historical market context and evidence. "
        "It does not issue trading decisions or control execution. "
        "Final decision authority remains D13."
    )


def _render_status_summary(
    st,
    state: MemoryPageState,
) -> None:
    """Render basic memory statistics."""

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Memory",
            state.total_records,
        )

    with col2:
        st.metric(
            "Visible",
            state.visible_records,
        )

    with col3:
        st.metric(
            "Selected",
            "Yes" if state.selected_memory_id else "No",
        )


def _render_memory_list(
    st,
    records: List[MemoryRecord],
) -> None:
    """Render memory records."""

    if not records:
        st.info("No memory records available.")
        return

    for record in records:

        label = (
            record.title
            or record.instrument
            or record.memory_id
            or "Memory Record"
        )

        with st.expander(label):

            st.write(
                f"**Memory ID:** {record.memory_id}"
            )

            st.write(
                f"**Type:** {record.memory_type.value}"
            )

            st.write(
                f"**Status:** {record.status.value}"
            )

            if record.market:
                st.write(
                    f"**Market:** {record.market}"
                )

            if record.instrument:
                st.write(
                    f"**Instrument:** {record.instrument}"
                )

            if record.timeframe:
                st.write(
                    f"**Timeframe:** {record.timeframe}"
                )

            if record.description:
                st.write(record.description)

            if record.source_engine:
                st.caption(
                    f"Source: {record.source_engine}"
                )


def _render_selected_memory(
    st,
    record: Optional[MemoryRecord],
) -> None:
    """Render selected memory details."""

    if record is None:
        st.info("Select a memory record to inspect details.")
        return

    st.subheader("Selected Memory")

    st.write(
        f"### {record.title or record.memory_id}"
    )

    st.write(
        f"**Timestamp:** {record.timestamp.isoformat()}"
    )

    st.write(
        f"**Type:** {record.memory_type.value}"
    )

    st.write(
        f"**Status:** {record.status.value}"
    )

    if record.description:
        st.write(record.description)

    if record.evidence:
        st.write("**Evidence Reference**")
        st.json(record.evidence)

    if record.context:
        st.write("**Historical Context**")
        st.json(record.context)

    if record.outcome:
        st.write("**Outcome**")
        st.json(record.outcome)


# ============================================================================
# BASIC PAGE RENDERER
# ============================================================================

def render_memory_page(
    controller: Optional[MemoryPageController] = None,
) -> None:
    """
    Basic Memory page renderer.

    This is Part 1 only.
    Advanced search, historical comparison, memory retrieval,
    learning integration, and governance integration can be layered
    on top without changing the architectural boundary.
    """

    st = _safe_import_streamlit()

    if st is None:
        raise RuntimeError(
            "Streamlit is required to render the Memory page."
        )

    controller = controller or MemoryPageController()

    state = controller.build_state()

    _render_header(st)
    _render_architecture_notice(st)
    _render_status_summary(st, state)

    st.divider()

    _render_memory_list(
        st,
        state.records,
    )

    st.divider()

    selected = (
        controller.get_record(state.selected_memory_id)
        if state.selected_memory_id
        else None
    )

    _render_selected_memory(
        st,
        selected,
    )


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "PAGE_TITLE",
    "PAGE_SUBTITLE",
    "MEMORY_PAGE_VERSION",
    "UI_SCHEMA_VERSION",
    "DECISION_AUTHORITY",
    "PRODUCTION_MUTATION_ALLOWED",
    "DIRECT_ENGINE_CONTROL_ALLOWED",
    "DIRECT_BROKER_CONTROL_ALLOWED",
    "MemoryStatus",
    "MemoryType",
    "MemoryRecord",
    "MemoryQuery",
    "MemoryPageState",
    "MemoryPageController",
    "render_memory_page",
]
```
```python
# ============================================================================
# PART 2 — SEARCH / FILTER / TIMELINE / NAVIGATION
# ============================================================================

from collections import Counter


# ============================================================================
# FILTER OPTIONS
# ============================================================================

def _get_unique_markets(
    records: List[MemoryRecord],
) -> List[str]:
    """Return available markets."""

    values = {
        record.market.strip()
        for record in records
        if record.market
    }

    return sorted(values)


def _get_unique_instruments(
    records: List[MemoryRecord],
) -> List[str]:
    """Return available instruments."""

    values = {
        record.instrument.strip()
        for record in records
        if record.instrument
    }

    return sorted(values)


def _get_unique_timeframes(
    records: List[MemoryRecord],
) -> List[str]:
    """Return available timeframes."""

    values = {
        record.timeframe.strip()
        for record in records
        if record.timeframe
    }

    return sorted(values)


def _get_unique_engines(
    records: List[MemoryRecord],
) -> List[str]:
    """Return source engines represented in memory."""

    values = {
        record.source_engine.strip()
        for record in records
        if record.source_engine
    }

    return sorted(values)


def _get_unique_tags(
    records: List[MemoryRecord],
) -> List[str]:
    """Return all known memory tags."""

    values = set()

    for record in records:
        for tag in record.tags:
            if tag:
                values.add(tag.strip())

    return sorted(values)


# ============================================================================
# MEMORY FILTER STATE
# ============================================================================

@dataclass
class MemoryFilterState:
    """
    UI filter state.

    Filters only retrieve/display existing memory.
    They do not generate intelligence.
    """

    market: Optional[str] = None
    instrument: Optional[str] = None
    timeframe: Optional[str] = None

    memory_type: Optional[MemoryType] = None
    status: Optional[MemoryStatus] = None

    source_engine: Optional[str] = None

    search_text: str = ""

    selected_tags: List[str] = field(
        default_factory=list
    )

    limit: int = 100

    def to_query(self) -> MemoryQuery:
        """Convert UI filter state into MemoryQuery."""

        return MemoryQuery(
            market=self.market,
            instrument=self.instrument,
            timeframe=self.timeframe,
            memory_type=self.memory_type,
            status=self.status,
            source_engine=self.source_engine,
            search_text=self.search_text or None,
            tags=list(self.selected_tags),
            limit=self.limit,
        )


# ============================================================================
# FILTER CONTROLLER
# ============================================================================

class MemoryFilterController:
    """
    Controls Memory UI filters.

    This class has no decision-making authority.
    """

    def __init__(self) -> None:

        self.state = MemoryFilterState()

    def reset(self) -> None:
        """Reset all filters."""

        self.state = MemoryFilterState()

    def build_query(self) -> MemoryQuery:
        """Return the current MemoryQuery."""

        return self.state.to_query()


# ============================================================================
# SEARCH HELPERS
# ============================================================================

def _memory_matches_search(
    record: MemoryRecord,
    search_text: str,
) -> bool:
    """
    Search across descriptive memory fields.

    This is textual retrieval only.
    """

    if not search_text:
        return True

    needle = search_text.strip().lower()

    if not needle:
        return True

    searchable_values = [
        record.memory_id,
        record.market,
        record.instrument,
        record.timeframe,
        record.title,
        record.description,
        record.source_engine,
        record.engine_version,
    ]

    searchable_values.extend(record.tags)

    for value in searchable_values:
        if value and needle in str(value).lower():
            return True

    return False


# ============================================================================
# TIMELINE MODEL
# ============================================================================

@dataclass
class MemoryTimelineItem:
    """
    Timeline representation of a memory record.

    This contains historical observations only.
    """

    memory_id: str
    timestamp: datetime

    title: str
    memory_type: MemoryType
    status: MemoryStatus

    market: str = ""
    instrument: str = ""
    timeframe: str = ""

    source_engine: str = ""

    description: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_record(
        cls,
        record: MemoryRecord,
    ) -> "MemoryTimelineItem":

        return cls(
            memory_id=record.memory_id,
            timestamp=record.timestamp,
            title=(
                record.title
                or record.instrument
                or record.memory_id
            ),
            memory_type=record.memory_type,
            status=record.status,
            market=record.market,
            instrument=record.instrument,
            timeframe=record.timeframe,
            source_engine=record.source_engine,
            description=record.description,
            metadata=dict(record.metadata),
        )


# ============================================================================
# TIMELINE BUILDER
# ============================================================================

class MemoryTimelineBuilder:
    """Build chronological memory views."""

    @staticmethod
    def build(
        records: List[MemoryRecord],
        newest_first: bool = True,
    ) -> List[MemoryTimelineItem]:

        ordered = sorted(
            records,
            key=lambda record: record.timestamp,
            reverse=newest_first,
        )

        return [
            MemoryTimelineItem.from_record(record)
            for record in ordered
        ]


# ============================================================================
# MEMORY STATISTICS
# ============================================================================

@dataclass
class MemoryStatistics:
    """Descriptive statistics for currently available memory."""

    total: int = 0

    by_type: Dict[str, int] = field(
        default_factory=dict
    )

    by_status: Dict[str, int] = field(
        default_factory=dict
    )

    by_market: Dict[str, int] = field(
        default_factory=dict
    )

    by_instrument: Dict[str, int] = field(
        default_factory=dict
    )

    by_engine: Dict[str, int] = field(
        default_factory=dict
    )


def build_memory_statistics(
    records: List[MemoryRecord],
) -> MemoryStatistics:
    """Build descriptive statistics without scoring or ranking."""

    type_counter = Counter(
        record.memory_type.value
        for record in records
    )

    status_counter = Counter(
        record.status.value
        for record in records
    )

    market_counter = Counter(
        record.market
        for record in records
        if record.market
    )

    instrument_counter = Counter(
        record.instrument
        for record in records
        if record.instrument
    )

    engine_counter = Counter(
        record.source_engine
        for record in records
        if record.source_engine
    )

    return MemoryStatistics(
        total=len(records),
        by_type=dict(type_counter),
        by_status=dict(status_counter),
        by_market=dict(market_counter),
        by_instrument=dict(instrument_counter),
        by_engine=dict(engine_counter),
    )


# ============================================================================
# STREAMLIT FILTER UI
# ============================================================================

def _render_memory_filters(
    st,
    controller: MemoryPageController,
    filter_controller: MemoryFilterController,
) -> MemoryQuery:
    """
    Render Memory filters and return the resulting query.
    """

    records = controller.list_records()
    state = filter_controller.state

    st.subheader("Memory Search")

    search_text = st.text_input(
        "Search memory",
        value=state.search_text,
        placeholder=(
            "Search by memory ID, market, instrument, "
            "title, description or source engine"
        ),
    )

    markets = ["All"] + _get_unique_markets(records)
    instruments = ["All"] + _get_unique_instruments(records)
    timeframes = ["All"] + _get_unique_timeframes(records)
    engines = ["All"] + _get_unique_engines(records)
    tags = _get_unique_tags(records)

    col1, col2, col3 = st.columns(3)

    with col1:

        selected_market = st.selectbox(
            "Market",
            markets,
            index=(
                markets.index(state.market)
                if state.market in markets
                else 0
            ),
        )

    with col2:

        selected_instrument = st.selectbox(
            "Instrument",
            instruments,
            index=(
                instruments.index(state.instrument)
                if state.instrument in instruments
                else 0
            ),
        )

    with col3:

        selected_timeframe = st.selectbox(
            "Timeframe",
            timeframes,
            index=(
                timeframes.index(state.timeframe)
                if state.timeframe in timeframes
                else 0
            ),
        )

    col4, col5, col6 = st.columns(3)

    memory_type_options = [
        "All"
    ] + [
        item.value
        for item in MemoryType
    ]

    status_options = [
        "All"
    ] + [
        item.value
        for item in MemoryStatus
    ]

    with col4:

        selected_type = st.selectbox(
            "Memory Type",
            memory_type_options,
        )

    with col5:

        selected_status = st.selectbox(
            "Status",
            status_options,
        )

    with col6:

        selected_engine = st.selectbox(
            "Source Engine",
            engines,
            index=(
                engines.index(state.source_engine)
                if state.source_engine in engines
                else 0
            ),
        )

    selected_tags = st.multiselect(
        "Tags",
        tags,
        default=[
            tag
            for tag in state.selected_tags
            if tag in tags
        ],
    )

    limit = st.number_input(
        "Maximum records",
        min_value=1,
        max_value=1000,
        value=max(1, min(state.limit, 1000)),
        step=10,
    )

    col_reset, col_apply = st.columns(2)

    with col_reset:

        if st.button(
            "Reset Filters",
            use_container_width=True,
        ):

            filter_controller.reset()
            st.rerun()

    with col_apply:

        apply_clicked = st.button(
            "Apply Filters",
            use_container_width=True,
        )

    # Update controller state.
    state.search_text = search_text

    state.market = (
        None
        if selected_market == "All"
        else selected_market
    )

    state.instrument = (
        None
        if selected_instrument == "All"
        else selected_instrument
    )

    state.timeframe = (
        None
        if selected_timeframe == "All"
        else selected_timeframe
    )

    state.memory_type = (
        None
        if selected_type == "All"
        else MemoryType(selected_type)
    )

    state.status = (
        None
        if selected_status == "All"
        else MemoryStatus(selected_status)
    )

    state.source_engine = (
        None
        if selected_engine == "All"
        else selected_engine
    )

    state.selected_tags = list(selected_tags)

    state.limit = int(limit)

    return filter_controller.build_query()


# ============================================================================
# TIMELINE UI
# ============================================================================

def _render_memory_timeline(
    st,
    records: List[MemoryRecord],
    controller: MemoryPageController,
) -> None:
    """Render chronological memory timeline."""

    st.subheader("Memory Timeline")

    timeline = MemoryTimelineBuilder.build(
        records,
        newest_first=True,
    )

    if not timeline:
        st.info("No historical memory matches the current filters.")
        return

    for item in timeline:

        timestamp_text = item.timestamp.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        label = (
            f"{timestamp_text} — "
            f"{item.title}"
        )

        with st.expander(label):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption("Type")
                st.write(item.memory_type.value)

            with col2:
                st.caption("Status")
                st.write(item.status.value)

            with col3:
                st.caption("Memory ID")
                st.write(item.memory_id)

            if item.market:
                st.write(
                    f"**Market:** {item.market}"
                )

            if item.instrument:
                st.write(
                    f"**Instrument:** {item.instrument}"
                )

            if item.timeframe:
                st.write(
                    f"**Timeframe:** {item.timeframe}"
                )

            if item.source_engine:
                st.write(
                    f"**Source:** {item.source_engine}"
                )

            if item.description:
                st.write(item.description)

            if st.button(
                "Inspect Memory",
                key=f"inspect_memory_{item.memory_id}",
                use_container_width=True,
            ):

                controller.select_memory(
                    item.memory_id
                )

                st.rerun()


# ============================================================================
# STATISTICS UI
# ============================================================================

def _render_memory_statistics(
    st,
    records: List[MemoryRecord],
) -> None:
    """Render descriptive memory statistics."""

    statistics = build_memory_statistics(records)

    st.subheader("Memory Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total",
            statistics.total,
        )

    with col2:
        st.metric(
            "Markets",
            len(statistics.by_market),
        )

    with col3:
        st.metric(
            "Instruments",
            len(statistics.by_instrument),
        )

    with col4:
        st.metric(
            "Memory Types",
            len(statistics.by_type),
        )

    if statistics.by_type:

        st.write("**By Memory Type**")

        st.json(statistics.by_type)

    if statistics.by_status:

        st.write("**By Status**")

        st.json(statistics.by_status)


# ============================================================================
# MEMORY SELECTOR
# ============================================================================

def _render_memory_selector(
    st,
    records: List[MemoryRecord],
    controller: MemoryPageController,
) -> None:
    """Render direct memory selection control."""

    if not records:
        return

    options = [
        record.memory_id
        for record in records
    ]

    current_id = controller.selected_memory_id

    current_index = (
        options.index(current_id)
        if current_id in options
        else 0
    )

    selected_id = st.selectbox(
        "Selected Memory",
        options,
        index=current_index,
    )

    if selected_id != controller.selected_memory_id:

        controller.select_memory(
            selected_id
        )


# ============================================================================
# ENHANCED PAGE RENDERER
# ============================================================================

def render_memory_page_part2(
    controller: Optional[MemoryPageController] = None,
) -> None:
    """
    Memory page renderer with Part 2 capabilities.

    Features:
        - Search
        - Filters
        - Memory selection
        - Timeline
        - Descriptive statistics
        - Historical detail view

    No decision or execution authority is added.
    """

    st = _safe_import_streamlit()

    if st is None:
        raise RuntimeError(
            "Streamlit is required to render the Memory page."
        )

    controller = controller or MemoryPageController()

    filter_controller = MemoryFilterController()

    # ------------------------------------------------------------
    # Header
    # ------------------------------------------------------------

    _render_header(st)

    _render_architecture_notice(st)

    # ------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------

    query = _render_memory_filters(
        st,
        controller,
        filter_controller,
    )

    filtered_records = controller.query(query)

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------

    st.divider()

    state = controller.build_state(query)

    _render_status_summary(
        st,
        state,
    )

    # ------------------------------------------------------------
    # Selector
    # ------------------------------------------------------------

    st.divider()

    _render_memory_selector(
        st,
        filtered_records,
        controller,
    )

    # ------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------

    st.divider()

    _render_memory_statistics(
        st,
        filtered_records,
    )

    # ------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------

    st.divider()

    _render_memory_timeline(
        st,
        filtered_records,
        controller,
    )

    # ------------------------------------------------------------
    # Selected memory
    # ------------------------------------------------------------

    st.divider()

    selected = (
        controller.get_record(
            controller.selected_memory_id
        )
        if controller.selected_memory_id
        else None
    )

    _render_selected_memory(
        st,
        selected,
    )


# ============================================================================
# PUBLIC API EXTENSION
# ============================================================================

try:
    __all__.extend(
        [
            "MemoryFilterState",
            "MemoryFilterController",
            "MemoryTimelineItem",
            "MemoryTimelineBuilder",
            "MemoryStatistics",
            "build_memory_statistics",
            "render_memory_page_part2",
        ]
    )
except NameError:
    __all__ = [
        "MemoryFilterState",
        "MemoryFilterController",
        "MemoryTimelineItem",
        "MemoryTimelineBuilder",
        "MemoryStatistics",
        "build_memory_statistics",
        "render_memory_page_part2",
    ]
```
```python
# ============================================================================
# PART 3 — MEMORY RELATIONSHIPS / RECURRENCE / CONTEXT COMPARISON
# ============================================================================

from dataclasses import asdict


# ============================================================================
# MEMORY RELATION TYPE
# ============================================================================

class MemoryRelationType(str, Enum):
    """
    Relationship between two historical memory records.

    These relationships describe historical/contextual similarity only.
    They are NOT trade signals.
    """

    SAME_INSTRUMENT = "SAME_INSTRUMENT"
    SAME_MARKET = "SAME_MARKET"
    SAME_TIMEFRAME = "SAME_TIMEFRAME"

    SAME_MEMORY_TYPE = "SAME_MEMORY_TYPE"

    SAME_SOURCE_ENGINE = "SAME_SOURCE_ENGINE"

    TEMPORAL_SEQUENCE = "TEMPORAL_SEQUENCE"

    SHARED_TAG = "SHARED_TAG"

    RELATED_CONTEXT = "RELATED_CONTEXT"

    RELATED_OUTCOME = "RELATED_OUTCOME"

    UNKNOWN = "UNKNOWN"


# ============================================================================
# MEMORY RELATION
# ============================================================================

@dataclass
class MemoryRelation:
    """
    Historical relationship between two memory records.

    No predictive score is generated here.
    """

    relation_id: str

    source_memory_id: str
    target_memory_id: str

    relation_type: MemoryRelationType

    reason: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "source_memory_id": self.source_memory_id,
            "target_memory_id": self.target_memory_id,
            "relation_type": self.relation_type.value,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


# ============================================================================
# MEMORY CONTEXT SNAPSHOT
# ============================================================================

@dataclass
class MemoryContextSnapshot:
    """
    Historical context extracted from one memory record.

    This preserves source information instead of converting history
    into an invented predictive indicator.
    """

    memory_id: str

    timestamp: datetime

    market: str = ""
    instrument: str = ""
    timeframe: str = ""

    memory_type: MemoryType = MemoryType.UNKNOWN
    status: MemoryStatus = MemoryStatus.UNKNOWN

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    outcome: Dict[str, Any] = field(
        default_factory=dict
    )

    source_engine: str = ""
    engine_version: str = ""

    tags: List[str] = field(
        default_factory=list
    )

    @classmethod
    def from_record(
        cls,
        record: MemoryRecord,
    ) -> "MemoryContextSnapshot":

        return cls(
            memory_id=record.memory_id,
            timestamp=record.timestamp,
            market=record.market,
            instrument=record.instrument,
            timeframe=record.timeframe,
            memory_type=record.memory_type,
            status=record.status,
            evidence=dict(record.evidence),
            context=dict(record.context),
            outcome=dict(record.outcome),
            source_engine=record.source_engine,
            engine_version=record.engine_version,
            tags=list(record.tags),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "timestamp": self.timestamp.isoformat(),
            "market": self.market,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "memory_type": self.memory_type.value,
            "status": self.status.value,
            "evidence": dict(self.evidence),
            "context": dict(self.context),
            "outcome": dict(self.outcome),
            "source_engine": self.source_engine,
            "engine_version": self.engine_version,
            "tags": list(self.tags),
        }


# ============================================================================
# MEMORY COMPARISON
# ============================================================================

@dataclass
class MemoryComparison:
    """
    Descriptive comparison between two historical memory records.

    Important:
        Similarity here is structural/descriptive.
        It is NOT a probability of future price movement.
    """

    source_memory_id: str
    target_memory_id: str

    same_market: bool = False
    same_instrument: bool = False
    same_timeframe: bool = False
    same_memory_type: bool = False
    same_source_engine: bool = False

    shared_tags: List[str] = field(
        default_factory=list
    )

    timestamp_distance_seconds: Optional[float] = None

    evidence_overlap: List[str] = field(
        default_factory=list
    )

    context_overlap: List[str] = field(
        default_factory=list
    )

    outcome_overlap: List[str] = field(
        default_factory=list
    )

    reasons: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# MEMORY COMPARISON ENGINE
# ============================================================================

class MemoryComparisonEngine:
    """
    Descriptive historical comparison engine.

    It does not calculate:
        - trade probability
        - entry
        - target
        - stop loss
        - BUY / SELL
        - position size
        - execution action
    """

    @staticmethod
    def _shared_keys(
        first: Dict[str, Any],
        second: Dict[str, Any],
    ) -> List[str]:

        first_keys = set(first.keys())
        second_keys = set(second.keys())

        return sorted(
            first_keys.intersection(second_keys)
        )

    @classmethod
    def compare(
        cls,
        source: MemoryRecord,
        target: MemoryRecord,
    ) -> MemoryComparison:

        shared_tags = sorted(
            {
                tag.lower()
                for tag in source.tags
            }.intersection(
                {
                    tag.lower()
                    for tag in target.tags
                }
            )
        )

        evidence_overlap = cls._shared_keys(
            source.evidence,
            target.evidence,
        )

        context_overlap = cls._shared_keys(
            source.context,
            target.context,
        )

        outcome_overlap = cls._shared_keys(
            source.outcome,
            target.outcome,
        )

        timestamp_distance = abs(
            (
                source.timestamp
                - target.timestamp
            ).total_seconds()
        )

        reasons: List[str] = []

        if source.market and (
            source.market.lower()
            == target.market.lower()
        ):
            reasons.append("Same market")

        if source.instrument and (
            source.instrument.lower()
            == target.instrument.lower()
        ):
            reasons.append("Same instrument")

        if source.timeframe and (
            source.timeframe.lower()
            == target.timeframe.lower()
        ):
            reasons.append("Same timeframe")

        if source.memory_type == target.memory_type:
            reasons.append("Same memory type")

        if shared_tags:
            reasons.append(
                "Shared tags present"
            )

        return MemoryComparison(
            source_memory_id=source.memory_id,
            target_memory_id=target.memory_id,
            same_market=(
                bool(source.market)
                and bool(target.market)
                and source.market.lower()
                == target.market.lower()
            ),
            same_instrument=(
                bool(source.instrument)
                and bool(target.instrument)
                and source.instrument.lower()
                == target.instrument.lower()
            ),
            same_timeframe=(
                bool(source.timeframe)
                and bool(target.timeframe)
                and source.timeframe.lower()
                == target.timeframe.lower()
            ),
            same_memory_type=(
                source.memory_type
                == target.memory_type
            ),
            same_source_engine=(
                bool(source.source_engine)
                and bool(target.source_engine)
                and source.source_engine.lower()
                == target.source_engine.lower()
            ),
            shared_tags=shared_tags,
            timestamp_distance_seconds=timestamp_distance,
            evidence_overlap=evidence_overlap,
            context_overlap=context_overlap,
            outcome_overlap=outcome_overlap,
            reasons=reasons,
        )


# ============================================================================
# RECURRENCE RECORD
# ============================================================================

@dataclass
class MemoryRecurrence:
    """
    Describes a recurring historical characteristic.

    This is a retrieval observation, not a predictive signal.
    """

    recurrence_id: str

    key: str

    occurrences: int

    memory_ids: List[str] = field(
        default_factory=list
    )

    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    markets: List[str] = field(
        default_factory=list
    )

    instruments: List[str] = field(
        default_factory=list
    )

    memory_types: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# RECURRENCE ENGINE
# ============================================================================

class MemoryRecurrenceEngine:
    """
    Finds simple repeated descriptive characteristics.

    No statistical prediction or trading probability is generated.
    """

    @staticmethod
    def build_tag_recurrence(
        records: List[MemoryRecord],
    ) -> List[MemoryRecurrence]:

        groups: Dict[str, List[MemoryRecord]] = {}

        for record in records:

            for tag in record.tags:

                normalized = tag.strip().lower()

                if not normalized:
                    continue

                groups.setdefault(
                    normalized,
                    [],
                ).append(record)

        results: List[MemoryRecurrence] = []

        for tag, grouped_records in groups.items():

            if len(grouped_records) < 2:
                continue

            ordered = sorted(
                grouped_records,
                key=lambda record: record.timestamp,
            )

            results.append(
                MemoryRecurrence(
                    recurrence_id=(
                        f"TAG:{tag}"
                    ),
                    key=f"tag:{tag}",
                    occurrences=len(
                        grouped_records
                    ),
                    memory_ids=[
                        record.memory_id
                        for record in ordered
                    ],
                    first_seen=ordered[0].timestamp,
                    last_seen=ordered[-1].timestamp,
                    markets=sorted(
                        {
                            record.market
                            for record in ordered
                            if record.market
                        }
                    ),
                    instruments=sorted(
                        {
                            record.instrument
                            for record in ordered
                            if record.instrument
                        }
                    ),
                    memory_types=sorted(
                        {
                            record.memory_type.value
                            for record in ordered
                        }
                    ),
                )
            )

        return results

    @staticmethod
    def build_instrument_recurrence(
        records: List[MemoryRecord],
    ) -> List[MemoryRecurrence]:

        groups: Dict[str, List[MemoryRecord]] = {}

        for record in records:

            key = record.instrument.strip().lower()

            if not key:
                continue

            groups.setdefault(
                key,
                [],
            ).append(record)

        results: List[MemoryRecurrence] = []

        for instrument, grouped_records in groups.items():

            if len(grouped_records) < 2:
                continue

            ordered = sorted(
                grouped_records,
                key=lambda record: record.timestamp,
            )

            results.append(
                MemoryRecurrence(
                    recurrence_id=(
                        f"INSTRUMENT:{instrument}"
                    ),
                    key=f"instrument:{instrument}",
                    occurrences=len(
                        grouped_records
                    ),
                    memory_ids=[
                        record.memory_id
                        for record in ordered
                    ],
                    first_seen=ordered[0].timestamp,
                    last_seen=ordered[-1].timestamp,
                    markets=sorted(
                        {
                            record.market
                            for record in ordered
                            if record.market
                        }
                    ),
                    instruments=[
                        ordered[0].instrument
                    ],
                    memory_types=sorted(
                        {
                            record.memory_type.value
                            for record in ordered
                        }
                    ),
                )
            )

        return results


# ============================================================================
# RELATIONSHIP BUILDER
# ============================================================================

class MemoryRelationshipEngine:
    """
    Builds transparent historical relationships.

    Relationships are explicit and explainable.
    """

    @staticmethod
    def build(
        records: List[MemoryRecord],
    ) -> List[MemoryRelation]:

        relations: List[MemoryRelation] = []

        for index, source in enumerate(records):

            for target in records[index + 1:]:

                relation_type: Optional[
                    MemoryRelationType
                ] = None

                reason = ""

                if (
                    source.instrument
                    and target.instrument
                    and source.instrument.lower()
                    == target.instrument.lower()
                ):

                    relation_type = (
                        MemoryRelationType.SAME_INSTRUMENT
                    )

                    reason = (
                        "Historical records reference "
                        "the same instrument."
                    )

                elif (
                    source.market
                    and target.market
                    and source.market.lower()
                    == target.market.lower()
                ):

                    relation_type = (
                        MemoryRelationType.SAME_MARKET
                    )

                    reason = (
                        "Historical records belong "
                        "to the same market."
                    )

                elif (
                    source.memory_type
                    == target.memory_type
                ):

                    relation_type = (
                        MemoryRelationType.SAME_MEMORY_TYPE
                    )

                    reason = (
                        "Historical records have "
                        "the same memory type."
                    )

                else:

                    shared_tags = {
                        tag.lower()
                        for tag in source.tags
                    }.intersection(
                        {
                            tag.lower()
                            for tag in target.tags
                        }
                    )

                    if shared_tags:

                        relation_type = (
                            MemoryRelationType.SHARED_TAG
                        )

                        reason = (
                            "Historical records share "
                            "one or more tags."
                        )

                if relation_type is None:
                    continue

                relation_id = (
                    f"{source.memory_id}"
                    f"::{target.memory_id}"
                    f"::{relation_type.value}"
                )

                relations.append(
                    MemoryRelation(
                        relation_id=relation_id,
                        source_memory_id=source.memory_id,
                        target_memory_id=target.memory_id,
                        relation_type=relation_type,
                        reason=reason,
                    )
                )

        return relations


# ============================================================================
# CONTEXT COMPARISON UI
# ============================================================================

def _render_memory_context_comparison(
    st,
    source: Optional[MemoryRecord],
    target: Optional[MemoryRecord],
) -> None:
    """
    Display two historical memories side by side.
    """

    st.subheader("Historical Context Comparison")

    if source is None or target is None:

        st.info(
            "Select two memory records to compare "
            "their historical context."
        )

        return

    comparison = MemoryComparisonEngine.compare(
        source,
        target,
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"**Source:** `{source.memory_id}`"
        )

        st.write(
            source.title
            or source.instrument
            or "Memory"
        )

        st.caption(
            source.timestamp.isoformat()
        )

    with col2:

        st.markdown(
            f"**Target:** `{target.memory_id}`"
        )

        st.write(
            target.title
            or target.instrument
            or "Memory"
        )

        st.caption(
            target.timestamp.isoformat()
        )

    st.divider()

    comparison_rows = {
        "Same market": comparison.same_market,
        "Same instrument": comparison.same_instrument,
        "Same timeframe": comparison.same_timeframe,
        "Same memory type": comparison.same_memory_type,
        "Same source engine": comparison.same_source_engine,
    }

    st.json(comparison_rows)

    if comparison.shared_tags:

        st.write(
            "**Shared Tags:**",
            ", ".join(comparison.shared_tags),
        )

    if comparison.evidence_overlap:

        st.write(
            "**Shared Evidence Fields:**",
            ", ".join(comparison.evidence_overlap),
        )

    if comparison.context_overlap:

        st.write(
            "**Shared Context Fields:**",
            ", ".join(comparison.context_overlap),
        )

    if comparison.outcome_overlap:

        st.write(
            "**Shared Outcome Fields:**",
            ", ".join(comparison.outcome_overlap),
        )

    if comparison.reasons:

        st.write("**Relationship Reasons**")

        for reason in comparison.reasons:
            st.write(f"- {reason}")

    if comparison.timestamp_distance_seconds is not None:

        st.caption(
            "Historical time distance: "
            f"{comparison.timestamp_distance_seconds:.0f} seconds"
        )


# ============================================================================
# RELATIONSHIP UI
# ============================================================================

def _render_memory_relationships(
    st,
    records: List[MemoryRecord],
) -> None:
    """Render historical relationships."""

    st.subheader("Memory Relationships")

    if len(records) < 2:

        st.info(
            "At least two memory records are required "
            "to inspect relationships."
        )

        return

    relations = MemoryRelationshipEngine.build(
        records
    )

    if not relations:

        st.info(
            "No explicit historical relationships "
            "were found."
        )

        return

    for relation in relations:

        with st.expander(
            f"{relation.source_memory_id} → "
            f"{relation.target_memory_id}"
        ):

            st.write(
                f"**Relationship:** "
                f"{relation.relation_type.value}"
            )

            st.write(
                f"**Reason:** {relation.reason}"
            )


# ============================================================================
# RECURRENCE UI
# ============================================================================

def _render_memory_recurrence(
    st,
    records: List[MemoryRecord],
) -> None:
    """Render recurring historical characteristics."""

    st.subheader("Historical Recurrence")

    tag_recurrence = (
        MemoryRecurrenceEngine
        .build_tag_recurrence(records)
    )

    instrument_recurrence = (
        MemoryRecurrenceEngine
        .build_instrument_recurrence(records)
    )

    if not tag_recurrence and not instrument_recurrence:

        st.info(
            "No recurring historical characteristics "
            "are available in the current memory set."
        )

        return

    if tag_recurrence:

        st.write("**Recurring Tags**")

        for recurrence in tag_recurrence:

            st.write(
                f"- `{recurrence.key}` — "
                f"{recurrence.occurrences} occurrences"
            )

    if instrument_recurrence:

        st.write("**Recurring Instruments**")

        for recurrence in instrument_recurrence:

            st.write(
                f"- `{recurrence.key}` — "
                f"{recurrence.occurrences} occurrences"
            )


# ============================================================================
# MEMORY EVIDENCE / CONTEXT / OUTCOME SEPARATION
# ============================================================================

def _render_memory_layers(
    st,
    record: Optional[MemoryRecord],
) -> None:
    """
    Display the three historical layers separately.

    Evidence:
        What upstream systems recorded.

    Context:
        What historical environment accompanied it.

    Outcome:
        What subsequently happened / was recorded.

    These are displayed separately to avoid conflating
    evidence with outcome.
    """

    st.subheader("Memory Layers")

    if record is None:

        st.info(
            "Select a memory record to inspect its layers."
        )

        return

    evidence_tab, context_tab, outcome_tab = st.tabs(
        [
            "Evidence",
            "Context",
            "Outcome",
        ]
    )

    with evidence_tab:

        if record.evidence:
            st.json(record.evidence)
        else:
            st.info(
                "No evidence payload is attached "
                "to this memory record."
            )

    with context_tab:

        if record.context:
            st.json(record.context)
        else:
            st.info(
                "No historical context payload is attached."
            )

    with outcome_tab:

        if record.outcome:
            st.json(record.outcome)
        else:
            st.info(
                "No historical outcome payload is attached."
            )


# ============================================================================
# PART 3 PAGE RENDERER
# ============================================================================

def render_memory_page_part3(
    controller: Optional[MemoryPageController] = None,
) -> None:
    """
    Memory page renderer with Part 1 + Part 2 + Part 3 capabilities.

    Part 3 adds:

        - Historical relationships
        - Recurrence inspection
        - Context comparison
        - Evidence/context/outcome separation
        - Transparent historical comparison

    No predictive trading model is introduced.
    """

    st = _safe_import_streamlit()

    if st is None:

        raise RuntimeError(
            "Streamlit is required to render the Memory page."
        )

    controller = (
        controller
        or MemoryPageController()
    )

    filter_controller = MemoryFilterController()

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    _render_header(st)

    _render_architecture_notice(st)

    # ------------------------------------------------------------------
    # Search / filters
    # ------------------------------------------------------------------

    query = _render_memory_filters(
        st,
        controller,
        filter_controller,
    )

    filtered_records = controller.query(
        query
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    st.divider()

    state = controller.build_state(
        query
    )

    _render_status_summary(
        st,
        state,
    )

    # ------------------------------------------------------------------
    # Selector
    # ------------------------------------------------------------------

    st.divider()

    _render_memory_selector(
        st,
        filtered_records,
        controller,
    )

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    st.divider()

    (
        overview_tab,
        timeline_tab,
        layers_tab,
        relationships_tab,
        recurrence_tab,
        comparison_tab,
    ) = st.tabs(
        [
            "Overview",
            "Timeline",
            "Memory Layers",
            "Relationships",
            "Recurrence",
            "Comparison",
        ]
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    with overview_tab:

        _render_memory_statistics(
            st,
            filtered_records,
        )

        st.divider()

        selected = (
            controller.get_record(
                controller.selected_memory_id
            )
            if controller.selected_memory_id
            else None
        )

        _render_selected_memory(
            st,
            selected,
        )

    # ------------------------------------------------------------------
    # Timeline
    # ------------------------------------------------------------------

    with timeline_tab:

        _render_memory_timeline(
            st,
            filtered_records,
            controller,
        )

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    with layers_tab:

        selected = (
            controller.get_record(
                controller.selected_memory_id
            )
            if controller.selected_memory_id
            else None
        )

        _render_memory_layers(
            st,
            selected,
        )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    with relationships_tab:

        _render_memory_relationships(
            st,
            filtered_records,
        )

    # ------------------------------------------------------------------
    # Recurrence
    # ------------------------------------------------------------------

    with recurrence_tab:

        _render_memory_recurrence(
            st,
            filtered_records,
        )

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    with comparison_tab:

        if len(filtered_records) >= 2:

            options = [
                record.memory_id
                for record in filtered_records
            ]

            source_id = st.selectbox(
                "Source Memory",
                options,
                key="memory_part3_source",
            )

            target_options = [
                item
                for item in options
                if item != source_id
            ]

            target_id = st.selectbox(
                "Target Memory",
                target_options,
                key="memory_part3_target",
            )

            source_record = (
                controller.get_record(
                    source_id
                )
            )

            target_record = (
                controller.get_record(
                    target_id
                )
            )

            _render_memory_context_comparison(
                st,
                source_record,
                target_record,
            )

        else:

            st.info(
                "At least two memory records are required "
                "for historical comparison."
            )


# ============================================================================
# PUBLIC API EXTENSION
# ============================================================================

try:

    __all__.extend(
        [
            "MemoryRelationType",
            "MemoryRelation",
            "MemoryContextSnapshot",
            "MemoryComparison",
            "MemoryComparisonEngine",
            "MemoryRecurrence",
            "MemoryRecurrenceEngine",
            "MemoryRelationshipEngine",
            "_render_memory_context_comparison",
            "_render_memory_relationships",
            "_render_memory_recurrence",
            "_render_memory_layers",
            "render_memory_page_part3",
        ]
    )

except NameError:

    __all__ = [
        "MemoryRelationType",
        "MemoryRelation",
        "MemoryContextSnapshot",
        "MemoryComparison",
        "MemoryComparisonEngine",
        "MemoryRecurrence",
        "MemoryRecurrenceEngine",
        "MemoryRelationshipEngine",
        "_render_memory_context_comparison",
        "_render_memory_relationships",
        "_render_memory_recurrence",
        "_render_memory_layers",
        "render_memory_page_part3",
    ]
```
```python
# ============================================================================
# PART 4 — PROVENANCE / VERSIONING / LEARNING HANDOFF / D13 BOUNDARY
# ============================================================================

# ============================================================================
# MEMORY PROVENANCE
# ============================================================================

@dataclass
class MemoryProvenance:
    """
    Provenance information for a historical memory record.

    Purpose:
        Preserve where the memory came from and which system versions
        produced or stored it.

    This is traceability metadata, not trading intelligence.
    """

    memory_id: str

    source_engine: str = ""
    engine_version: str = ""

    schema_version: str = ""
    robomlm_version: str = ""

    input_reference: Optional[str] = None
    output_reference: Optional[str] = None

    source_timestamp: Optional[datetime] = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "memory_id": self.memory_id,
            "source_engine": self.source_engine,
            "engine_version": self.engine_version,
            "schema_version": self.schema_version,
            "robomlm_version": self.robomlm_version,
            "input_reference": self.input_reference,
            "output_reference": self.output_reference,
            "source_timestamp": (
                self.source_timestamp.isoformat()
                if self.source_timestamp
                else None
            ),
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


# ============================================================================
# MEMORY VERSION
# ============================================================================

@dataclass
class MemoryVersion:
    """
    Version identity for a memory representation.

    A version identifies the representation/source state.
    It does not imply that the memory itself is correct or predictive.
    """

    memory_id: str

    memory_version: str = "1.0.0"

    robomlm_version: str = ""
    engine_version: str = ""
    schema_version: str = ""

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    parent_version: Optional[str] = None

    status: str = "ACTIVE"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "memory_id": self.memory_id,
            "memory_version": self.memory_version,
            "robomlm_version": self.robomlm_version,
            "engine_version": self.engine_version,
            "schema_version": self.schema_version,
            "created_at": self.created_at.isoformat(),
            "parent_version": self.parent_version,
            "status": self.status,
            "metadata": dict(self.metadata),
        }


# ============================================================================
# MEMORY LEARNING HANDOFF
# ============================================================================

@dataclass
class MemoryLearningInput:
    """
    Read-only handoff from Memory to Learning.

    Memory supplies historical information.

    Learning decides how that information is evaluated or learned.

    The Memory UI does not perform learning itself.
    """

    handoff_id: str

    memory_id: str

    timestamp: datetime

    market: str = ""
    instrument: str = ""
    timeframe: str = ""

    memory_type: MemoryType = MemoryType.UNKNOWN
    status: MemoryStatus = MemoryStatus.UNKNOWN

    evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    context: Dict[str, Any] = field(
        default_factory=dict
    )

    outcome: Dict[str, Any] = field(
        default_factory=dict
    )

    provenance: Optional[MemoryProvenance] = None
    version: Optional[MemoryVersion] = None

    source_engines: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "handoff_id": self.handoff_id,
            "memory_id": self.memory_id,
            "timestamp": self.timestamp.isoformat(),
            "market": self.market,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "memory_type": self.memory_type.value,
            "status": self.status.value,
            "evidence": dict(self.evidence),
            "context": dict(self.context),
            "outcome": dict(self.outcome),
            "provenance": (
                self.provenance.to_dict()
                if self.provenance
                else None
            ),
            "version": (
                self.version.to_dict()
                if self.version
                else None
            ),
            "source_engines": list(
                self.source_engines
            ),
            "metadata": dict(self.metadata),
        }


class MemoryLearningHandoffBuilder:
    """
    Builds a read-only learning input from MemoryRecord.

    No formula is created here.
    No learning update is performed here.
    """

    @staticmethod
    def build(
        record: MemoryRecord,
        provenance: Optional[MemoryProvenance] = None,
        version: Optional[MemoryVersion] = None,
    ) -> MemoryLearningInput:

        handoff_id = (
            f"MEMORY-LEARNING::{record.memory_id}"
        )

        source_engines = []

        if record.source_engine:
            source_engines.append(
                record.source_engine
            )

        return MemoryLearningInput(
            handoff_id=handoff_id,
            memory_id=record.memory_id,
            timestamp=record.timestamp,
            market=record.market,
            instrument=record.instrument,
            timeframe=record.timeframe,
            memory_type=record.memory_type,
            status=record.status,
            evidence=dict(record.evidence),
            context=dict(record.context),
            outcome=dict(record.outcome),
            provenance=provenance,
            version=version,
            source_engines=source_engines,
        )


# ============================================================================
# MEMORY DECISION CONTEXT
# ============================================================================

@dataclass
class MemoryDecisionContext:
    """
    Read-only historical context supplied toward decision processing.

    IMPORTANT:
        This object is NOT a decision.

        D13 remains the final decision authority.
    """

    context_id: str

    memory_id: str

    timestamp: datetime

    market: str = ""
    instrument: str = ""
    timeframe: str = ""

    historical_evidence: Dict[str, Any] = field(
        default_factory=dict
    )

    historical_context: Dict[str, Any] = field(
        default_factory=dict
    )

    historical_outcome: Dict[str, Any] = field(
        default_factory=dict
    )

    provenance: Optional[MemoryProvenance] = None

    memory_version: Optional[str] = None

    decision_authority: str = DECISION_AUTHORITY

    trade_issued: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "context_id": self.context_id,
            "memory_id": self.memory_id,
            "timestamp": self.timestamp.isoformat(),
            "market": self.market,
            "instrument": self.instrument,
            "timeframe": self.timeframe,
            "historical_evidence": dict(
                self.historical_evidence
            ),
            "historical_context": dict(
                self.historical_context
            ),
            "historical_outcome": dict(
                self.historical_outcome
            ),
            "provenance": (
                self.provenance.to_dict()
                if self.provenance
                else None
            ),
            "memory_version": self.memory_version,
            "decision_authority": self.decision_authority,
            "trade_issued": self.trade_issued,
            "metadata": dict(self.metadata),
        }


class MemoryDecisionContextBuilder:
    """
    Converts historical Memory into read-only decision context.

    The builder does not make a decision.
    """

    @staticmethod
    def build(
        record: MemoryRecord,
        provenance: Optional[MemoryProvenance] = None,
        version: Optional[MemoryVersion] = None,
    ) -> MemoryDecisionContext:

        return MemoryDecisionContext(
            context_id=(
                f"MEMORY-CONTEXT::{record.memory_id}"
            ),
            memory_id=record.memory_id,
            timestamp=record.timestamp,
            market=record.market,
            instrument=record.instrument,
            timeframe=record.timeframe,
            historical_evidence=dict(
                record.evidence
            ),
            historical_context=dict(
                record.context
            ),
            historical_outcome=dict(
                record.outcome
            ),
            provenance=provenance,
            memory_version=(
                version.memory_version
                if version
                else None
            ),
            decision_authority=DECISION_AUTHORITY,
            trade_issued=False,
        )


# ============================================================================
# MEMORY INTEGRATION CONTRACT
# ============================================================================

@dataclass
class MemoryIntegrationContract:
    """
    Integration contract describing what Memory can provide downstream.

    It explicitly prevents the UI from becoming a decision/execution layer.
    """

    contract_version: str = "1.0.0"

    provider: str = "MEMORY"

    historical_context_available: bool = True
    evidence_available: bool = True
    outcome_available: bool = True

    learning_handoff_available: bool = True
    decision_context_available: bool = True

    direct_decision_allowed: bool = False
    direct_execution_allowed: bool = False
    production_mutation_allowed: bool = False

    decision_authority: str = DECISION_AUTHORITY

    supported_outputs: List[str] = field(
        default_factory=lambda: [
            "HISTORICAL_EVIDENCE",
            "HISTORICAL_CONTEXT",
            "HISTORICAL_OUTCOME",
            "MEMORY_RELATIONSHIPS",
            "MEMORY_RECURRENCE",
            "LEARNING_HANDOFF",
            "DECISION_CONTEXT",
        ]
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "contract_version": self.contract_version,
            "provider": self.provider,
            "historical_context_available": (
                self.historical_context_available
            ),
            "evidence_available": (
                self.evidence_available
            ),
            "outcome_available": (
                self.outcome_available
            ),
            "learning_handoff_available": (
                self.learning_handoff_available
            ),
            "decision_context_available": (
                self.decision_context_available
            ),
            "direct_decision_allowed": (
                self.direct_decision_allowed
            ),
            "direct_execution_allowed": (
                self.direct_execution_allowed
            ),
            "production_mutation_allowed": (
                self.production_mutation_allowed
            ),
            "decision_authority": (
                self.decision_authority
            ),
            "supported_outputs": list(
                self.supported_outputs
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================================
# MEMORY INTEGRATION SERVICE
# ============================================================================

class MemoryIntegrationService:
    """
    Read-only integration service for Memory.

    Responsibilities:
        - expose provenance
        - expose version identity
        - prepare Learning handoff
        - prepare Decision Context
        - expose integration contract

    It does NOT:
        - calculate trade signals
        - modify production engines
        - place orders
        - approve trades
        - override D13
    """

    def __init__(
        self,
        robomlm_version: str = "",
        schema_version: str = UI_SCHEMA_VERSION,
    ) -> None:

        self.robomlm_version = robomlm_version
        self.schema_version = schema_version

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def build_provenance(
        self,
        record: MemoryRecord,
    ) -> MemoryProvenance:

        return MemoryProvenance(
            memory_id=record.memory_id,
            source_engine=record.source_engine,
            engine_version=record.engine_version,
            schema_version=self.schema_version,
            robomlm_version=self.robomlm_version,
            input_reference=record.input_reference,
            output_reference=record.output_reference,
            source_timestamp=record.timestamp,
        )

    # ------------------------------------------------------------------
    # Version
    # ------------------------------------------------------------------

    def build_version(
        self,
        record: MemoryRecord,
        memory_version: str = "1.0.0",
        parent_version: Optional[str] = None,
    ) -> MemoryVersion:

        return MemoryVersion(
            memory_id=record.memory_id,
            memory_version=memory_version,
            robomlm_version=self.robomlm_version,
            engine_version=record.engine_version,
            schema_version=self.schema_version,
            parent_version=parent_version,
        )

    # ------------------------------------------------------------------
    # Learning handoff
    # ------------------------------------------------------------------

    def build_learning_input(
        self,
        record: MemoryRecord,
        memory_version: str = "1.0.0",
    ) -> MemoryLearningInput:

        provenance = self.build_provenance(
            record
        )

        version = self.build_version(
            record,
            memory_version=memory_version,
        )

        return MemoryLearningHandoffBuilder.build(
            record,
            provenance=provenance,
            version=version,
        )

    # ------------------------------------------------------------------
    # Decision context
    # ------------------------------------------------------------------

    def build_decision_context(
        self,
        record: MemoryRecord,
        memory_version: str = "1.0.0",
    ) -> MemoryDecisionContext:

        provenance = self.build_provenance(
            record
        )

        version = self.build_version(
            record,
            memory_version=memory_version,
        )

        return MemoryDecisionContextBuilder.build(
            record,
            provenance=provenance,
            version=version,
        )

    # ------------------------------------------------------------------
    # Contract
    # ------------------------------------------------------------------

    def contract(self) -> MemoryIntegrationContract:

        return MemoryIntegrationContract(
            decision_authority=DECISION_AUTHORITY,
            direct_decision_allowed=False,
            direct_execution_allowed=False,
            production_mutation_allowed=False,
        )


# ============================================================================
# INTEGRATION UI
# ============================================================================

def _render_memory_provenance(
    st,
    record: Optional[MemoryRecord],
    service: MemoryIntegrationService,
) -> None:
    """Display provenance and version information."""

    st.subheader("Memory Provenance")

    if record is None:

        st.info(
            "Select a memory record to inspect provenance."
        )

        return

    provenance = service.build_provenance(
        record
    )

    version = service.build_version(
        record
    )

    st.write("**Source**")

    st.json(
        {
            "source_engine": provenance.source_engine,
            "engine_version": provenance.engine_version,
            "schema_version": provenance.schema_version,
            "ROBOMLM_version": provenance.robomlm_version,
        }
    )

    st.write("**References**")

    st.json(
        {
            "input_reference": (
                provenance.input_reference
            ),
            "output_reference": (
                provenance.output_reference
            ),
        }
    )

    st.write("**Memory Version**")

    st.json(
        version.to_dict()
    )


# ============================================================================
# LEARNING HANDOFF UI
# ============================================================================

def _render_memory_learning_handoff(
    st,
    record: Optional[MemoryRecord],
    service: MemoryIntegrationService,
) -> None:
    """
    Display the read-only Learning handoff.

    No learning operation is executed by the UI.
    """

    st.subheader("Learning Handoff")

    if record is None:

        st.info(
            "Select a memory record to inspect "
            "its Learning handoff."
        )

        return

    learning_input = (
        service.build_learning_input(
            record
        )
    )

    st.caption(
        "Read-only historical input prepared for "
        "the Learning layer."
    )

    st.json(
        learning_input.to_dict()
    )

    st.warning(
        "The Memory UI does not perform learning updates."
    )


# ============================================================================
# DECISION CONTEXT UI
# ============================================================================

def _render_memory_decision_context(
    st,
    record: Optional[MemoryRecord],
    service: MemoryIntegrationService,
) -> None:
    """
    Display the historical context that can be supplied downstream.

    This is NOT a D13 decision.
    """

    st.subheader("Decision Context")

    if record is None:

        st.info(
            "Select a memory record to inspect "
            "decision context."
        )

        return

    context = (
        service.build_decision_context(
            record
        )
    )

    st.caption(
        "Historical context only. "
        "Final decision authority remains D13."
    )

    st.json(
        context.to_dict()
    )


# ============================================================================
# ARCHITECTURAL BOUNDARY UI
# ============================================================================

def _render_memory_integration_boundary(
    st,
    service: MemoryIntegrationService,
) -> None:
    """Display Memory integration boundaries."""

    st.subheader("Memory Integration Boundary")

    contract = service.contract()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Decision Authority",
            contract.decision_authority,
        )

    with col2:

        st.metric(
            "Direct Decision",
            "NO"
            if not contract.direct_decision_allowed
            else "YES",
        )

    with col3:

        st.metric(
            "Direct Execution",
            "NO"
            if not contract.direct_execution_allowed
            else "YES",
        )

    st.json(
        contract.to_dict()
    )


# ============================================================================
# PART 4 PAGE RENDERER
# ============================================================================

def render_memory_page_part4(
    controller: Optional[MemoryPageController] = None,
    robomlm_version: str = "",
) -> None:
    """
    Memory page renderer with Parts 1–4.

    Part 4 adds:

        - Provenance
        - Version identity
        - Learning handoff
        - Decision context
        - Integration contract
        - D13 authority boundary
    """

    st = _safe_import_streamlit()

    if st is None:

        raise RuntimeError(
            "Streamlit is required to render the Memory page."
        )

    controller = (
        controller
        or MemoryPageController()
    )

    service = MemoryIntegrationService(
        robomlm_version=robomlm_version,
        schema_version=UI_SCHEMA_VERSION,
    )

    filter_controller = MemoryFilterController()

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    _render_header(st)

    _render_architecture_notice(st)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    query = _render_memory_filters(
        st,
        controller,
        filter_controller,
    )

    filtered_records = controller.query(
        query
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    st.divider()

    state = controller.build_state(
        query
    )

    _render_status_summary(
        st,
        state,
    )

    # ------------------------------------------------------------------
    # Selector
    # ------------------------------------------------------------------

    st.divider()

    _render_memory_selector(
        st,
        filtered_records,
        controller,
    )

    selected = (
        controller.get_record(
            controller.selected_memory_id
        )
        if controller.selected_memory_id
        else None
    )

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    st.divider()

    (
        overview_tab,
        history_tab,
        layers_tab,
        relationships_tab,
        recurrence_tab,
        provenance_tab,
        learning_tab,
        decision_context_tab,
        architecture_tab,
    ) = st.tabs(
        [
            "Overview",
            "History",
            "Memory Layers",
            "Relationships",
            "Recurrence",
            "Provenance",
            "Learning",
            "Decision Context",
            "Architecture",
        ]
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    with overview_tab:

        _render_memory_statistics(
            st,
            filtered_records,
        )

        st.divider()

        _render_selected_memory(
            st,
            selected,
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    with history_tab:

        _render_memory_timeline(
            st,
            filtered_records,
            controller,
        )

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    with layers_tab:

        _render_memory_layers(
            st,
            selected,
        )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    with relationships_tab:

        _render_memory_relationships(
            st,
            filtered_records,
        )

    # ------------------------------------------------------------------
    # Recurrence
    # ------------------------------------------------------------------

    with recurrence_tab:

        _render_memory_recurrence(
            st,
            filtered_records,
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    with provenance_tab:

        _render_memory_provenance(
            st,
            selected,
            service,
        )

    # ------------------------------------------------------------------
    # Learning
    # ------------------------------------------------------------------

    with learning_tab:

        _render_memory_learning_handoff(
            st,
            selected,
            service,
        )

    # ------------------------------------------------------------------
    # Decision Context
    # ------------------------------------------------------------------

    with decision_context_tab:

        _render_memory_decision_context(
            st,
            selected,
            service,
        )

    # ------------------------------------------------------------------
    # Architecture
    # ------------------------------------------------------------------

    with architecture_tab:

        _render_memory_integration_boundary(
            st,
            service,
        )


# ============================================================================
# PUBLIC API EXTENSION
# ============================================================================

try:

    __all__.extend(
        [
            "MemoryProvenance",
            "MemoryVersion",
            "MemoryLearningInput",
            "MemoryLearningHandoffBuilder",
            "MemoryDecisionContext",
            "MemoryDecisionContextBuilder",
            "MemoryIntegrationContract",
            "MemoryIntegrationService",
            "_render_memory_provenance",
            "_render_memory_learning_handoff",
            "_render_memory_decision_context",
            "_render_memory_integration_boundary",
            "render_memory_page_part4",
        ]
    )

except NameError:

    __all__ = [
        "MemoryProvenance",
        "MemoryVersion",
        "MemoryLearningInput",
        "MemoryLearningHandoffBuilder",
        "MemoryDecisionContext",
        "MemoryDecisionContextBuilder",
        "MemoryIntegrationContract",
        "MemoryIntegrationService",
        "_render_memory_provenance",
        "_render_memory_learning_handoff",
        "_render_memory_decision_context",
        "_render_memory_integration_boundary",
        "render_memory_page_part4",
    ]
```
```python
# ============================================================================
# PART 5 — MEMORY WORKSPACE / SESSION STATE / INTEGRATED UI
# ============================================================================

# ============================================================================
# SESSION STATE KEYS
# ============================================================================

MEMORY_SESSION_CONTROLLER = (
    "robomlm_memory_controller"
)

MEMORY_SESSION_FILTERS = (
    "robomlm_memory_filters"
)

MEMORY_SESSION_SELECTED = (
    "robomlm_memory_selected"
)

MEMORY_SESSION_INITIALIZED = (
    "robomlm_memory_initialized"
)

MEMORY_SESSION_VIEW = (
    "robomlm_memory_view"
)


# ============================================================================
# MEMORY WORKSPACE STATE
# ============================================================================

@dataclass
class MemoryWorkspaceState:
    """
    Complete UI workspace state.

    This state belongs to the UI layer only.
    It is not the canonical Memory database.
    """

    initialized: bool = False

    selected_memory_id: Optional[str] = None

    active_view: str = "Overview"

    search_text: str = ""

    market: Optional[str] = None
    instrument: Optional[str] = None
    timeframe: Optional[str] = None

    memory_type: Optional[str] = None
    status: Optional[str] = None
    source_engine: Optional[str] = None

    visible_records: int = 0
    total_records: int = 0

    decision_authority: str = DECISION_AUTHORITY

    production_mutation_allowed: bool = False
    direct_engine_control_allowed: bool = False
    direct_broker_control_allowed: bool = False

    warnings: List[str] = field(
        default_factory=list
    )

    messages: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# SESSION INITIALIZATION
# ============================================================================

def _initialize_memory_session(
    st,
) -> None:
    """
    Initialize Memory UI session state.

    The controller is created once per Streamlit session.
    """

    if (
        MEMORY_SESSION_INITIALIZED
        not in st.session_state
    ):

        st.session_state[
            MEMORY_SESSION_CONTROLLER
        ] = MemoryPageController()

        st.session_state[
            MEMORY_SESSION_FILTERS
        ] = MemoryFilterController()

        st.session_state[
            MEMORY_SESSION_SELECTED
        ] = None

        st.session_state[
            MEMORY_SESSION_VIEW
        ] = "Overview"

        st.session_state[
            MEMORY_SESSION_INITIALIZED
        ] = True


# ============================================================================
# SESSION ACCESSORS
# ============================================================================

def _get_memory_controller(
    st,
) -> MemoryPageController:

    _initialize_memory_session(st)

    return st.session_state[
        MEMORY_SESSION_CONTROLLER
    ]


def _get_memory_filter_controller(
    st,
) -> MemoryFilterController:

    _initialize_memory_session(st)

    return st.session_state[
        MEMORY_SESSION_FILTERS
    ]


# ============================================================================
# SESSION RESET
# ============================================================================

def _reset_memory_workspace(
    st,
) -> None:
    """
    Reset only Memory UI workspace state.

    This does NOT delete persistent/canonical memory.
    """

    st.session_state[
        MEMORY_SESSION_SELECTED
    ] = None

    st.session_state[
        MEMORY_SESSION_VIEW
    ] = "Overview"

    st.session_state[
        MEMORY_SESSION_FILTERS
    ] = MemoryFilterController()


# ============================================================================
# SELECTED MEMORY SYNCHRONIZATION
# ============================================================================

def _sync_selected_memory(
    st,
    controller: MemoryPageController,
) -> Optional[MemoryRecord]:
    """
    Synchronize selected memory between controller and Streamlit session.
    """

    session_selected = st.session_state.get(
        MEMORY_SESSION_SELECTED
    )

    controller_selected = (
        controller.selected_memory_id
    )

    selected_id = (
        controller_selected
        or session_selected
    )

    if selected_id:

        record = controller.get_record(
            selected_id
        )

        if record is not None:

            controller.select_memory(
                selected_id
            )

            st.session_state[
                MEMORY_SESSION_SELECTED
            ] = selected_id

            return record

    st.session_state[
        MEMORY_SESSION_SELECTED
    ] = None

    return None


# ============================================================================
# WORKSPACE SUMMARY
# ============================================================================

def _build_memory_workspace_state(
    controller: MemoryPageController,
    filter_controller: MemoryFilterController,
) -> MemoryWorkspaceState:

    query = filter_controller.build_query()

    visible_records = controller.query(
        query
    )

    selected_id = (
        controller.selected_memory_id
    )

    return MemoryWorkspaceState(
        initialized=True,
        selected_memory_id=selected_id,
        search_text=(
            filter_controller.state.search_text
        ),
        market=(
            filter_controller.state.market
        ),
        instrument=(
            filter_controller.state.instrument
        ),
        timeframe=(
            filter_controller.state.timeframe
        ),
        memory_type=(
            filter_controller.state.memory_type.value
            if filter_controller.state.memory_type
            else None
        ),
        status=(
            filter_controller.state.status.value
            if filter_controller.state.status
            else None
        ),
        source_engine=(
            filter_controller.state.source_engine
        ),
        visible_records=len(
            visible_records
        ),
        total_records=len(
            controller.list_records()
        ),
        decision_authority=DECISION_AUTHORITY,
        production_mutation_allowed=False,
        direct_engine_control_allowed=False,
        direct_broker_control_allowed=False,
    )


# ============================================================================
# MEMORY HEALTH SUMMARY
# ============================================================================

@dataclass
class MemoryHealthSummary:
    """
    Descriptive health/availability summary.

    This does not judge trading opportunity quality.
    """

    total_records: int = 0

    available_records: int = 0
    verified_records: int = 0
    stale_records: int = 0
    invalidated_records: int = 0
    archived_records: int = 0

    records_without_source: int = 0
    records_without_timestamp: int = 0

    records_with_evidence: int = 0
    records_with_context: int = 0
    records_with_outcome: int = 0


def build_memory_health_summary(
    records: List[MemoryRecord],
) -> MemoryHealthSummary:
    """
    Build a descriptive Memory data-quality summary.
    """

    summary = MemoryHealthSummary(
        total_records=len(records)
    )

    for record in records:

        if record.status == MemoryStatus.AVAILABLE:
            summary.available_records += 1

        if record.status == MemoryStatus.VERIFIED:
            summary.verified_records += 1

        if record.status == MemoryStatus.STALE:
            summary.stale_records += 1

        if record.status == MemoryStatus.INVALIDATED:
            summary.invalidated_records += 1

        if record.status == MemoryStatus.ARCHIVED:
            summary.archived_records += 1

        if not record.source_engine:
            summary.records_without_source += 1

        if not record.timestamp:
            summary.records_without_timestamp += 1

        if record.evidence:
            summary.records_with_evidence += 1

        if record.context:
            summary.records_with_context += 1

        if record.outcome:
            summary.records_with_outcome += 1

    return summary


# ============================================================================
# HEALTH UI
# ============================================================================

def _render_memory_health(
    st,
    records: List[MemoryRecord],
) -> None:
    """Render descriptive Memory availability summary."""

    st.subheader("Memory Health")

    summary = build_memory_health_summary(
        records
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total",
            summary.total_records,
        )

    with col2:
        st.metric(
            "Available",
            summary.available_records,
        )

    with col3:
        st.metric(
            "Verified",
            summary.verified_records,
        )

    with col4:
        st.metric(
            "Stale",
            summary.stale_records,
        )

    st.write("**Historical Payload Availability**")

    payload_data = {
        "Evidence": summary.records_with_evidence,
        "Context": summary.records_with_context,
        "Outcome": summary.records_with_outcome,
    }

    st.json(payload_data)

    if summary.records_without_source:

        st.warning(
            f"{summary.records_without_source} "
            "memory record(s) have no source engine."
        )

    if summary.invalidated_records:

        st.warning(
            f"{summary.invalidated_records} "
            "memory record(s) are marked INVALIDATED."
        )


# ============================================================================
# MEMORY TYPE DISTRIBUTION
# ============================================================================

def _render_memory_type_distribution(
    st,
    records: List[MemoryRecord],
) -> None:
    """Display memory-type distribution."""

    st.subheader("Memory Composition")

    if not records:

        st.info(
            "No memory records are available."
        )

        return

    statistics = build_memory_statistics(
        records
    )

    if statistics.by_type:

        st.json(
            statistics.by_type
        )

    if statistics.by_market:

        st.write("**Markets**")

        st.json(
            statistics.by_market
        )

    if statistics.by_engine:

        st.write("**Source Engines**")

        st.json(
            statistics.by_engine
        )


# ============================================================================
# MEMORY WORKSPACE HEADER
# ============================================================================

def _render_memory_workspace_header(
    st,
) -> None:

    st.title(
        "Memory"
    )

    st.caption(
        "Historical Market Context & Intelligence Memory"
    )

    st.caption(
        f"Memory UI v{MEMORY_PAGE_VERSION} | "
        f"Decision Authority: {DECISION_AUTHORITY}"
    )

    st.info(
        "Memory preserves historical evidence, context and outcomes. "
        "It supports downstream intelligence but does not itself "
        "issue trading decisions or execute orders."
    )


# ============================================================================
# PAGE CONTROLS
# ============================================================================

def _render_memory_page_controls(
    st,
) -> None:
    """Render workspace controls."""

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Reset Workspace",
            use_container_width=True,
        ):

            _reset_memory_workspace(st)

            st.rerun()

    with col2:

        st.caption(
            "Production mutation: DISABLED"
        )


# ============================================================================
# MEMORY SELECTOR V2
# ============================================================================

def _render_memory_workspace_selector(
    st,
    records: List[MemoryRecord],
    controller: MemoryPageController,
) -> Optional[MemoryRecord]:
    """
    Workspace-level memory selector.

    Selection remains read-only.
    """

    if not records:

        st.info(
            "No records available for selection."
        )

        return None

    options = [
        record.memory_id
        for record in records
    ]

    current_id = (
        controller.selected_memory_id
    )

    if current_id not in options:

        current_id = options[0]

    selected_id = st.selectbox(
        "Memory Record",
        options,
        index=options.index(
            current_id
        ),
        key="memory_workspace_selector",
    )

    record = controller.get_record(
        selected_id
    )

    if record:

        controller.select_memory(
            selected_id
        )

        st.session_state[
            MEMORY_SESSION_SELECTED
        ] = selected_id

    return record


# ============================================================================
# SELECTED MEMORY SUMMARY
# ============================================================================

def _render_memory_summary_card(
    st,
    record: Optional[MemoryRecord],
) -> None:
    """Render compact selected-memory summary."""

    if record is None:

        st.info(
            "No memory record selected."
        )

        return

    st.subheader(
        record.title
        or record.instrument
        or record.memory_id
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.caption("Memory ID")
        st.write(record.memory_id)

    with col2:

        st.caption("Type")
        st.write(record.memory_type.value)

    with col3:

        st.caption("Status")
        st.write(record.status.value)

    with col4:

        st.caption("Source")
        st.write(
            record.source_engine
            or "Unknown"
        )


# ============================================================================
# D13 BOUNDARY CARD
# ============================================================================

def _render_memory_d13_boundary(
    st,
) -> None:
    """
    Explicitly show the D13 authority boundary.
    """

    st.subheader(
        "Decision Authority Boundary"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Decision Authority",
            DECISION_AUTHORITY,
        )

    with col2:

        st.metric(
            "Memory Decision",
            "NO",
        )

    with col3:

        st.metric(
            "Memory Execution",
            "NO",
        )

    st.caption(
        "Memory can provide historical context to downstream "
        "intelligence. Final decision authority remains D13."
    )


# ============================================================================
# WORKSPACE OVERVIEW
# ============================================================================

def _render_memory_workspace_overview(
    st,
    records: List[MemoryRecord],
    selected: Optional[MemoryRecord],
) -> None:

    _render_memory_health(
        st,
        records,
    )

    st.divider()

    _render_memory_type_distribution(
        st,
        records,
    )

    st.divider()

    _render_memory_summary_card(
        st,
        selected,
    )


# ============================================================================
# HISTORY VIEW
# ============================================================================

def _render_memory_history_view(
    st,
    records: List[MemoryRecord],
    controller: MemoryPageController,
) -> None:

    st.subheader(
        "Historical Memory"
    )

    _render_memory_timeline(
        st,
        records,
        controller,
    )


# ============================================================================
# RELATIONSHIP VIEW
# ============================================================================

def _render_memory_relationship_view(
    st,
    records: List[MemoryRecord],
) -> None:

    _render_memory_relationships(
        st,
        records,
    )

    st.divider()

    _render_memory_recurrence(
        st,
        records,
    )


# ============================================================================
# INTEGRATION VIEW
# ============================================================================

def _render_memory_integration_view(
    st,
    selected: Optional[MemoryRecord],
    service: MemoryIntegrationService,
) -> None:

    st.subheader(
        "Downstream Integration"
    )

    _render_memory_provenance(
        st,
        selected,
        service,
    )

    st.divider()

    _render_memory_learning_handoff(
        st,
        selected,
        service,
    )

    st.divider()

    _render_memory_decision_context(
        st,
        selected,
        service,
    )


# ============================================================================
# ARCHITECTURE VIEW
# ============================================================================

def _render_memory_architecture_view(
    st,
    service: MemoryIntegrationService,
) -> None:

    st.subheader(
        "Memory Architecture"
    )

    st.write(
        """
        **Canonical Memory role**

        Market/Data
        → Evidence
        → Historical Memory
        → Context / Relationship / Recurrence
        → Learning / Intelligence Consumers
        → D13 Decision Authority
        """
    )

    st.divider()

    _render_memory_integration_boundary(
        st,
        service,
    )

    st.divider()

    _render_memory_d13_boundary(
        st,
    )

    st.divider()

    st.write(
        "**Production Safety Boundary**"
    )

    st.json(
        {
            "production_mutation_allowed": False,
            "direct_engine_control_allowed": False,
            "direct_broker_control_allowed": False,
            "decision_authority": DECISION_AUTHORITY,
        }
    )


# ============================================================================
# PART 5 COMPLETE PAGE
# ============================================================================

def render_memory_page_complete(
    robomlm_version: str = "",
) -> None:
    """
    Complete Memory workspace renderer.

    Includes Parts 1–5:

        Part 1:
            Memory records / controller / base UI

        Part 2:
            Search / filters / timeline / statistics

        Part 3:
            Relationships / recurrence / comparison / layers

        Part 4:
            Provenance / version / Learning handoff /
            Decision Context / integration boundary

        Part 5:
            Session state / integrated workspace / navigation
    """

    st = _safe_import_streamlit()

    if st is None:

        raise RuntimeError(
            "Streamlit is required to render the Memory page."
        )

    # ------------------------------------------------------------------
    # Initialize session
    # ------------------------------------------------------------------

    _initialize_memory_session(st)

    controller = _get_memory_controller(st)

    filter_controller = (
        _get_memory_filter_controller(st)
    )

    service = MemoryIntegrationService(
        robomlm_version=robomlm_version,
        schema_version=UI_SCHEMA_VERSION,
    )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    _render_memory_workspace_header(
        st
    )

    # ------------------------------------------------------------------
    # Controls
    # ------------------------------------------------------------------

    _render_memory_page_controls(
        st
    )

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    st.divider()

    query = _render_memory_filters(
        st,
        controller,
        filter_controller,
    )

    filtered_records = controller.query(
        query
    )

    # ------------------------------------------------------------------
    # Synchronize selection
    # ------------------------------------------------------------------

    selected = _sync_selected_memory(
        st,
        controller,
    )

    # ------------------------------------------------------------------
    # Workspace selector
    # ------------------------------------------------------------------

    st.divider()

    selected_from_selector = (
        _render_memory_workspace_selector(
            st,
            filtered_records,
            controller,
        )
    )

    if selected_from_selector is not None:

        selected = selected_from_selector

    # ------------------------------------------------------------------
    # Workspace state
    # ------------------------------------------------------------------

    workspace_state = (
        _build_memory_workspace_state(
            controller,
            filter_controller,
        )
    )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Memory",
            workspace_state.total_records,
        )

    with col2:

        st.metric(
            "Visible",
            workspace_state.visible_records,
        )

    with col3:

        st.metric(
            "Selected",
            "YES"
            if workspace_state.selected_memory_id
            else "NO",
        )

    with col4:

        st.metric(
            "Authority",
            workspace_state.decision_authority,
        )

    # ------------------------------------------------------------------
    # Selected summary
    # ------------------------------------------------------------------

    st.divider()

    _render_memory_summary_card(
        st,
        selected,
    )

    # ------------------------------------------------------------------
    # Main workspace tabs
    # ------------------------------------------------------------------

    st.divider()

    (
        overview_tab,
        history_tab,
        layers_tab,
        relationships_tab,
        comparison_tab,
        integration_tab,
        architecture_tab,
    ) = st.tabs(
        [
            "Overview",
            "History",
            "Memory Layers",
            "Relationships",
            "Comparison",
            "Integration",
            "Architecture",
        ]
    )

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    with overview_tab:

        _render_memory_workspace_overview(
            st,
            filtered_records,
            selected,
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    with history_tab:

        _render_memory_history_view(
            st,
            filtered_records,
            controller,
        )

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    with layers_tab:

        _render_memory_layers(
            st,
            selected,
        )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    with relationships_tab:

        _render_memory_relationship_view(
            st,
            filtered_records,
        )

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    with comparison_tab:

        if len(filtered_records) >= 2:

            options = [
                record.memory_id
                for record in filtered_records
            ]

            source_id = st.selectbox(
                "Source Memory",
                options,
                key="memory_part5_source",
            )

            target_options = [
                item
                for item in options
                if item != source_id
            ]

            if target_options:

                target_id = st.selectbox(
                    "Target Memory",
                    target_options,
                    key="memory_part5_target",
                )

                source_record = (
                    controller.get_record(
                        source_id
                    )
                )

                target_record = (
                    controller.get_record(
                        target_id
                    )
                )

                _render_memory_context_comparison(
                    st,
                    source_record,
                    target_record,
                )

        else:

            st.info(
                "At least two memory records are required "
                "for historical comparison."
            )

    # ------------------------------------------------------------------
    # Integration
    # ------------------------------------------------------------------

    with integration_tab:

        _render_memory_integration_view(
            st,
            selected,
            service,
        )

    # ------------------------------------------------------------------
    # Architecture
    # ------------------------------------------------------------------

    with architecture_tab:

        _render_memory_architecture_view(
            st,
            service,
        )


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================

render_memory_page_v5 = (
    render_memory_page_complete
)


render_memory_page_part5 = (
    render_memory_page_complete
)


# ============================================================================
# PUBLIC API EXTENSION
# ============================================================================

try:

    __all__.extend(
        [
            "MEMORY_SESSION_CONTROLLER",
            "MEMORY_SESSION_FILTERS",
            "MEMORY_SESSION_SELECTED",
            "MEMORY_SESSION_INITIALIZED",
            "MEMORY_SESSION_VIEW",
            "MemoryWorkspaceState",
            "MemoryHealthSummary",
            "build_memory_health_summary",
            "_initialize_memory_session",
            "_get_memory_controller",
            "_get_memory_filter_controller",
            "_reset_memory_workspace",
            "_sync_selected_memory",
            "_build_memory_workspace_state",
            "_render_memory_health",
            "_render_memory_type_distribution",
            "_render_memory_workspace_header",
            "_render_memory_page_controls",
            "_render_memory_workspace_selector",
            "_render_memory_summary_card",
            "_render_memory_d13_boundary",
            "_render_memory_workspace_overview",
            "_render_memory_history_view",
            "_render_memory_relationship_view",
            "_render_memory_integration_view",
            "_render_memory_architecture_view",
            "render_memory_page_complete",
            "render_memory_page_v5",
            "render_memory_page_part5",
        ]
    )

except NameError:

    __all__ = [
        "MEMORY_SESSION_CONTROLLER",
        "MEMORY_SESSION_FILTERS",
        "MEMORY_SESSION_SELECTED",
        "MEMORY_SESSION_INITIALIZED",
        "MEMORY_SESSION_VIEW",
        "MemoryWorkspaceState",
        "MemoryHealthSummary",
        "build_memory_health_summary",
        "_initialize_memory_session",
        "_get_memory_controller",
        "_get_memory_filter_controller",
        "_reset_memory_workspace",
        "_sync_selected_memory",
        "_build_memory_workspace_state",
        "_render_memory_health",
        "_render_memory_type_distribution",
        "_render_memory_workspace_header",
        "_render_memory_page_controls",
        "_render_memory_workspace_selector",
        "_render_memory_summary_card",
        "_render_memory_d13_boundary",
        "_render_memory_workspace_overview",
        "_render_memory_history_view",
        "_render_memory_relationship_view",
        "_render_memory_integration_view",
        "_render_memory_architecture_view",
        "render_memory_page_complete",
        "render_memory_page_v5",
        "render_memory_page_part5",
    ]
```
