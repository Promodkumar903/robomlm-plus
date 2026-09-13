"""
ROBOMLM_PLUS
Research Page — Part 1
Path:
    app/ui/research/research_page.py

Purpose:
    Research/Admin presentation foundation.

Architecture:
    UI → Research Application/API layer
    UI MUST NOT directly control:
        - production formulas
        - intelligence engines
        - broker/execution
        - CAS
        - D13 decision authority

Research lifecycle:
    RESEARCH → EXPERIMENT → VALIDATION → STRESS_TEST
             → ADMIN_REVIEW → CANDIDATE → VERSION
             → CONTROLLED_DEPLOYMENT

Part 1:
    - Research page constants
    - Research lifecycle state
    - Research record
    - UI-safe research view model
    - Research page controller
    - Streamlit rendering foundation

NOTE:
    This module is intentionally presentation/control oriented.
    It does not implement research formulas or production intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# PAGE CONSTANTS
# ============================================================

PAGE_TITLE = "Research"
PAGE_SUBTITLE = "Research, Validation & Controlled Intelligence Evolution"

RESEARCH_VERSION = "1.0.0"
UI_SCHEMA_VERSION = "1.0.0"

DECISION_AUTHORITY = "D13"

PRODUCTION_MUTATION_ALLOWED = False
DIRECT_ENGINE_CONTROL_ALLOWED = False
DIRECT_BROKER_CONTROL_ALLOWED = False


# ============================================================
# RESEARCH LIFECYCLE
# ============================================================

class ResearchStatus(str, Enum):
    RESEARCH = "RESEARCH"
    EXPERIMENT = "EXPERIMENT"
    VALIDATION = "VALIDATION"
    STRESS_TEST = "STRESS_TEST"
    ADMIN_REVIEW = "ADMIN_REVIEW"
    CANDIDATE = "CANDIDATE"
    VERSION = "VERSION"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    ROLLED_BACK = "ROLLED_BACK"


# ============================================================
# RESEARCH RECORD
# ============================================================

@dataclass
class ResearchRecord:
    """
    UI-safe representation of a research item.

    This object describes research.
    It does not execute research.
    """

    research_id: str

    hypothesis: str = ""

    dataset: str = ""

    engine_version: str = ""

    experiment: str = ""

    metrics: Dict[str, Any] = field(default_factory=dict)

    validation: Dict[str, Any] = field(default_factory=dict)

    stress_tests: Dict[str, Any] = field(default_factory=dict)

    result: str = ""

    review_status: ResearchStatus = ResearchStatus.RESEARCH

    candidate_version: str = ""

    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "research_id": self.research_id,
            "hypothesis": self.hypothesis,
            "dataset": self.dataset,
            "engine_version": self.engine_version,
            "experiment": self.experiment,
            "metrics": dict(self.metrics),
            "validation": dict(self.validation),
            "stress_tests": dict(self.stress_tests),
            "result": self.result,
            "review_status": self.review_status.value,
            "candidate_version": self.candidate_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }


# ============================================================
# UI VIEW MODEL
# ============================================================

@dataclass
class ResearchPageState:
    """
    State consumed by the Research UI.

    The UI receives state; it does not become the intelligence
    engine itself.
    """

    records: List[ResearchRecord] = field(default_factory=list)

    selected_research_id: Optional[str] = None

    active_status: Optional[ResearchStatus] = None

    can_create_research: bool = True

    can_run_experiment: bool = False

    can_validate: bool = False

    can_stress_test: bool = False

    can_admin_review: bool = False

    can_deploy: bool = False

    production_mutation_allowed: bool = False

    decision_authority: str = DECISION_AUTHORITY

    messages: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# RESEARCH PAGE CONTROLLER
# ============================================================

class ResearchPageController:
    """
    Presentation/controller boundary for Research.

    IMPORTANT:
        This controller does not execute production intelligence.

    Actual research execution, validation, versioning and deployment
    must be delegated to the appropriate application/service layer.
    """

    def __init__(self) -> None:
        self._records: Dict[str, ResearchRecord] = {}

    # --------------------------------------------------------
    # READ
    # --------------------------------------------------------

    def list_records(self) -> List[ResearchRecord]:
        return list(self._records.values())

    def get_record(
        self,
        research_id: str,
    ) -> Optional[ResearchRecord]:

        return self._records.get(research_id)

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def create_research(
        self,
        research_id: str,
        hypothesis: str,
        dataset: str = "",
        engine_version: str = "",
        experiment: str = "",
    ) -> ResearchRecord:
        """
        Create a research definition.

        No production code is changed here.
        """

        research_id = str(research_id).strip()

        if not research_id:
            raise ValueError("research_id is required")

        if research_id in self._records:
            raise ValueError(
                f"Research already exists: {research_id}"
            )

        record = ResearchRecord(
            research_id=research_id,
            hypothesis=str(hypothesis).strip(),
            dataset=str(dataset).strip(),
            engine_version=str(engine_version).strip(),
            experiment=str(experiment).strip(),
            review_status=ResearchStatus.RESEARCH,
        )

        self._records[research_id] = record

        return record

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    def select_research(
        self,
        research_id: Optional[str],
    ) -> Optional[ResearchRecord]:

        if research_id is None:
            return None

        return self.get_record(research_id)

    # --------------------------------------------------------
    # PAGE STATE
    # --------------------------------------------------------

    def build_state(
        self,
        selected_research_id: Optional[str] = None,
        active_status: Optional[ResearchStatus] = None,
    ) -> ResearchPageState:

        selected = self.select_research(selected_research_id)

        messages: List[str] = []
        warnings: List[str] = []

        if selected is not None:
            messages.append(
                f"Research selected: {selected.research_id}"
            )

        warnings.append(
            "Research UI cannot directly modify production intelligence."
        )

        return ResearchPageState(
            records=self.list_records(),
            selected_research_id=(
                selected.research_id
                if selected is not None
                else None
            ),
            active_status=active_status,
            can_create_research=True,
            can_run_experiment=False,
            can_validate=False,
            can_stress_test=False,
            can_admin_review=False,
            can_deploy=False,
            production_mutation_allowed=False,
            decision_authority=DECISION_AUTHORITY,
            messages=messages,
            warnings=warnings,
        )


# ============================================================
# STREAMLIT UI HELPERS
# ============================================================

def _safe_import_streamlit():
    """
    Import Streamlit lazily.

    Keeps the module importable in environments where Streamlit
    is not installed, such as unit-test environments.
    """

    try:
        import streamlit as st

        return st

    except ImportError as exc:
        raise RuntimeError(
            "Streamlit is required to render Research Page."
        ) from exc


def _render_header(st) -> None:
    st.title(PAGE_TITLE)

    st.caption(PAGE_SUBTITLE)

    st.divider()


def _render_architecture_notice(st) -> None:
    st.info(
        "Research is a controlled intelligence-evolution layer. "
        "Research experiments must not directly modify production "
        "intelligence, execution, broker state, CAS, or D13 authority."
    )


def _render_status_summary(
    st,
    state: ResearchPageState,
) -> None:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Research Items",
            len(state.records),
        )

    with col2:
        st.metric(
            "Selected",
            (
                state.selected_research_id
                if state.selected_research_id
                else "None"
            ),
        )

    with col3:
        st.metric(
            "Decision Authority",
            state.decision_authority,
        )

    with col4:
        st.metric(
            "Production Mutation",
            "BLOCKED",
        )


def _render_research_list(
    st,
    state: ResearchPageState,
) -> None:

    st.subheader("Research Registry")

    if not state.records:
        st.info(
            "No research records available."
        )
        return

    for record in state.records:

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [3, 2, 1]
            )

            with col1:
                st.write(
                    f"**{record.research_id}**"
                )

                if record.hypothesis:
                    st.caption(
                        record.hypothesis
                    )

            with col2:
                st.write(
                    record.review_status.value
                )

            with col3:
                st.write(
                    record.engine_version or "-"
                )


def _render_selected_research(
    st,
    state: ResearchPageState,
) -> None:

    if not state.selected_research_id:
        return

    record = next(
        (
            item
            for item in state.records
            if item.research_id
            == state.selected_research_id
        ),
        None,
    )

    if record is None:
        return

    st.subheader("Selected Research")

    st.write(
        f"**Research ID:** {record.research_id}"
    )

    st.write(
        f"**Hypothesis:** "
        f"{record.hypothesis or '-'}"
    )

    st.write(
        f"**Dataset:** "
        f"{record.dataset or '-'}"
    )

    st.write(
        f"**Engine Version:** "
        f"{record.engine_version or '-'}"
    )

    st.write(
        f"**Experiment:** "
        f"{record.experiment or '-'}"
    )

    st.write(
        f"**Status:** "
        f"{record.review_status.value}"
    )


# ============================================================
# MAIN PAGE
# ============================================================

def render_research_page(
    controller: Optional[ResearchPageController] = None,
) -> None:
    """
    Main Streamlit entry point.

    Example:

        from app.ui.research.research_page import (
            render_research_page,
        )

        render_research_page()
    """

    st = _safe_import_streamlit()

    if controller is None:
        controller = ResearchPageController()

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    _render_header(st)

    # --------------------------------------------------------
    # Architecture boundary
    # --------------------------------------------------------

    _render_architecture_notice(st)

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    state = controller.build_state()

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    _render_status_summary(
        st,
        state,
    )

    st.divider()

    # --------------------------------------------------------
    # Registry
    # --------------------------------------------------------

    _render_research_list(
        st,
        state,
    )

    # --------------------------------------------------------
    # Selected item
    # --------------------------------------------------------

    _render_selected_research(
        st,
        state,
    )

    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    if state.warnings:

        st.divider()

        for warning in state.warnings:
            st.warning(warning)


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "PAGE_TITLE",
    "PAGE_SUBTITLE",
    "RESEARCH_VERSION",
    "UI_SCHEMA_VERSION",
    "DECISION_AUTHORITY",
    "ResearchStatus",
    "ResearchRecord",
    "ResearchPageState",
    "ResearchPageController",
    "render_research_page",
]
```python
# ============================================================
# PART 2 — RESEARCH WORKFLOW & LIFECYCLE UI
# ============================================================

# ------------------------------------------------------------
# LIFECYCLE ORDER
# ------------------------------------------------------------

RESEARCH_LIFECYCLE_ORDER = [
    ResearchStatus.RESEARCH,
    ResearchStatus.EXPERIMENT,
    ResearchStatus.VALIDATION,
    ResearchStatus.STRESS_TEST,
    ResearchStatus.ADMIN_REVIEW,
    ResearchStatus.CANDIDATE,
    ResearchStatus.VERSION,
    ResearchStatus.APPROVED,
    ResearchStatus.DEPLOYED,
]


# ------------------------------------------------------------
# ALLOWED LIFECYCLE TRANSITIONS
# ------------------------------------------------------------

ALLOWED_RESEARCH_TRANSITIONS = {
    ResearchStatus.RESEARCH: {
        ResearchStatus.EXPERIMENT,
    },

    ResearchStatus.EXPERIMENT: {
        ResearchStatus.VALIDATION,
    },

    ResearchStatus.VALIDATION: {
        ResearchStatus.STRESS_TEST,
    },

    ResearchStatus.STRESS_TEST: {
        ResearchStatus.ADMIN_REVIEW,
    },

    ResearchStatus.ADMIN_REVIEW: {
        ResearchStatus.CANDIDATE,
    },

    ResearchStatus.CANDIDATE: {
        ResearchStatus.VERSION,
    },

    ResearchStatus.VERSION: {
        ResearchStatus.APPROVED,
    },

    ResearchStatus.APPROVED: {
        ResearchStatus.DEPLOYED,
    },

    ResearchStatus.DEPLOYED: {
        ResearchStatus.ROLLED_BACK,
    },

    ResearchStatus.ROLLED_BACK: set(),
}


# ------------------------------------------------------------
# RESEARCH WORKFLOW RESULT
# ------------------------------------------------------------

@dataclass
class ResearchWorkflowResult:
    """
    Safe result returned by Research UI workflow operations.

    This does not mean that an experiment or deployment was
    actually executed. It only represents the UI/application
    workflow state.
    """

    success: bool

    research_id: str

    previous_status: Optional[ResearchStatus] = None

    current_status: Optional[ResearchStatus] = None

    message: str = ""

    blockers: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "research_id": self.research_id,
            "previous_status": (
                self.previous_status.value
                if self.previous_status
                else None
            ),
            "current_status": (
                self.current_status.value
                if self.current_status
                else None
            ),
            "message": self.message,
            "blockers": list(self.blockers),
            "metadata": dict(self.metadata),
        }


# ------------------------------------------------------------
# RESEARCH INPUT CONTRACT
# ------------------------------------------------------------

@dataclass
class ResearchInput:
    """
    Structured research definition.

    This is intentionally formula-neutral.

    Research formulas must come from the approved research /
    formula registry layer and must not be invented by this UI.
    """

    research_id: str

    hypothesis: str

    dataset: str

    engine_version: str

    experiment: str

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    validation: Dict[str, Any] = field(
        default_factory=dict
    )

    stress_tests: Dict[str, Any] = field(
        default_factory=dict
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> List[str]:

        blockers: List[str] = []

        if not self.research_id.strip():
            blockers.append(
                "research_id is required"
            )

        if not self.hypothesis.strip():
            blockers.append(
                "hypothesis is required"
            )

        if not self.dataset.strip():
            blockers.append(
                "dataset is required"
            )

        if not self.engine_version.strip():
            blockers.append(
                "engine_version is required"
            )

        if not self.experiment.strip():
            blockers.append(
                "experiment is required"
            )

        return blockers


# ============================================================
# CONTROLLER EXTENSIONS
# ============================================================

def _controller_transition(
    controller: ResearchPageController,
    research_id: str,
    target_status: ResearchStatus,
) -> ResearchWorkflowResult:
    """
    Controlled lifecycle transition.

    The UI can request a transition, but this function does not
    execute production deployment or modify production formulas.
    """

    record = controller.get_record(
        research_id
    )

    if record is None:
        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            message="Research record not found.",
            blockers=[
                "Unknown research_id"
            ],
        )

    current_status = record.review_status

    allowed_targets = (
        ALLOWED_RESEARCH_TRANSITIONS.get(
            current_status,
            set(),
        )
    )

    if target_status not in allowed_targets:

        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            previous_status=current_status,
            current_status=current_status,
            message=(
                f"Invalid lifecycle transition: "
                f"{current_status.value} → "
                f"{target_status.value}"
            ),
            blockers=[
                "Lifecycle transition is not allowed."
            ],
        )

    # --------------------------------------------------------
    # Production deployment protection
    # --------------------------------------------------------

    if target_status == ResearchStatus.DEPLOYED:

        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            previous_status=current_status,
            current_status=current_status,
            message=(
                "Production deployment cannot be performed "
                "from Research UI."
            ),
            blockers=[
                "Deployment must be handled by the controlled "
                "application/deployment layer.",
                "Research UI cannot mutate production.",
            ],
        )

    record.review_status = target_status
    record.updated_at = (
        datetime.now(timezone.utc).isoformat()
    )

    return ResearchWorkflowResult(
        success=True,
        research_id=research_id,
        previous_status=current_status,
        current_status=target_status,
        message=(
            f"Research moved from "
            f"{current_status.value} to "
            f"{target_status.value}."
        ),
    )


# ------------------------------------------------------------
# ATTACH METHODS TO EXISTING CONTROLLER
# ------------------------------------------------------------

def controller_transition(
    self: ResearchPageController,
    research_id: str,
    target_status: ResearchStatus,
) -> ResearchWorkflowResult:

    return _controller_transition(
        self,
        research_id,
        target_status,
    )


def controller_update_research(
    self: ResearchPageController,
    research_id: str,
    *,
    hypothesis: Optional[str] = None,
    dataset: Optional[str] = None,
    engine_version: Optional[str] = None,
    experiment: Optional[str] = None,
) -> ResearchWorkflowResult:

    record = self.get_record(
        research_id
    )

    if record is None:

        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            message="Research record not found.",
            blockers=[
                "Unknown research_id"
            ],
        )

    # --------------------------------------------------------
    # Production safety
    # --------------------------------------------------------

    if record.review_status in {
        ResearchStatus.APPROVED,
        ResearchStatus.DEPLOYED,
    }:

        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            previous_status=record.review_status,
            current_status=record.review_status,
            message=(
                "Approved/deployed research cannot be "
                "edited through the Research UI."
            ),
            blockers=[
                "Create a new research/version instead."
            ],
        )

    if hypothesis is not None:
        record.hypothesis = hypothesis.strip()

    if dataset is not None:
        record.dataset = dataset.strip()

    if engine_version is not None:
        record.engine_version = engine_version.strip()

    if experiment is not None:
        record.experiment = experiment.strip()

    record.updated_at = (
        datetime.now(timezone.utc).isoformat()
    )

    return ResearchWorkflowResult(
        success=True,
        research_id=research_id,
        previous_status=record.review_status,
        current_status=record.review_status,
        message="Research definition updated.",
    )


# ------------------------------------------------------------
# Bind methods without replacing controller class
# ------------------------------------------------------------

ResearchPageController.transition = (
    controller_transition
)

ResearchPageController.update_research = (
    controller_update_research
)


# ============================================================
# UI — CREATE RESEARCH FORM
# ============================================================

def _render_create_research_form(
    st,
    controller: ResearchPageController,
) -> None:

    st.subheader("Create Research")

    with st.form(
        "robomlm_create_research_form",
        clear_on_submit=False,
    ):

        research_id = st.text_input(
            "Research ID",
            placeholder="RESEARCH-001",
        )

        hypothesis = st.text_area(
            "Hypothesis",
            placeholder=(
                "Define the research hypothesis "
                "to be tested."
            ),
        )

        dataset = st.text_input(
            "Dataset",
            placeholder=(
                "Dataset / market sample / "
                "historical period"
            ),
        )

        engine_version = st.text_input(
            "Engine Version",
            placeholder="Engine version under research",
        )

        experiment = st.text_area(
            "Experiment",
            placeholder=(
                "Describe the experiment design, "
                "not the production implementation."
            ),
        )

        submitted = st.form_submit_button(
            "Create Research"
        )

    if not submitted:
        return

    research_input = ResearchInput(
        research_id=research_id,
        hypothesis=hypothesis,
        dataset=dataset,
        engine_version=engine_version,
        experiment=experiment,
    )

    blockers = research_input.validate()

    if blockers:

        for blocker in blockers:
            st.error(blocker)

        return

    try:

        record = controller.create_research(
            research_id=research_input.research_id,
            hypothesis=research_input.hypothesis,
            dataset=research_input.dataset,
            engine_version=research_input.engine_version,
            experiment=research_input.experiment,
        )

        st.success(
            f"Research {record.research_id} created."
        )

    except ValueError as exc:

        st.error(str(exc))


# ============================================================
# UI — LIFECYCLE
# ============================================================

def _render_lifecycle(
    st,
    record: ResearchRecord,
) -> None:

    st.subheader("Research Lifecycle")

    current_index = (
        RESEARCH_LIFECYCLE_ORDER.index(
            record.review_status
        )
        if record.review_status
        in RESEARCH_LIFECYCLE_ORDER
        else -1
    )

    lifecycle_labels = [
        status.value
        for status in RESEARCH_LIFECYCLE_ORDER
    ]

    st.write(
        " → ".join(lifecycle_labels)
    )

    if current_index >= 0:

        st.progress(
            (current_index + 1)
            / len(RESEARCH_LIFECYCLE_ORDER)
        )

    st.caption(
        f"Current state: "
        f"{record.review_status.value}"
    )


# ============================================================
# UI — RESEARCH DETAIL
# ============================================================

def _render_research_detail(
    st,
    controller: ResearchPageController,
    record: ResearchRecord,
) -> None:

    st.subheader("Research Detail")

    st.write(
        f"**Research ID:** {record.research_id}"
    )

    st.write(
        f"**Hypothesis:** "
        f"{record.hypothesis or '-'}"
    )

    st.write(
        f"**Dataset:** "
        f"{record.dataset or '-'}"
    )

    st.write(
        f"**Engine Version:** "
        f"{record.engine_version or '-'}"
    )

    st.write(
        f"**Experiment:** "
        f"{record.experiment or '-'}"
    )

    _render_lifecycle(
        st,
        record,
    )


# ============================================================
# UI — NEXT ACTIONS
# ============================================================

def _render_next_actions(
    st,
    controller: ResearchPageController,
    record: ResearchRecord,
) -> None:

    st.subheader("Next Research Action")

    current_status = record.review_status

    allowed = ALLOWED_RESEARCH_TRANSITIONS.get(
        current_status,
        set(),
    )

    if not allowed:

        st.info(
            "No further UI lifecycle transition "
            "is available from the current state."
        )

        return

    for target_status in sorted(
        allowed,
        key=lambda item: RESEARCH_LIFECYCLE_ORDER.index(item)
        if item in RESEARCH_LIFECYCLE_ORDER
        else 999,
    ):

        # ----------------------------------------------------
        # Deployment is intentionally blocked.
        # ----------------------------------------------------

        if target_status == ResearchStatus.DEPLOYED:

            st.warning(
                "DEPLOYED is controlled outside the Research UI."
            )

            continue

        button_key = (
            f"research_transition_"
            f"{record.research_id}_"
            f"{target_status.value}"
        )

        if st.button(
            f"Move to {target_status.value}",
            key=button_key,
        ):

            result = controller.transition(
                record.research_id,
                target_status,
            )

            if result.success:

                st.success(
                    result.message
                )

                st.rerun()

            else:

                st.error(
                    result.message
                )

                for blocker in result.blockers:
                    st.warning(blocker)


# ============================================================
# UI — GOVERNANCE PANEL
# ============================================================

def _render_governance_panel(
    st,
    state: ResearchPageState,
) -> None:

    st.subheader("Governance")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "**Decision Authority**"
        )

        st.code(
            state.decision_authority
        )

    with col2:

        st.write(
            "**Production Mutation**"
        )

        st.error(
            "BLOCKED"
        )

    st.caption(
        "Research UI is a controlled research/admin "
        "presentation layer. Production changes require "
        "the approved deployment pipeline."
    )


# ============================================================
# UI — FULL PART 2 WORKFLOW
# ============================================================

def render_research_workflow(
    controller: Optional[ResearchPageController] = None,
) -> None:
    """
    Part 2 workflow renderer.

    This can be called from the main Research page after
    the Part 1 foundation renderer.
    """

    st = _safe_import_streamlit()

    if controller is None:
        controller = ResearchPageController()

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    _render_create_research_form(
        st,
        controller,
    )

    st.divider()

    # --------------------------------------------------------
    # Registry
    # --------------------------------------------------------

    records = controller.list_records()

    if not records:

        st.info(
            "Create a research item to begin the "
            "controlled research lifecycle."
        )

        _render_governance_panel(
            st,
            controller.build_state(),
        )

        return

    # --------------------------------------------------------
    # Selection
    # --------------------------------------------------------

    research_ids = [
        record.research_id
        for record in records
    ]

    selected_id = st.selectbox(
        "Select Research",
        research_ids,
    )

    record = controller.get_record(
        selected_id
    )

    if record is None:
        return

    # --------------------------------------------------------
    # Detail
    # --------------------------------------------------------

    _render_research_detail(
        st,
        controller,
        record,
    )

    st.divider()

    # --------------------------------------------------------
    # Next action
    # --------------------------------------------------------

    _render_next_actions(
        st,
        controller,
        record,
    )

    st.divider()

    # --------------------------------------------------------
    # Governance
    # --------------------------------------------------------

    _render_governance_panel(
        st,
        controller.build_state(
            selected_research_id=record.research_id,
            active_status=record.review_status,
        ),
    )


# ============================================================
# EXTENDED PUBLIC API
# ============================================================

__all__.extend([
    "RESEARCH_LIFECYCLE_ORDER",
    "ALLOWED_RESEARCH_TRANSITIONS",
    "ResearchWorkflowResult",
    "ResearchInput",
    "render_research_workflow",
])
```
```python
# ============================================================
# PART 3 — EXPERIMENT / VALIDATION / STRESS TEST
# ============================================================

# ============================================================
# RESULT STATUS
# ============================================================

class ResearchResultStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    INSUFFICIENT = "INSUFFICIENT"
    PASS = "PASS"
    FAIL = "FAIL"
    INCONCLUSIVE = "INCONCLUSIVE"


# ============================================================
# EXPERIMENT RESULT
# ============================================================

@dataclass
class ExperimentResult:
    """
    Research experiment output.

    This is a result container only.

    The Research UI does not calculate the experiment itself.
    """

    research_id: str

    status: ResearchResultStatus = (
        ResearchResultStatus.NOT_RUN
    )

    experiment_id: str = ""

    dataset_reference: str = ""

    sample_size: int = 0

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    observations: List[str] = field(
        default_factory=list
    )

    limitations: List[str] = field(
        default_factory=list
    )

    result_summary: str = ""

    executed_at: Optional[str] = None

    engine_version: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "status": self.status.value,
            "experiment_id": self.experiment_id,
            "dataset_reference": (
                self.dataset_reference
            ),
            "sample_size": self.sample_size,
            "metrics": dict(self.metrics),
            "observations": list(self.observations),
            "limitations": list(self.limitations),
            "result_summary": self.result_summary,
            "executed_at": self.executed_at,
            "engine_version": self.engine_version,
            "metadata": dict(self.metadata),
        }


# ============================================================
# VALIDATION RESULT
# ============================================================

@dataclass
class ValidationResult:
    """
    Validation output.

    Validation criteria are supplied by the research /
    validation layer. The UI does not manufacture pass/fail
    formulas.
    """

    research_id: str

    status: ResearchResultStatus = (
        ResearchResultStatus.NOT_RUN
    )

    validation_id: str = ""

    criteria: Dict[str, Any] = field(
        default_factory=dict
    )

    measured_metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    passed_checks: List[str] = field(
        default_factory=list
    )

    failed_checks: List[str] = field(
        default_factory=list
    )

    unresolved_checks: List[str] = field(
        default_factory=list
    )

    conclusion: str = ""

    evidence_reference: str = ""

    validated_at: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "status": self.status.value,
            "validation_id": self.validation_id,
            "criteria": dict(self.criteria),
            "measured_metrics": dict(
                self.measured_metrics
            ),
            "passed_checks": list(
                self.passed_checks
            ),
            "failed_checks": list(
                self.failed_checks
            ),
            "unresolved_checks": list(
                self.unresolved_checks
            ),
            "conclusion": self.conclusion,
            "evidence_reference": (
                self.evidence_reference
            ),
            "validated_at": self.validated_at,
            "metadata": dict(self.metadata),
        }


# ============================================================
# STRESS TEST RESULT
# ============================================================

@dataclass
class StressTestResult:
    """
    Stress-test output.

    Stress testing is represented here, not implemented here.
    """

    research_id: str

    status: ResearchResultStatus = (
        ResearchResultStatus.NOT_RUN
    )

    stress_test_id: str = ""

    scenarios: Dict[str, Any] = field(
        default_factory=dict
    )

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    passed_scenarios: List[str] = field(
        default_factory=list
    )

    failed_scenarios: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    conclusion: str = ""

    tested_at: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "status": self.status.value,
            "stress_test_id": self.stress_test_id,
            "scenarios": dict(self.scenarios),
            "metrics": dict(self.metrics),
            "passed_scenarios": list(
                self.passed_scenarios
            ),
            "failed_scenarios": list(
                self.failed_scenarios
            ),
            "warnings": list(self.warnings),
            "conclusion": self.conclusion,
            "tested_at": self.tested_at,
            "metadata": dict(self.metadata),
        }


# ============================================================
# RESEARCH EVIDENCE PACKAGE
# ============================================================

@dataclass
class ResearchEvidencePackage:
    """
    Consolidated evidence presented to the Research UI.

    This package preserves traceability between:
        research
        experiment
        validation
        stress testing

    It does not itself approve deployment.
    """

    research_id: str

    experiment: Optional[ExperimentResult] = None

    validation: Optional[ValidationResult] = None

    stress_test: Optional[StressTestResult] = None

    source_references: List[str] = field(
        default_factory=list
    )

    evidence_quality: Optional[float] = None

    confidence: Optional[float] = None

    contradictions: List[str] = field(
        default_factory=list
    )

    uncertainties: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "experiment": (
                self.experiment.to_dict()
                if self.experiment
                else None
            ),
            "validation": (
                self.validation.to_dict()
                if self.validation
                else None
            ),
            "stress_test": (
                self.stress_test.to_dict()
                if self.stress_test
                else None
            ),
            "source_references": list(
                self.source_references
            ),
            "evidence_quality": (
                self.evidence_quality
            ),
            "confidence": self.confidence,
            "contradictions": list(
                self.contradictions
            ),
            "uncertainties": list(
                self.uncertainties
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# RESEARCH RESULTS STORE
# ============================================================

class ResearchResultsStore:
    """
    In-memory result store for the UI/application boundary.

    Production implementation can later replace this with the
    appropriate persistence/application service.

    No production intelligence is changed here.
    """

    def __init__(self) -> None:

        self._experiments: Dict[
            str,
            ExperimentResult,
        ] = {}

        self._validations: Dict[
            str,
            ValidationResult,
        ] = {}

        self._stress_tests: Dict[
            str,
            StressTestResult,
        ] = {}

    # --------------------------------------------------------
    # EXPERIMENT
    # --------------------------------------------------------

    def save_experiment(
        self,
        result: ExperimentResult,
    ) -> None:

        self._experiments[
            result.research_id
        ] = result

    def get_experiment(
        self,
        research_id: str,
    ) -> Optional[ExperimentResult]:

        return self._experiments.get(
            research_id
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    def save_validation(
        self,
        result: ValidationResult,
    ) -> None:

        self._validations[
            result.research_id
        ] = result

    def get_validation(
        self,
        research_id: str,
    ) -> Optional[ValidationResult]:

        return self._validations.get(
            research_id
        )

    # --------------------------------------------------------
    # STRESS TEST
    # --------------------------------------------------------

    def save_stress_test(
        self,
        result: StressTestResult,
    ) -> None:

        self._stress_tests[
            result.research_id
        ] = result

    def get_stress_test(
        self,
        research_id: str,
    ) -> Optional[StressTestResult]:

        return self._stress_tests.get(
            research_id
        )

    # --------------------------------------------------------
    # EVIDENCE PACKAGE
    # --------------------------------------------------------

    def build_evidence_package(
        self,
        research_id: str,
    ) -> ResearchEvidencePackage:

        return ResearchEvidencePackage(
            research_id=research_id,
            experiment=self.get_experiment(
                research_id
            ),
            validation=self.get_validation(
                research_id
            ),
            stress_test=self.get_stress_test(
                research_id
            ),
        )


# ============================================================
# UI HELPERS
# ============================================================

def _format_result_status(
    status: ResearchResultStatus,
) -> str:

    return status.value.replace(
        "_",
        " ",
    )


def _render_metric_dictionary(
    st,
    metrics: Dict[str, Any],
) -> None:

    if not metrics:

        st.caption(
            "No metrics available."
        )

        return

    columns = st.columns(
        min(
            max(len(metrics), 1),
            4,
        )
    )

    for index, (name, value) in enumerate(
        metrics.items()
    ):

        column = columns[
            index % len(columns)
        ]

        with column:

            if isinstance(
                value,
                (int, float),
            ):

                st.metric(
                    name,
                    value,
                )

            else:

                st.metric(
                    name,
                    str(value),
                )


# ============================================================
# UI — EXPERIMENT RESULT
# ============================================================

def _render_experiment_result(
    st,
    result: Optional[ExperimentResult],
) -> None:

    st.subheader(
        "Experiment Result"
    )

    if result is None:

        st.info(
            "Experiment has not been executed."
        )

        return

    st.write(
        f"**Status:** "
        f"{_format_result_status(result.status)}"
    )

    if result.experiment_id:

        st.write(
            f"**Experiment ID:** "
            f"{result.experiment_id}"
        )

    if result.dataset_reference:

        st.write(
            f"**Dataset:** "
            f"{result.dataset_reference}"
        )

    st.write(
        f"**Sample Size:** "
        f"{result.sample_size:,}"
    )

    _render_metric_dictionary(
        st,
        result.metrics,
    )

    if result.result_summary:

        st.write(
            "**Result Summary**"
        )

        st.info(
            result.result_summary
        )

    if result.observations:

        st.write(
            "**Observations**"
        )

        for observation in result.observations:
            st.write(
                f"- {observation}"
            )

    if result.limitations:

        st.write(
            "**Limitations**"
        )

        for limitation in result.limitations:
            st.warning(
                limitation
            )


# ============================================================
# UI — VALIDATION RESULT
# ============================================================

def _render_validation_result(
    st,
    result: Optional[ValidationResult],
) -> None:

    st.subheader(
        "Validation"
    )

    if result is None:

        st.info(
            "Validation has not been completed."
        )

        return

    st.write(
        f"**Status:** "
        f"{_format_result_status(result.status)}"
    )

    if result.validation_id:

        st.write(
            f"**Validation ID:** "
            f"{result.validation_id}"
        )

    # --------------------------------------------------------
    # Criteria
    # --------------------------------------------------------

    if result.criteria:

        st.write(
            "**Validation Criteria**"
        )

        _render_metric_dictionary(
            st,
            result.criteria,
        )

    # --------------------------------------------------------
    # Measured metrics
    # --------------------------------------------------------

    if result.measured_metrics:

        st.write(
            "**Measured Metrics**"
        )

        _render_metric_dictionary(
            st,
            result.measured_metrics,
        )

    # --------------------------------------------------------
    # Checks
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Passed",
            len(result.passed_checks),
        )

    with col2:

        st.metric(
            "Failed",
            len(result.failed_checks),
        )

    with col3:

        st.metric(
            "Unresolved",
            len(result.unresolved_checks),
        )

    # --------------------------------------------------------
    # Detailed checks
    # --------------------------------------------------------

    if result.passed_checks:

        with st.expander(
            "Passed Checks",
            expanded=False,
        ):

            for item in result.passed_checks:
                st.success(item)

    if result.failed_checks:

        with st.expander(
            "Failed Checks",
            expanded=True,
        ):

            for item in result.failed_checks:
                st.error(item)

    if result.unresolved_checks:

        with st.expander(
            "Unresolved Checks",
            expanded=True,
        ):

            for item in result.unresolved_checks:
                st.warning(item)

    if result.conclusion:

        st.write(
            "**Validation Conclusion**"
        )

        st.info(
            result.conclusion
        )


# ============================================================
# UI — STRESS TEST RESULT
# ============================================================

def _render_stress_test_result(
    st,
    result: Optional[StressTestResult],
) -> None:

    st.subheader(
        "Stress Test"
    )

    if result is None:

        st.info(
            "Stress testing has not been completed."
        )

        return

    st.write(
        f"**Status:** "
        f"{_format_result_status(result.status)}"
    )

    if result.stress_test_id:

        st.write(
            f"**Stress Test ID:** "
            f"{result.stress_test_id}"
        )

    # --------------------------------------------------------
    # Scenario counts
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Passed Scenarios",
            len(result.passed_scenarios),
        )

    with col2:

        st.metric(
            "Failed Scenarios",
            len(result.failed_scenarios),
        )

    with col3:

        st.metric(
            "Warnings",
            len(result.warnings),
        )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    if result.metrics:

        st.write(
            "**Stress Metrics**"
        )

        _render_metric_dictionary(
            st,
            result.metrics,
        )

    # --------------------------------------------------------
    # Scenario details
    # --------------------------------------------------------

    if result.passed_scenarios:

        with st.expander(
            "Passed Scenarios",
            expanded=False,
        ):

            for scenario in result.passed_scenarios:
                st.success(scenario)

    if result.failed_scenarios:

        with st.expander(
            "Failed Scenarios",
            expanded=True,
        ):

            for scenario in result.failed_scenarios:
                st.error(scenario)

    if result.warnings:

        with st.expander(
            "Stress Test Warnings",
            expanded=True,
        ):

            for warning in result.warnings:
                st.warning(warning)

    if result.conclusion:

        st.write(
            "**Stress Test Conclusion**"
        )

        st.info(
            result.conclusion
        )


# ============================================================
# UI — EVIDENCE PACKAGE
# ============================================================

def _render_evidence_package(
    st,
    package: ResearchEvidencePackage,
) -> None:

    st.subheader(
        "Research Evidence"
    )

    col1, col2 = st.columns(2)

    with col1:

        evidence_quality = (
            package.evidence_quality
            if package.evidence_quality is not None
            else "N/A"
        )

        st.metric(
            "Evidence Quality",
            evidence_quality,
        )

    with col2:

        confidence = (
            package.confidence
            if package.confidence is not None
            else "N/A"
        )

        st.metric(
            "Confidence",
            confidence,
        )

    if package.source_references:

        st.write(
            "**Source References**"
        )

        for reference in package.source_references:
            st.caption(reference)

    if package.contradictions:

        st.write(
            "**Contradictions**"
        )

        for contradiction in package.contradictions:
            st.warning(contradiction)

    if package.uncertainties:

        st.write(
            "**Uncertainties**"
        )

        for uncertainty in package.uncertainties:
            st.warning(uncertainty)


# ============================================================
# UI — COMPLETE RESEARCH EVIDENCE WORKSPACE
# ============================================================

def render_research_evidence(
    controller: ResearchPageController,
    results_store: ResearchResultsStore,
    research_id: str,
) -> None:
    """
    Render experiment, validation, stress-test and evidence
    results for one research item.
    """

    st = _safe_import_streamlit()

    record = controller.get_record(
        research_id
    )

    if record is None:

        st.error(
            f"Research not found: {research_id}"
        )

        return

    st.header(
        f"Research Evidence — {research_id}"
    )

    st.caption(
        f"Research lifecycle state: "
        f"{record.review_status.value}"
    )

    # --------------------------------------------------------
    # Experiment
    # --------------------------------------------------------

    experiment = (
        results_store.get_experiment(
            research_id
        )
    )

    _render_experiment_result(
        st,
        experiment,
    )

    st.divider()

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation = (
        results_store.get_validation(
            research_id
        )
    )

    _render_validation_result(
        st,
        validation,
    )

    st.divider()

    # --------------------------------------------------------
    # Stress Test
    # --------------------------------------------------------

    stress_test = (
        results_store.get_stress_test(
            research_id
        )
    )

    _render_stress_test_result(
        st,
        stress_test,
    )

    st.divider()

    # --------------------------------------------------------
    # Consolidated evidence
    # --------------------------------------------------------

    package = (
        results_store.build_evidence_package(
            research_id
        )
    )

    _render_evidence_package(
        st,
        package,
    )

    st.divider()

    # --------------------------------------------------------
    # Governance
    # --------------------------------------------------------

    st.warning(
        "Displayed research evidence does not automatically "
        "approve, deploy, or modify production intelligence."
    )


# ============================================================
# PART 3 PUBLIC API
# ============================================================

__all__.extend([
    "ResearchResultStatus",
    "ExperimentResult",
    "ValidationResult",
    "StressTestResult",
    "ResearchEvidencePackage",
    "ResearchResultsStore",
    "render_research_evidence",
])
```
```python
# ============================================================
# PART 4 — ADMIN REVIEW / CANDIDATE / VERSION / AUDIT
# ============================================================

# ============================================================
# ADMIN REVIEW STATUS
# ============================================================

class AdminReviewStatus(str, Enum):
    NOT_REVIEWED = "NOT_REVIEWED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUIRED = "REVISION_REQUIRED"


# ============================================================
# VERSION STATE
# ============================================================

class VersionState(str, Enum):
    NONE = "NONE"
    CANDIDATE = "CANDIDATE"
    VERSIONED = "VERSIONED"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    ROLLED_BACK = "ROLLED_BACK"


# ============================================================
# ADMIN REVIEW RECORD
# ============================================================

@dataclass
class AdminReviewRecord:
    """
    Controlled administrative review record.

    The reviewer can approve/reject a research candidate,
    but this object does not itself deploy production code.
    """

    research_id: str

    review_id: str = ""

    status: AdminReviewStatus = (
        AdminReviewStatus.NOT_REVIEWED
    )

    reviewer: str = ""

    reviewed_at: Optional[str] = None

    decision_reason: str = ""

    approval_conditions: List[str] = field(
        default_factory=list
    )

    blockers: List[str] = field(
        default_factory=list
    )

    evidence_references: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "review_id": self.review_id,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "reviewed_at": self.reviewed_at,
            "decision_reason": self.decision_reason,
            "approval_conditions": list(
                self.approval_conditions
            ),
            "blockers": list(self.blockers),
            "evidence_references": list(
                self.evidence_references
            ),
            "metadata": dict(self.metadata),
        }


# ============================================================
# CANDIDATE RECORD
# ============================================================

@dataclass
class ResearchCandidate:
    """
    Candidate representation before controlled production
    versioning/deployment.

    Candidate != production.
    """

    research_id: str

    candidate_id: str = ""

    candidate_version: str = ""

    source_engine_version: str = ""

    hypothesis: str = ""

    evidence_reference: str = ""

    validation_reference: str = ""

    stress_test_reference: str = ""

    admin_review_reference: str = ""

    status: VersionState = VersionState.CANDIDATE

    created_at: str = field(
        default_factory=lambda: (
            datetime.now(timezone.utc).isoformat()
        )
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "candidate_id": self.candidate_id,
            "candidate_version": (
                self.candidate_version
            ),
            "source_engine_version": (
                self.source_engine_version
            ),
            "hypothesis": self.hypothesis,
            "evidence_reference": (
                self.evidence_reference
            ),
            "validation_reference": (
                self.validation_reference
            ),
            "stress_test_reference": (
                self.stress_test_reference
            ),
            "admin_review_reference": (
                self.admin_review_reference
            ),
            "status": self.status.value,
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }


# ============================================================
# VERSION RECORD
# ============================================================

@dataclass
class ResearchVersionRecord:
    """
    Immutable-style research version metadata.

    A version identifies a validated research candidate.
    """

    research_id: str

    version_id: str = ""

    version: str = ""

    candidate_id: str = ""

    engine_version: str = ""

    schema_version: str = UI_SCHEMA_VERSION

    config_version: str = ""

    strategy_version: str = ""

    version_state: VersionState = (
        VersionState.VERSIONED
    )

    created_at: str = field(
        default_factory=lambda: (
            datetime.now(timezone.utc).isoformat()
        )
    )

    changelog: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "research_id": self.research_id,
            "version_id": self.version_id,
            "version": self.version,
            "candidate_id": self.candidate_id,
            "engine_version": self.engine_version,
            "schema_version": self.schema_version,
            "config_version": self.config_version,
            "strategy_version": self.strategy_version,
            "version_state": (
                self.version_state.value
            ),
            "created_at": self.created_at,
            "changelog": self.changelog,
            "metadata": dict(self.metadata),
        }


# ============================================================
# AUDIT EVENT
# ============================================================

@dataclass
class ResearchAuditEvent:
    """
    Research governance audit event.

    Designed to preserve traceability across the research
    lifecycle.
    """

    event_id: str

    timestamp: str

    research_id: str

    action: str

    previous_status: Optional[str] = None

    current_status: Optional[str] = None

    actor: str = ""

    reason: str = ""

    reference_id: str = ""

    engine_version: str = ""

    schema_version: str = UI_SCHEMA_VERSION

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "research_id": self.research_id,
            "action": self.action,
            "previous_status": self.previous_status,
            "current_status": self.current_status,
            "actor": self.actor,
            "reason": self.reason,
            "reference_id": self.reference_id,
            "engine_version": self.engine_version,
            "schema_version": self.schema_version,
            "metadata": dict(self.metadata),
        }


# ============================================================
# GOVERNANCE STORE
# ============================================================

class ResearchGovernanceStore:
    """
    Governance state store.

    This is currently an application/UI boundary implementation.
    It can later be replaced by the canonical persistence layer.

    IMPORTANT:
        It never writes production intelligence directly.
    """

    def __init__(self) -> None:

        self._reviews: Dict[
            str,
            AdminReviewRecord,
        ] = {}

        self._candidates: Dict[
            str,
            ResearchCandidate,
        ] = {}

        self._versions: Dict[
            str,
            ResearchVersionRecord,
        ] = {}

        self._audit_events: List[
            ResearchAuditEvent
        ] = []

    # ========================================================
    # REVIEW
    # ========================================================

    def save_review(
        self,
        review: AdminReviewRecord,
    ) -> None:

        self._reviews[
            review.research_id
        ] = review

    def get_review(
        self,
        research_id: str,
    ) -> Optional[AdminReviewRecord]:

        return self._reviews.get(
            research_id
        )

    # ========================================================
    # CANDIDATE
    # ========================================================

    def save_candidate(
        self,
        candidate: ResearchCandidate,
    ) -> None:

        self._candidates[
            candidate.research_id
        ] = candidate

    def get_candidate(
        self,
        research_id: str,
    ) -> Optional[ResearchCandidate]:

        return self._candidates.get(
            research_id
        )

    # ========================================================
    # VERSION
    # ========================================================

    def save_version(
        self,
        version: ResearchVersionRecord,
    ) -> None:

        self._versions[
            version.research_id
        ] = version

    def get_version(
        self,
        research_id: str,
    ) -> Optional[ResearchVersionRecord]:

        return self._versions.get(
            research_id
        )

    # ========================================================
    # AUDIT
    # ========================================================

    def add_audit_event(
        self,
        event: ResearchAuditEvent,
    ) -> None:

        self._audit_events.append(
            event
        )

    def get_audit_events(
        self,
        research_id: Optional[str] = None,
    ) -> List[ResearchAuditEvent]:

        if research_id is None:
            return list(
                self._audit_events
            )

        return [
            event
            for event in self._audit_events
            if event.research_id
            == research_id
        ]


# ============================================================
# GOVERNANCE SERVICE
# ============================================================

class ResearchGovernanceService:
    """
    Controlled governance service for the Research UI.

    This service handles metadata/state transitions only.

    It does NOT:
        - execute formulas
        - run production engines
        - place orders
        - modify broker state
        - modify CAS
        - modify D13
        - deploy production code
    """

    def __init__(
        self,
        controller: ResearchPageController,
        governance_store: ResearchGovernanceStore,
    ) -> None:

        self.controller = controller
        self.store = governance_store

    # ========================================================
    # INTERNAL AUDIT
    # ========================================================

    def _audit(
        self,
        research_id: str,
        action: str,
        previous_status: Optional[str],
        current_status: Optional[str],
        actor: str = "research_ui",
        reason: str = "",
        reference_id: str = "",
    ) -> None:

        event = ResearchAuditEvent(
            event_id=(
                f"RESEARCH-EVENT-"
                f"{len(self.store.get_audit_events()) + 1:06d}"
            ),
            timestamp=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            research_id=research_id,
            action=action,
            previous_status=previous_status,
            current_status=current_status,
            actor=actor,
            reason=reason,
            reference_id=reference_id,
        )

        self.store.add_audit_event(
            event
        )

    # ========================================================
    # ADMIN REVIEW
    # ========================================================

    def start_admin_review(
        self,
        research_id: str,
        reviewer: str = "",
    ) -> ResearchWorkflowResult:

        record = self.controller.get_record(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
                blockers=[
                    "Unknown research_id"
                ],
            )

        if record.review_status != (
            ResearchStatus.ADMIN_REVIEW
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                previous_status=record.review_status,
                current_status=record.review_status,
                message=(
                    "Research must reach ADMIN_REVIEW "
                    "before administrative review begins."
                ),
                blockers=[
                    "Complete validation and stress testing first."
                ],
            )

        review = AdminReviewRecord(
            research_id=research_id,
            review_id=(
                f"REVIEW-{research_id}"
            ),
            status=AdminReviewStatus.IN_REVIEW,
            reviewer=reviewer.strip(),
            reviewed_at=(
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
        )

        self.store.save_review(
            review
        )

        self._audit(
            research_id=research_id,
            action="ADMIN_REVIEW_STARTED",
            previous_status=record.review_status.value,
            current_status=record.review_status.value,
            actor=reviewer or "research_ui",
            reference_id=review.review_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=record.review_status,
            current_status=record.review_status,
            message="Administrative review started.",
        )

    # ========================================================
    # APPROVE REVIEW
    # ========================================================

    def approve_review(
        self,
        research_id: str,
        reviewer: str,
        reason: str,
    ) -> ResearchWorkflowResult:

        record = self.controller.get_record(
            research_id
        )

        review = self.store.get_review(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        if review is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Administrative review not found.",
                blockers=[
                    "Start admin review first."
                ],
            )

        if review.status != (
            AdminReviewStatus.IN_REVIEW
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Research is not currently "
                    "under administrative review."
                ),
            )

        if not reviewer.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Reviewer is required.",
                blockers=[
                    "Administrative approval requires an actor."
                ],
            )

        if not reason.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Approval reason is required.",
            )

        previous_status = (
            record.review_status
        )

        review.status = (
            AdminReviewStatus.APPROVED
        )

        review.reviewer = reviewer.strip()

        review.decision_reason = (
            reason.strip()
        )

        review.reviewed_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self.store.save_review(
            review
        )

        result = _controller_transition(
            self.controller,
            research_id,
            ResearchStatus.CANDIDATE,
        )

        if not result.success:

            return result

        self._audit(
            research_id=research_id,
            action="ADMIN_REVIEW_APPROVED",
            previous_status=previous_status.value,
            current_status=(
                ResearchStatus.CANDIDATE.value
            ),
            actor=reviewer,
            reason=reason,
            reference_id=review.review_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=previous_status,
            current_status=ResearchStatus.CANDIDATE,
            message=(
                "Administrative review approved; "
                "research is now a candidate."
            ),
        )

    # ========================================================
    # REJECT REVIEW
    # ========================================================

    def reject_review(
        self,
        research_id: str,
        reviewer: str,
        reason: str,
    ) -> ResearchWorkflowResult:

        review = self.store.get_review(
            research_id
        )

        if review is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Administrative review not found.",
            )

        if not reason.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Rejection reason is required.",
            )

        review.status = (
            AdminReviewStatus.REJECTED
        )

        review.reviewer = reviewer.strip()

        review.decision_reason = (
            reason.strip()
        )

        review.reviewed_at = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        review.blockers.append(
            reason.strip()
        )

        self.store.save_review(
            review
        )

        self._audit(
            research_id=research_id,
            action="ADMIN_REVIEW_REJECTED",
            previous_status=(
                AdminReviewStatus.IN_REVIEW.value
            ),
            current_status=(
                AdminReviewStatus.REJECTED.value
            ),
            actor=reviewer or "research_ui",
            reason=reason,
            reference_id=review.review_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            message=(
                "Research candidate rejected."
            ),
        )

    # ========================================================
    # CREATE CANDIDATE
    # ========================================================

    def create_candidate(
        self,
        research_id: str,
    ) -> ResearchWorkflowResult:

        record = self.controller.get_record(
            research_id
        )

        review = self.store.get_review(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        if review is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Admin review is required.",
            )

        if review.status != (
            AdminReviewStatus.APPROVED
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Only an approved admin review "
                    "can produce a candidate."
                ),
            )

        if record.review_status != (
            ResearchStatus.CANDIDATE
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Research must be in CANDIDATE state."
                ),
            )

        existing = self.store.get_candidate(
            research_id
        )

        if existing is not None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Candidate already exists."
                ),
            )

        candidate = ResearchCandidate(
            research_id=research_id,
            candidate_id=(
                f"CANDIDATE-{research_id}"
            ),
            candidate_version=(
                record.candidate_version
                or "CANDIDATE-UNVERSIONED"
            ),
            source_engine_version=(
                record.engine_version
            ),
            hypothesis=record.hypothesis,
            admin_review_reference=(
                review.review_id
            ),
        )

        self.store.save_candidate(
            candidate
        )

        self._audit(
            research_id=research_id,
            action="CANDIDATE_CREATED",
            previous_status=(
                ResearchStatus.CANDIDATE.value
            ),
            current_status=(
                ResearchStatus.CANDIDATE.value
            ),
            reference_id=candidate.candidate_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=ResearchStatus.CANDIDATE,
            current_status=ResearchStatus.CANDIDATE,
            message="Research candidate created.",
        )

    # ========================================================
    # VERSION CANDIDATE
    # ========================================================

    def version_candidate(
        self,
        research_id: str,
        version: str,
        changelog: str,
        config_version: str = "",
        strategy_version: str = "",
    ) -> ResearchWorkflowResult:

        record = self.controller.get_record(
            research_id
        )

        candidate = self.store.get_candidate(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        if candidate is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research candidate not found.",
            )

        if not version.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Version is required.",
            )

        if not changelog.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Changelog is required.",
            )

        if record.review_status != (
            ResearchStatus.CANDIDATE
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Only CANDIDATE research can be versioned."
                ),
            )

        existing_version = (
            self.store.get_version(
                research_id
            )
        )

        if existing_version is not None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "A version already exists for this "
                    "research item."
                ),
            )

        version_record = ResearchVersionRecord(
            research_id=research_id,
            version_id=(
                f"VERSION-{research_id}-{version.strip()}"
            ),
            version=version.strip(),
            candidate_id=candidate.candidate_id,
            engine_version=(
                candidate.source_engine_version
            ),
            schema_version=UI_SCHEMA_VERSION,
            config_version=config_version.strip(),
            strategy_version=strategy_version.strip(),
            version_state=VersionState.VERSIONED,
            changelog=changelog.strip(),
        )

        self.store.save_version(
            version_record
        )

        previous_status = (
            record.review_status
        )

        transition = _controller_transition(
            self.controller,
            research_id,
            ResearchStatus.VERSION,
        )

        if not transition.success:

            return transition

        self._audit(
            research_id=research_id,
            action="RESEARCH_VERSION_CREATED",
            previous_status=previous_status.value,
            current_status=(
                ResearchStatus.VERSION.value
            ),
            reference_id=version_record.version_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=previous_status,
            current_status=ResearchStatus.VERSION,
            message=(
                f"Research version "
                f"{version_record.version} created."
            ),
        )

    # ========================================================
    # APPROVE VERSION
    # ========================================================

    def approve_version(
        self,
        research_id: str,
        reviewer: str,
        reason: str,
    ) -> ResearchWorkflowResult:

        record = self.controller.get_record(
            research_id
        )

        version = self.store.get_version(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        if version is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Version record not found.",
            )

        if record.review_status != (
            ResearchStatus.VERSION
        ):

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message=(
                    "Research must be in VERSION state "
                    "before approval."
                ),
            )

        if not reviewer.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Reviewer is required.",
            )

        if not reason.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Approval reason is required.",
            )

        previous_status = (
            record.review_status
        )

        version.version_state = (
            VersionState.APPROVED
        )

        version.metadata[
            "approved_by"
        ] = reviewer.strip()

        version.metadata[
            "approval_reason"
        ] = reason.strip()

        version.metadata[
            "approved_at"
        ] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self.store.save_version(
            version
        )

        transition = _controller_transition(
            self.controller,
            research_id,
            ResearchStatus.APPROVED,
        )

        if not transition.success:

            return transition

        self._audit(
            research_id=research_id,
            action="VERSION_APPROVED",
            previous_status=previous_status.value,
            current_status=(
                ResearchStatus.APPROVED.value
            ),
            actor=reviewer,
            reason=reason,
            reference_id=version.version_id,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=previous_status,
            current_status=ResearchStatus.APPROVED,
            message=(
                f"Version {version.version} approved."
            ),
        )

    # ========================================================
    # DEPLOYMENT GUARD
    # ========================================================

    def request_deployment(
        self,
        research_id: str,
    ) -> ResearchWorkflowResult:

        """
        Explicit safety boundary.

        Research UI NEVER performs production deployment.
        """

        record = self.controller.get_record(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        self._audit(
            research_id=research_id,
            action="DEPLOYMENT_REQUEST_BLOCKED",
            previous_status=(
                record.review_status.value
            ),
            current_status=(
                record.review_status.value
            ),
            reason=(
                "Research UI cannot directly deploy "
                "production intelligence."
            ),
        )

        return ResearchWorkflowResult(
            success=False,
            research_id=research_id,
            previous_status=record.review_status,
            current_status=record.review_status,
            message=(
                "Production deployment is blocked "
                "from Research UI."
            ),
            blockers=[
                "Use the controlled deployment layer.",
                "Production mutation is not permitted here.",
            ],
        )

    # ========================================================
    # ROLLBACK REQUEST GUARD
    # ========================================================

    def request_rollback(
        self,
        research_id: str,
        reason: str,
    ) -> ResearchWorkflowResult:

        """
        Rollback request is recorded but not executed here.
        """

        record = self.controller.get_record(
            research_id
        )

        if record is None:

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Research record not found.",
            )

        if not reason.strip():

            return ResearchWorkflowResult(
                success=False,
                research_id=research_id,
                message="Rollback reason is required.",
            )

        self._audit(
            research_id=research_id,
            action="ROLLBACK_REQUESTED",
            previous_status=(
                record.review_status.value
            ),
            current_status=(
                record.review_status.value
            ),
            reason=reason,
        )

        return ResearchWorkflowResult(
            success=True,
            research_id=research_id,
            previous_status=record.review_status,
            current_status=record.review_status,
            message=(
                "Rollback request recorded for the "
                "controlled deployment layer."
            ),
            metadata={
                "execution": "NOT_PERFORMED_BY_UI"
            },
        )


# ============================================================
# UI — ADMIN REVIEW PANEL
# ============================================================

def _render_admin_review_panel(
    st,
    service: ResearchGovernanceService,
    record: ResearchRecord,
) -> None:

    st.subheader(
        "Admin Review"
    )

    review = service.store.get_review(
        record.research_id
    )

    if review is None:

        st.info(
            "No administrative review exists yet."
        )

        if record.review_status == (
            ResearchStatus.ADMIN_REVIEW
        ):

            reviewer = st.text_input(
                "Reviewer",
                key=(
                    f"reviewer_"
                    f"{record.research_id}"
                ),
            )

            if st.button(
                "Start Admin Review",
                key=(
                    f"start_review_"
                    f"{record.research_id}"
                ),
            ):

                result = (
                    service.start_admin_review(
                        record.research_id,
                        reviewer,
                    )
                )

                if result.success:
                    st.success(
                        result.message
                    )
                    st.rerun()

                else:
                    st.error(
                        result.message
                    )

        return

    st.write(
        f"**Review Status:** "
        f"{review.status.value}"
    )

    st.write(
        f"**Reviewer:** "
        f"{review.reviewer or '-'}"
    )

    if review.decision_reason:

        st.write(
            f"**Decision Reason:** "
            f"{review.decision_reason}"
        )

    if review.status == (
        AdminReviewStatus.IN_REVIEW
    ):

        reviewer = st.text_input(
            "Reviewing Actor",
            value=review.reviewer,
            key=(
                f"review_actor_"
                f"{record.research_id}"
            ),
        )

        reason = st.text_area(
            "Decision Reason",
            key=(
                f"review_reason_"
                f"{record.research_id}"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Approve Review",
                key=(
                    f"approve_review_"
                    f"{record.research_id}"
                ),
            ):

                result = service.approve_review(
                    record.research_id,
                    reviewer,
                    reason,
                )

                if result.success:
                    st.success(
                        result.message
                    )
                    st.rerun()

                else:
                    st.error(
                        result.message
                    )

        with col2:

            if st.button(
                "Reject Review",
                key=(
                    f"reject_review_"
                    f"{record.research_id}"
                ),
            ):

                result = service.reject_review(
                    record.research_id,
                    reviewer,
                    reason,
                )

                if result.success:
                    st.warning(
                        result.message
                    )
                    st.rerun()

                else:
                    st.error(
                        result.message
                    )


# ============================================================
# UI — CANDIDATE / VERSION PANEL
# ============================================================

def _render_candidate_version_panel(
    st,
    service: ResearchGovernanceService,
    record: ResearchRecord,
) -> None:

    st.subheader(
        "Candidate & Version"
    )

    candidate = service.store.get_candidate(
        record.research_id
    )

    version = service.store.get_version(
        record.research_id
    )

    # --------------------------------------------------------
    # Candidate
    # --------------------------------------------------------

    if record.review_status == (
        ResearchStatus.CANDIDATE
    ):

        if candidate is None:

            st.info(
                "Approved research can now be "
                "materialized as a candidate."
            )

            if st.button(
                "Create Candidate",
                key=(
                    f"create_candidate_"
                    f"{record.research_id}"
                ),
            ):

                result = (
                    service.create_candidate(
                        record.research_id
                    )
                )

                if result.success:
                    st.success(
                        result.message
                    )
                    st.rerun()

                else:
                    st.error(
                        result.message
                    )

        else:

            st.write(
                f"**Candidate ID:** "
                f"{candidate.candidate_id}"
            )

            st.write(
                f"**Candidate Version:** "
                f"{candidate.candidate_version}"
            )

    # --------------------------------------------------------
    # Version
    # --------------------------------------------------------

    if record.review_status == (
        ResearchStatus.CANDIDATE
    ) and candidate is not None and version is None:

        st.divider()

        st.write(
            "**Create Controlled Version**"
        )

        version_name = st.text_input(
            "Version",
            placeholder="v1.0.0",
            key=(
                f"version_name_"
                f"{record.research_id}"
            ),
        )

        changelog = st.text_area(
            "Changelog",
            placeholder=(
                "Describe exactly what this research "
                "version represents."
            ),
            key=(
                f"version_changelog_"
                f"{record.research_id}"
            ),
        )

        config_version = st.text_input(
            "Config Version",
            key=(
                f"config_version_"
                f"{record.research_id}"
            ),
        )

        strategy_version = st.text_input(
            "Strategy Version",
            key=(
                f"strategy_version_"
                f"{record.research_id}"
            ),
        )

        if st.button(
            "Create Version",
            key=(
                f"create_version_"
                f"{record.research_id}"
            ),
        ):

            result = service.version_candidate(
                research_id=record.research_id,
                version=version_name,
                changelog=changelog,
                config_version=config_version,
                strategy_version=strategy_version,
            )

            if result.success:
                st.success(
                    result.message
                )
                st.rerun()

            else:
                st.error(
                    result.message
                )

    # --------------------------------------------------------
    # Version approval
    # --------------------------------------------------------

    if (
        record.review_status
        == ResearchStatus.VERSION
        and version is not None
    ):

        st.divider()

        st.write(
            f"**Version:** {version.version}"
        )

        st.write(
            f"**State:** "
            f"{version.version_state.value}"
        )

        reviewer = st.text_input(
            "Version Approver",
            key=(
                f"version_approver_"
                f"{record.research_id}"
            ),
        )

        reason = st.text_area(
            "Approval Reason",
            key=(
                f"version_approval_reason_"
                f"{record.research_id}"
            ),
        )

        if st.button(
            "Approve Version",
            key=(
                f"approve_version_"
                f"{record.research_id}"
            ),
        ):

            result = service.approve_version(
                research_id=record.research_id,
                reviewer=reviewer,
                reason=reason,
            )

            if result.success:
                st.success(
                    result.message
                )
                st.rerun()

            else:
                st.error(
                    result.message
                )


# ============================================================
# UI — AUDIT TRAIL
# ============================================================

def _render_audit_trail(
    st,
    service: ResearchGovernanceService,
    research_id: str,
) -> None:

    st.subheader(
        "Research Audit Trail"
    )

    events = service.store.get_audit_events(
        research_id
    )

    if not events:

        st.info(
            "No audit events recorded."
        )

        return

    for event in reversed(events):

        with st.expander(
            (
                f"{event.action} — "
                f"{event.timestamp}"
            ),
            expanded=False,
        ):

            st.write(
                f"**Event ID:** "
                f"{event.event_id}"
            )

            st.write(
                f"**Actor:** "
                f"{event.actor or '-'}"
            )

            st.write(
                f"**Previous:** "
                f"{event.previous_status or '-'}"
            )

            st.write(
                f"**Current:** "
                f"{event.current_status or '-'}"
            )

            if event.reason:

                st.write(
                    f"**Reason:** "
                    f"{event.reason}"
                )

            if event.reference_id:

                st.write(
                    f"**Reference:** "
                    f"{event.reference_id}"
                )


# ============================================================
# UI — DEPLOYMENT / ROLLBACK BOUNDARY
# ============================================================

def _render_deployment_boundary(
    st,
    service: ResearchGovernanceService,
    record: ResearchRecord,
) -> None:

    st.subheader(
        "Controlled Deployment"
    )

    st.warning(
        "Production deployment is intentionally outside "
        "the Research UI."
    )

    if record.review_status == (
        ResearchStatus.APPROVED
    ):

        if st.button(
            "Request Controlled Deployment",
            key=(
                f"request_deployment_"
                f"{record.research_id}"
            ),
        ):

            result = (
                service.request_deployment(
                    record.research_id
                )
            )

            st.error(
                result.message
            )

            for blocker in result.blockers:
                st.warning(blocker)

    st.caption(
        "The UI may record a deployment request, but "
        "the controlled deployment layer must perform "
        "the actual production change."
    )


# ============================================================
# COMPLETE PART 4 GOVERNANCE WORKSPACE
# ============================================================

def render_research_governance(
    controller: ResearchPageController,
    governance_store: ResearchGovernanceStore,
    research_id: str,
) -> None:
    """
    Complete Part 4 governance workspace.
    """

    st = _safe_import_streamlit()

    record = controller.get_record(
        research_id
    )

    if record is None:

        st.error(
            f"Research not found: {research_id}"
        )

        return

    service = ResearchGovernanceService(
        controller=controller,
        governance_store=governance_store,
    )

    st.header(
        f"Research Governance — {research_id}"
    )

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    st.caption(
        f"Current lifecycle state: "
        f"{record.review_status.value}"
    )

    # --------------------------------------------------------
    # Admin Review
    # --------------------------------------------------------

    _render_admin_review_panel(
        st,
        service,
        record,
    )

    st.divider()

    # --------------------------------------------------------
    # Candidate / Version
    # --------------------------------------------------------

    _render_candidate_version_panel(
        st,
        service,
        record,
    )

    st.divider()

    # --------------------------------------------------------
    # Deployment boundary
    # --------------------------------------------------------

    _render_deployment_boundary(
        st,
        service,
        record,
    )

    st.divider()

    # --------------------------------------------------------
    # Audit
    # --------------------------------------------------------

    _render_audit_trail(
        st,
        service,
        research_id,
    )


# ============================================================
# PART 4 PUBLIC API
# ============================================================

__all__.extend([
    "AdminReviewStatus",
    "VersionState",
    "AdminReviewRecord",
    "ResearchCandidate",
    "ResearchVersionRecord",
    "ResearchAuditEvent",
    "ResearchGovernanceStore",
    "ResearchGovernanceService",
    "render_research_governance",
])
```
```python
# ============================================================
# PART 5 — COMPLETE RESEARCH PAGE INTEGRATION
# ============================================================

# ============================================================
# SESSION STATE KEYS
# ============================================================

RESEARCH_SESSION_CONTROLLER = (
    "robomlm_research_controller"
)

RESEARCH_SESSION_RESULTS = (
    "robomlm_research_results_store"
)

RESEARCH_SESSION_GOVERNANCE = (
    "robomlm_research_governance_store"
)

RESEARCH_SESSION_SELECTED = (
    "robomlm_research_selected_id"
)

RESEARCH_SESSION_INITIALIZED = (
    "robomlm_research_initialized"
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

def _initialize_research_session(st) -> None:
    """
    Initialize Research page state exactly once per Streamlit
    session.

    Session state is UI/application state only.
    """

    if (
        RESEARCH_SESSION_CONTROLLER
        not in st.session_state
    ):

        st.session_state[
            RESEARCH_SESSION_CONTROLLER
        ] = ResearchPageController()

    if (
        RESEARCH_SESSION_RESULTS
        not in st.session_state
    ):

        st.session_state[
            RESEARCH_SESSION_RESULTS
        ] = ResearchResultsStore()

    if (
        RESEARCH_SESSION_GOVERNANCE
        not in st.session_state
    ):

        st.session_state[
            RESEARCH_SESSION_GOVERNANCE
        ] = ResearchGovernanceStore()

    if (
        RESEARCH_SESSION_SELECTED
        not in st.session_state
    ):

        st.session_state[
            RESEARCH_SESSION_SELECTED
        ] = None

    st.session_state[
        RESEARCH_SESSION_INITIALIZED
    ] = True


# ============================================================
# SESSION ACCESSORS
# ============================================================

def _get_research_controller(st) -> ResearchPageController:

    return st.session_state[
        RESEARCH_SESSION_CONTROLLER
    ]


def _get_research_results_store(
    st,
) -> ResearchResultsStore:

    return st.session_state[
        RESEARCH_SESSION_RESULTS
    ]


def _get_research_governance_store(
    st,
) -> ResearchGovernanceStore:

    return st.session_state[
        RESEARCH_SESSION_GOVERNANCE
    ]


# ============================================================
# PAGE RESET
# ============================================================

def _reset_research_workspace(st) -> None:
    """
    Reset only Research UI/application state.

    This MUST NOT reset or mutate production intelligence.
    """

    st.session_state[
        RESEARCH_SESSION_CONTROLLER
    ] = ResearchPageController()

    st.session_state[
        RESEARCH_SESSION_RESULTS
    ] = ResearchResultsStore()

    st.session_state[
        RESEARCH_SESSION_GOVERNANCE
    ] = ResearchGovernanceStore()

    st.session_state[
        RESEARCH_SESSION_SELECTED
    ] = None


# ============================================================
# RESEARCH FILTER
# ============================================================

def _filter_research_records(
    records: List[ResearchRecord],
    status: Optional[ResearchStatus],
) -> List[ResearchRecord]:

    if status is None:
        return list(records)

    return [
        record
        for record in records
        if record.review_status == status
    ]


# ============================================================
# FILTER PANEL
# ============================================================

def _render_research_filters(
    st,
    controller: ResearchPageController,
) -> Optional[ResearchStatus]:

    st.subheader(
        "Research Filters"
    )

    status_options = [
        "ALL"
    ] + [
        status.value
        for status in ResearchStatus
    ]

    selected_status = st.selectbox(
        "Lifecycle Status",
        status_options,
        key="research_status_filter",
    )

    if selected_status == "ALL":
        return None

    try:
        return ResearchStatus(
            selected_status
        )

    except ValueError:
        return None


# ============================================================
# RESEARCH SELECTOR
# ============================================================

def _render_research_selector(
    st,
    records: List[ResearchRecord],
) -> Optional[str]:

    if not records:

        st.info(
            "No research records match the selected filter."
        )

        return None

    research_ids = [
        record.research_id
        for record in records
    ]

    current_selected = st.session_state.get(
        RESEARCH_SESSION_SELECTED
    )

    if (
        current_selected not in research_ids
    ):

        current_selected = research_ids[0]

        st.session_state[
            RESEARCH_SESSION_SELECTED
        ] = current_selected

    selected_id = st.selectbox(
        "Research Item",
        research_ids,
        index=research_ids.index(
            current_selected
        ),
        key="research_item_selector",
    )

    st.session_state[
        RESEARCH_SESSION_SELECTED
    ] = selected_id

    return selected_id


# ============================================================
# RESEARCH SUMMARY CARD
# ============================================================

def _render_research_summary_card(
    st,
    record: ResearchRecord,
) -> None:

    st.subheader(
        "Research Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Research ID",
            record.research_id,
        )

    with col2:

        st.metric(
            "Lifecycle",
            record.review_status.value,
        )

    with col3:

        st.metric(
            "Engine Version",
            record.engine_version or "-",
        )

    with col4:

        st.metric(
            "Candidate Version",
            record.candidate_version or "-",
        )

    if record.hypothesis:

        st.write(
            "**Hypothesis**"
        )

        st.info(
            record.hypothesis
        )

    if record.dataset:

        st.write(
            f"**Dataset:** {record.dataset}"
        )

    if record.experiment:

        st.write(
            "**Experiment Definition**"
        )

        st.write(
            record.experiment
        )


# ============================================================
# LIFECYCLE PIPELINE VIEW
# ============================================================

def _render_lifecycle_pipeline(
    st,
    record: ResearchRecord,
) -> None:

    st.subheader(
        "Controlled Research Pipeline"
    )

    current_status = record.review_status

    pipeline = [
        ResearchStatus.RESEARCH,
        ResearchStatus.EXPERIMENT,
        ResearchStatus.VALIDATION,
        ResearchStatus.STRESS_TEST,
        ResearchStatus.ADMIN_REVIEW,
        ResearchStatus.CANDIDATE,
        ResearchStatus.VERSION,
        ResearchStatus.APPROVED,
        ResearchStatus.DEPLOYED,
    ]

    current_index = (
        pipeline.index(current_status)
        if current_status in pipeline
        else -1
    )

    for index, status in enumerate(
        pipeline
    ):

        if index < current_index:

            marker = "✓"

        elif index == current_index:

            marker = "●"

        else:

            marker = "○"

        st.write(
            f"{marker} **{status.value}**"
        )

        if index < len(pipeline) - 1:
            st.caption("↓")


# ============================================================
# GOVERNANCE STATE CARD
# ============================================================

def _render_governance_state(
    st,
    record: ResearchRecord,
    governance_store: ResearchGovernanceStore,
) -> None:

    review = governance_store.get_review(
        record.research_id
    )

    candidate = governance_store.get_candidate(
        record.research_id
    )

    version = governance_store.get_version(
        record.research_id
    )

    st.subheader(
        "Governance State"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "**Admin Review**"
        )

        st.write(
            review.status.value
            if review
            else "NOT STARTED"
        )

    with col2:

        st.write(
            "**Candidate**"
        )

        st.write(
            candidate.status.value
            if candidate
            else "NOT CREATED"
        )

    with col3:

        st.write(
            "**Version**"
        )

        st.write(
            version.version_state.value
            if version
            else "NOT VERSIONED"
        )


# ============================================================
# AUDIT COUNT
# ============================================================

def _render_audit_summary(
    st,
    governance_store: ResearchGovernanceStore,
    research_id: str,
) -> None:

    events = governance_store.get_audit_events(
        research_id
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Audit Events",
            len(events),
        )

    with col2:

        last_action = (
            events[-1].action
            if events
            else "NONE"
        )

        st.metric(
            "Last Action",
            last_action,
        )


# ============================================================
# RESEARCH TAB
# ============================================================

def _render_research_overview_tab(
    st,
    controller: ResearchPageController,
    governance_store: ResearchGovernanceStore,
) -> None:

    records = controller.list_records()

    if not records:

        st.info(
            "Research registry is empty."
        )

        _render_create_research_form(
            st,
            controller,
        )

        return

    status_filter = _render_research_filters(
        st,
        controller,
    )

    filtered_records = (
        _filter_research_records(
            records,
            status_filter,
        )
    )

    selected_id = _render_research_selector(
        st,
        filtered_records,
    )

    if selected_id is None:
        return

    record = controller.get_record(
        selected_id
    )

    if record is None:
        return

    st.divider()

    _render_research_summary_card(
        st,
        record,
    )

    st.divider()

    _render_lifecycle_pipeline(
        st,
        record,
    )

    st.divider()

    _render_governance_state(
        st,
        record,
        governance_store,
    )

    _render_audit_summary(
        st,
        governance_store,
        record.research_id,
    )


# ============================================================
# EVIDENCE TAB
# ============================================================

def _render_evidence_tab(
    st,
    controller: ResearchPageController,
    results_store: ResearchResultsStore,
) -> None:

    records = controller.list_records()

    if not records:

        st.info(
            "No research available for evidence review."
        )

        return

    research_ids = [
        record.research_id
        for record in records
    ]

    selected_id = st.selectbox(
        "Research Evidence Item",
        research_ids,
        key="research_evidence_selector",
    )

    render_research_evidence(
        controller=controller,
        results_store=results_store,
        research_id=selected_id,
    )


# ============================================================
# GOVERNANCE TAB
# ============================================================

def _render_governance_tab(
    st,
    controller: ResearchPageController,
    governance_store: ResearchGovernanceStore,
) -> None:

    records = controller.list_records()

    if not records:

        st.info(
            "No research available for governance review."
        )

        return

    research_ids = [
        record.research_id
        for record in records
    ]

    selected_id = st.selectbox(
        "Research Governance Item",
        research_ids,
        key="research_governance_selector",
    )

    render_research_governance(
        controller=controller,
        governance_store=governance_store,
        research_id=selected_id,
    )


# ============================================================
# CREATE TAB
# ============================================================

def _render_create_tab(
    st,
    controller: ResearchPageController,
) -> None:

    st.header(
        "New Research"
    )

    st.caption(
        "Create a research definition without changing "
        "production intelligence."
    )

    _render_create_research_form(
        st,
        controller,
    )

    st.divider()

    st.info(
        "Research creation defines the hypothesis and "
        "experiment boundary. Formula implementation and "
        "production deployment belong to controlled "
        "downstream layers."
    )


# ============================================================
# AUDIT TAB
# ============================================================

def _render_audit_tab(
    st,
    controller: ResearchPageController,
    governance_store: ResearchGovernanceStore,
) -> None:

    st.header(
        "Research Audit"
    )

    records = controller.list_records()

    if not records:

        st.info(
            "No research audit data available."
        )

        return

    selected_id = st.selectbox(
        "Research",
        [
            record.research_id
            for record in records
        ],
        key="research_audit_selector",
    )

    _render_audit_trail(
        st,
        ResearchGovernanceService(
            controller=controller,
            governance_store=governance_store,
        ),
        selected_id,
    )


# ============================================================
# SAFETY / ARCHITECTURE TAB
# ============================================================

def _render_architecture_tab(
    st,
) -> None:

    st.header(
        "Research Architecture"
    )

    st.info(
        "Research is isolated from direct production mutation."
    )

    st.write(
        "**Research flow**"
    )

    st.code(
        (
            "Research\n"
            "   ↓\n"
            "Experiment\n"
            "   ↓\n"
            "Validation\n"
            "   ↓\n"
            "Stress Test\n"
            "   ↓\n"
            "Admin Review\n"
            "   ↓\n"
            "Candidate\n"
            "   ↓\n"
            "Version\n"
            "   ↓\n"
            "Approval\n"
            "   ↓\n"
            "Controlled Deployment"
        )
    )

    st.write(
        "**Authority Boundary**"
    )

    st.write(
        "Research UI"
        " → "
        "Research/Application Layer"
        " → "
        "Controlled Deployment Layer"
    )

    st.write(
        "**Decision Authority:** "
        f"{DECISION_AUTHORITY}"
    )

    st.write(
        "**Production Mutation from UI:** BLOCKED"
    )

    st.write(
        "**Direct Broker Control:** BLOCKED"
    )

    st.write(
        "**Direct CAS Control:** BLOCKED"
    )

    st.write(
        "**Direct D13 Modification:** BLOCKED"
    )

    st.warning(
        "Research UI presents and controls research workflow "
        "metadata. It must never become a hidden production "
        "intelligence engine."
    )


# ============================================================
# TOP PAGE CONTROLS
# ============================================================

def _render_page_controls(
    st,
    controller: ResearchPageController,
) -> None:

    col1, col2, col3 = st.columns(
        [2, 2, 1]
    )

    with col1:

        st.caption(
            f"Research Version: {RESEARCH_VERSION}"
        )

    with col2:

        st.caption(
            f"UI Schema: {UI_SCHEMA_VERSION}"
        )

    with col3:

        if st.button(
            "Reset UI State",
            key="research_reset_ui",
        ):

            _reset_research_workspace(
                st
            )

            st.rerun()


# ============================================================
# MAIN INTEGRATED RESEARCH PAGE
# ============================================================

def render_research_page_complete() -> None:
    """
    Complete integrated ROBOMLM Research page.

    This is the recommended Part 5 entry point.

    It connects:
        Part 1 → Registry / Controller
        Part 2 → Lifecycle workflow
        Part 3 → Evidence
        Part 4 → Governance / Audit
        Part 5 → Integrated UI
    """

    st = _safe_import_streamlit()

    # --------------------------------------------------------
    # Initialize
    # --------------------------------------------------------

    _initialize_research_session(
        st
    )

    controller = _get_research_controller(
        st
    )

    results_store = _get_research_results_store(
        st
    )

    governance_store = (
        _get_research_governance_store(
            st
        )
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.title(
        PAGE_TITLE
    )

    st.caption(
        PAGE_SUBTITLE
    )

    _render_page_controls(
        st,
        controller,
    )

    st.divider()

    # --------------------------------------------------------
    # Architecture boundary
    # --------------------------------------------------------

    _render_architecture_notice(
        st
    )

    # --------------------------------------------------------
    # Main tabs
    # --------------------------------------------------------

    (
        overview_tab,
        create_tab,
        evidence_tab,
        governance_tab,
        audit_tab,
        architecture_tab,
    ) = st.tabs(
        [
            "Overview",
            "New Research",
            "Evidence",
            "Governance",
            "Audit",
            "Architecture",
        ]
    )

    # ========================================================
    # OVERVIEW
    # ========================================================

    with overview_tab:

        _render_research_overview_tab(
            st,
            controller,
            governance_store,
        )

    # ========================================================
    # NEW RESEARCH
    # ========================================================

    with create_tab:

        _render_create_tab(
            st,
            controller,
        )

    # ========================================================
    # EVIDENCE
    # ========================================================

    with evidence_tab:

        _render_evidence_tab(
            st,
            controller,
            results_store,
        )

    # ========================================================
    # GOVERNANCE
    # ========================================================

    with governance_tab:

        _render_governance_tab(
            st,
            controller,
            governance_store,
        )

    # ========================================================
    # AUDIT
    # ========================================================

    with audit_tab:

        _render_audit_tab(
            st,
            controller,
            governance_store,
        )

    # ========================================================
    # ARCHITECTURE
    # ========================================================

    with architecture_tab:

        _render_architecture_tab(
            st
        )

    # --------------------------------------------------------
    # Footer boundary
    # --------------------------------------------------------

    st.divider()

    st.caption(
        "ROBOMLM Research Layer — "
        "Research → Evidence → Validation → "
        "Stress Test → Admin Review → Candidate → "
        "Version → Controlled Deployment"
    )


# ============================================================
# COMPATIBILITY ENTRY POINT
# ============================================================

def render_research_page_v5() -> None:
    """
    Compatibility alias for the complete Part 5 page.
    """

    render_research_page_complete()


# ============================================================
# FINAL PUBLIC API
# ============================================================

__all__.extend([
    "RESEARCH_SESSION_CONTROLLER",
    "RESEARCH_SESSION_RESULTS",
    "RESEARCH_SESSION_GOVERNANCE",
    "RESEARCH_SESSION_SELECTED",
    "RESEARCH_SESSION_INITIALIZED",
    "render_research_page_complete",
    "render_research_page_v5",
])
```
