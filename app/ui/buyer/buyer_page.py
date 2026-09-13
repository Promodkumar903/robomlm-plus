```python
"""
ROBOMLM_PLUS
Buyer UI — Part 1
=================

File:
    app/ui/buyer/buyer_page.py

Purpose:
    Buyer workspace foundation.

Blueprint flow:
    Market
        ↓
    Instrument
        ↓
    Contract
        ↓
    Strategy
        ↓
    Mode
        ↓
    Apply for Analysis
        ↓
    Intelligence
        ↓
    Decision
        ↓
    Risk
        ↓
    CAS
        ↓
    Result

Important architectural boundaries:
    - Buyer owns user interaction flow.
    - Buyer does NOT calculate decision mathematics.
    - Buyer does NOT calculate risk mathematics.
    - Buyer does NOT authorize execution.
    - Buyer does NOT bypass D13.
    - Buyer does NOT bypass CAS.
    - Buyer does NOT submit broker orders.
    - Apply is NOT Execute.

This file intentionally contains no trading formulas or invented thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional, Sequence
from uuid import uuid4


# ============================================================================
# VERSION / ARCHITECTURE CONSTANTS
# ============================================================================

BUYER_PAGE_VERSION = "1.0.0"
BUYER_UI_SCHEMA_VERSION = "1.0.0"

DECISION_AUTHORITY = "D13"

PRODUCTION_MUTATION_ALLOWED = False
DIRECT_ENGINE_CONTROL_ALLOWED = False
DIRECT_BROKER_CONTROL_ALLOWED = False
DIRECT_EXECUTION_ALLOWED = False
DIRECT_CAS_OVERRIDE_ALLOWED = False


# ============================================================================
# ENUMS
# ============================================================================


class BuyerMode(str, Enum):
    """
    Blueprint-defined Buyer modes.

    ANALYSIS:
        Request/display intelligence without execution authorization.

    SIMULATION:
        Evaluate the workflow in simulation context.

    AUTHORIZED_EXECUTION:
        Represents an execution-capable request context only after the
        required downstream authorization chain succeeds.

    The UI itself never grants authorization.
    """

    ANALYSIS = "ANALYSIS"
    SIMULATION = "SIMULATION"
    AUTHORIZED_EXECUTION = "AUTHORIZED_EXECUTION"


class BuyerStage(str, Enum):
    """Current stage of the Buyer workflow."""

    IDLE = "IDLE"
    MARKET = "MARKET"
    INSTRUMENT = "INSTRUMENT"
    CONTRACT = "CONTRACT"
    STRATEGY = "STRATEGY"
    MODE = "MODE"
    ANALYSIS_REQUESTED = "ANALYSIS_REQUESTED"
    INTELLIGENCE = "INTELLIGENCE"
    DECISION = "DECISION"
    RISK = "RISK"
    CAS = "CAS"
    RESULT = "RESULT"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


class BuyerRequestStatus(str, Enum):
    """Lifecycle status of a Buyer request."""

    DRAFT = "DRAFT"
    READY = "READY"
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class BuyerResultStatus(str, Enum):
    """
    Final presentation state.

    This is deliberately descriptive.
    It does not create an execution authorization.
    """

    NOT_AVAILABLE = "NOT_AVAILABLE"
    AVAILABLE = "AVAILABLE"
    RESTRICTED = "RESTRICTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    ERROR = "ERROR"


# ============================================================================
# IMMUTABLE-ish ID / TIME HELPERS
# ============================================================================


def _utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _new_id(prefix: str) -> str:
    """Create a traceable Buyer identifier."""
    return f"{prefix}_{uuid4().hex}"


# ============================================================================
# BUYER REQUEST CONTRACT
# ============================================================================


@dataclass
class BuyerRequest:
    """
    Canonical UI-side request representation.

    This is a request contract, not an intelligence result.

    Required conceptual inputs from blueprint:
        Market
        Instrument
        Contract
        Strategy
        Mode
    """

    request_id: str = field(default_factory=lambda: _new_id("BUYREQ"))

    market: Optional[str] = None
    instrument: Optional[str] = None
    contract: Optional[str] = None
    strategy: Optional[str] = None

    mode: BuyerMode = BuyerMode.ANALYSIS

    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    status: BuyerRequestStatus = BuyerRequestStatus.DRAFT

    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update modification timestamp."""
        self.updated_at = _utc_now()

    def is_selection_complete(self) -> bool:
        """
        Check whether the basic Buyer request selections exist.

        This is NOT a market compatibility check.
        It is only a UI/request completeness check.
        """

        return all(
            (
                self.market,
                self.instrument,
                self.contract,
                self.strategy,
                self.mode,
            )
        )

    def mark_ready(self) -> bool:
        """
        Mark request READY if all basic selections are present.

        No intelligence or risk calculation happens here.
        """

        if not self.is_selection_complete():
            return False

        self.status = BuyerRequestStatus.READY
        self.touch()
        return True

    def mark_submitted(self) -> None:
        """Mark request as submitted to the application layer."""
        self.status = BuyerRequestStatus.SUBMITTED
        self.touch()

    def mark_processing(self) -> None:
        """Mark request as processing."""
        self.status = BuyerRequestStatus.PROCESSING
        self.touch()

    def mark_completed(self) -> None:
        """Mark request as completed."""
        self.status = BuyerRequestStatus.COMPLETED
        self.touch()

    def mark_blocked(self, reason: Optional[str] = None) -> None:
        """
        Mark request blocked.

        Blocking authority must come from the appropriate downstream
        application/CAS layer. The UI only represents the result.
        """

        self.status = BuyerRequestStatus.BLOCKED

        if reason:
            self.metadata["blocked_reason"] = reason

        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize request into a transport-friendly dictionary."""

        data = asdict(self)

        data["mode"] = self.mode.value
        data["status"] = self.status.value

        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        return data


# ============================================================================
# BUYER RESULT CONTRACT
# ============================================================================


@dataclass
class BuyerResult:
    """
    UI presentation contract for a downstream calculated result.

    Buyer does not calculate these fields.

    The fields are intentionally optional because the real application
    contract may evolve independently from this UI layer.
    """

    request_id: str

    status: BuyerResultStatus = BuyerResultStatus.NOT_AVAILABLE

    intelligence: Optional[Mapping[str, Any]] = None
    decision: Optional[Mapping[str, Any]] = None
    risk: Optional[Mapping[str, Any]] = None
    cas: Optional[Mapping[str, Any]] = None

    result: Optional[Mapping[str, Any]] = None

    authorized_action: Optional[Mapping[str, Any]] = None

    generated_at: datetime = field(default_factory=_utc_now)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Buyer result."""

        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "intelligence": self.intelligence,
            "decision": self.decision,
            "risk": self.risk,
            "cas": self.cas,
            "result": self.result,
            "authorized_action": self.authorized_action,
            "generated_at": self.generated_at.isoformat(),
            "metadata": dict(self.metadata),
        }


# ============================================================================
# BUYER WORKSPACE STATE
# ============================================================================


@dataclass
class BuyerWorkspaceState:
    """
    Session/UI state.

    The workspace stores selections and downstream results.

    It does not own business authority.
    """

    request: BuyerRequest = field(default_factory=BuyerRequest)

    stage: BuyerStage = BuyerStage.IDLE

    result: Optional[BuyerResult] = None

    selected_market: Optional[str] = None
    selected_instrument: Optional[str] = None
    selected_contract: Optional[str] = None
    selected_strategy: Optional[str] = None

    mode: BuyerMode = BuyerMode.ANALYSIS

    initialized: bool = False

    warnings: List[str] = field(default_factory=list)
    messages: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def sync_request(self) -> None:
        """Synchronize UI selections into BuyerRequest."""

        self.request.market = self.selected_market
        self.request.instrument = self.selected_instrument
        self.request.contract = self.selected_contract
        self.request.strategy = self.selected_strategy
        self.request.mode = self.mode

        self.request.touch()

    def clear_messages(self) -> None:
        """Clear transient UI messages."""
        self.warnings.clear()
        self.messages.clear()


# ============================================================================
# BUYER WORKSPACE CONTROLLER
# ============================================================================


class BuyerWorkspaceController:
    """
    Lightweight UI controller.

    This controller intentionally does not import:
        - decision engines
        - risk engines
        - CAS implementation
        - broker adapters
        - execution managers

    Those belong downstream of the application/API/domain architecture.
    """

    def __init__(self) -> None:
        self.state = BuyerWorkspaceState()

    # ------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------

    def initialize(self) -> BuyerWorkspaceState:
        """Initialize a clean Buyer workspace."""

        self.state = BuyerWorkspaceState(
            initialized=True,
            stage=BuyerStage.IDLE,
        )

        return self.state

    # ------------------------------------------------------------------
    # SELECTIONS
    # ------------------------------------------------------------------

    def select_market(self, market: Optional[str]) -> None:
        """Set market selection."""

        self.state.selected_market = market
        self.state.stage = (
            BuyerStage.INSTRUMENT if market else BuyerStage.MARKET
        )

        self.state.sync_request()

    def select_instrument(self, instrument: Optional[str]) -> None:
        """Set instrument selection."""

        self.state.selected_instrument = instrument
        self.state.stage = (
            BuyerStage.CONTRACT if instrument else BuyerStage.INSTRUMENT
        )

        self.state.sync_request()

    def select_contract(self, contract: Optional[str]) -> None:
        """Set contract selection."""

        self.state.selected_contract = contract
        self.state.stage = (
            BuyerStage.STRATEGY if contract else BuyerStage.CONTRACT
        )

        self.state.sync_request()

    def select_strategy(self, strategy: Optional[str]) -> None:
        """Set strategy selection."""

        self.state.selected_strategy = strategy
        self.state.stage = (
            BuyerStage.MODE if strategy else BuyerStage.STRATEGY
        )

        self.state.sync_request()

    def select_mode(self, mode: BuyerMode | str) -> None:
        """Set Buyer mode."""

        if isinstance(mode, str):
            mode = BuyerMode(mode)

        self.state.mode = mode
        self.state.stage = BuyerStage.MODE

        self.state.sync_request()

    # ------------------------------------------------------------------
    # REQUEST VALIDATION
    # ------------------------------------------------------------------

    def validate_request_completeness(self) -> tuple[bool, List[str]]:
        """
        Validate only UI-level completeness.

        No market compatibility, intelligence, risk or CAS calculation
        is performed here.
        """

        self.state.sync_request()

        missing: List[str] = []

        if not self.state.request.market:
            missing.append("market")

        if not self.state.request.instrument:
            missing.append("instrument")

        if not self.state.request.contract:
            missing.append("contract")

        if not self.state.request.strategy:
            missing.append("strategy")

        if not self.state.request.mode:
            missing.append("mode")

        if missing:
            return False, missing

        return True, []

    def prepare_request(self) -> BuyerRequest:
        """
        Prepare the Buyer request for the application layer.

        This method does not submit orders and does not authorize execution.
        """

        valid, missing = self.validate_request_completeness()

        if not valid:
            self.state.request.status = BuyerRequestStatus.DRAFT
            self.state.stage = BuyerStage.ERROR

            self.state.warnings = [
                "Buyer request is incomplete.",
                f"Missing: {', '.join(missing)}",
            ]

            return self.state.request

        self.state.request.mark_ready()
        self.state.stage = BuyerStage.MODE

        self.state.messages = [
            "Buyer request is ready for application-layer processing."
        ]

        return self.state.request

    # ------------------------------------------------------------------
    # APPLY / ANALYSIS BOUNDARY
    # ------------------------------------------------------------------

    def apply_for_analysis(self) -> BuyerRequest:
        """
        Apply the selected Buyer request.

        IMPORTANT:
            Apply != Execute.

        This method only changes request state. Actual processing must be
        performed by the application/API layer.
        """

        request = self.prepare_request()

        if request.status != BuyerRequestStatus.READY:
            return request

        request.mark_submitted()

        self.state.stage = BuyerStage.ANALYSIS_REQUESTED

        self.state.messages.append(
            "Request submitted for downstream analysis."
        )

        return request

    # ------------------------------------------------------------------
    # DOWNSTREAM RESULT ATTACHMENT
    # ------------------------------------------------------------------

    def attach_result(
        self,
        result: BuyerResult,
    ) -> None:
        """
        Attach an already calculated downstream result.

        The Buyer UI does not calculate or alter:
            Intelligence
            Decision
            Risk
            CAS
            AuthorizedAction
        """

        if result.request_id != self.state.request.request_id:
            self.state.warnings.append(
                "Result request_id does not match the active Buyer request."
            )
            return

        self.state.result = result

        if result.status == BuyerResultStatus.BLOCKED:
            self.state.stage = BuyerStage.BLOCKED

        elif result.status == BuyerResultStatus.REVIEW_REQUIRED:
            self.state.stage = BuyerStage.CAS

        elif result.status in (
            BuyerResultStatus.AVAILABLE,
            BuyerResultStatus.RESTRICTED,
        ):
            self.state.stage = BuyerStage.RESULT

        elif result.status == BuyerResultStatus.ERROR:
            self.state.stage = BuyerStage.ERROR

        else:
            self.state.stage = BuyerStage.RESULT

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def reset(self) -> BuyerWorkspaceState:
        """Reset Buyer UI state without modifying production systems."""

        return self.initialize()

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """Return a complete UI workspace snapshot."""

        return {
            "request": self.state.request.to_dict(),
            "stage": self.state.stage.value,
            "result": (
                self.state.result.to_dict()
                if self.state.result is not None
                else None
            ),
            "selected_market": self.state.selected_market,
            "selected_instrument": self.state.selected_instrument,
            "selected_contract": self.state.selected_contract,
            "selected_strategy": self.state.selected_strategy,
            "mode": self.state.mode.value,
            "initialized": self.state.initialized,
            "warnings": list(self.state.warnings),
            "messages": list(self.state.messages),
            "metadata": dict(self.state.metadata),
        }


# ============================================================================
# STREAMLIT IMPORT
# ============================================================================


def _safe_import_streamlit() -> Any:
    """
    Lazy Streamlit import.

    Allows this module to be imported in environments where Streamlit
    is not installed, such as unit-test or architecture-validation runs.
    """

    try:
        import streamlit as st

        return st

    except Exception:
        return None


# ============================================================================
# SESSION STATE
# ============================================================================


BUYER_SESSION_CONTROLLER_KEY = "robomlm_buyer_workspace_controller"
BUYER_SESSION_INITIALIZED_KEY = "robomlm_buyer_initialized"


def get_buyer_controller(st: Any) -> BuyerWorkspaceController:
    """
    Get or create the Buyer workspace controller in Streamlit session state.
    """

    if BUYER_SESSION_CONTROLLER_KEY not in st.session_state:
        controller = BuyerWorkspaceController()
        controller.initialize()

        st.session_state[BUYER_SESSION_CONTROLLER_KEY] = controller
        st.session_state[BUYER_SESSION_INITIALIZED_KEY] = True

    return st.session_state[BUYER_SESSION_CONTROLLER_KEY]


# ============================================================================
# UI HELPERS
# ============================================================================


def _render_header(st: Any) -> None:
    """Render Buyer page header."""

    st.title("Buyer")

    st.caption(
        "Action-oriented intelligence workspace — "
        "Apply for analysis; execution requires downstream authorization."
    )


def _render_architecture_boundary(st: Any) -> None:
    """Render the Buyer architectural boundary."""

    with st.expander("Buyer Architecture Boundary", expanded=False):
        st.markdown(
            """
**Buyer owns**
- Market selection
- Instrument selection
- Contract selection
- Strategy selection
- Mode selection
- Analysis request
- Result presentation

**Buyer does not own**
- Decision mathematics
- Risk mathematics
- CAS authorization
- Broker order submission
- Execution authorization
- Engine implementation

**Authority:** D13 remains the decision authority.

**Safety:** CAS remains the final internal authorization boundary.

**Important:** Apply ≠ Execute.
"""
        )


def _render_request_summary(
    st: Any,
    controller: BuyerWorkspaceController,
) -> None:
    """Render current Buyer request."""

    request = controller.state.request

    st.subheader("Buyer Request")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Request ID**")
        st.code(request.request_id)

        st.write("**Market**")
        st.write(request.market or "—")

        st.write("**Instrument**")
        st.write(request.instrument or "—")

        st.write("**Contract**")
        st.write(request.contract or "—")

    with col2:
        st.write("**Strategy**")
        st.write(request.strategy or "—")

        st.write("**Mode**")
        st.write(request.mode.value)

        st.write("**Status**")
        st.write(request.status.value)

        st.write("**Stage**")
        st.write(controller.state.stage.value)


def _render_basic_selection_ui(
    st: Any,
    controller: BuyerWorkspaceController,
) -> None:
    """
    Minimal foundation selection UI.

    Real registries/selectors will be connected in later Buyer parts.
    No hardcoded market/instrument/contract/strategy universe is invented.
    """

    st.subheader("Selection")

    st.info(
        "Market, instrument, contract and strategy registries will be "
        "connected through the appropriate application/API contracts."
    )

    market = st.text_input(
        "Market",
        value=controller.state.selected_market or "",
        key="buyer_market_input",
        placeholder="Select from market registry",
    )

    instrument = st.text_input(
        "Instrument",
        value=controller.state.selected_instrument or "",
        key="buyer_instrument_input",
        placeholder="Select from instrument registry",
    )

    contract = st.text_input(
        "Contract",
        value=controller.state.selected_contract or "",
        key="buyer_contract_input",
        placeholder="Select from contract registry",
    )

    strategy = st.text_input(
        "Strategy",
        value=controller.state.selected_strategy or "",
        key="buyer_strategy_input",
        placeholder="Select from strategy registry",
    )

    mode = st.selectbox(
        "Mode",
        options=[item.value for item in BuyerMode],
        index=[item.value for item in BuyerMode].index(
            controller.state.mode.value
        ),
        key="buyer_mode_select",
    )

    if market != controller.state.selected_market:
        controller.select_market(market or None)

    if instrument != controller.state.selected_instrument:
        controller.select_instrument(instrument or None)

    if contract != controller.state.selected_contract:
        controller.select_contract(contract or None)

    if strategy != controller.state.selected_strategy:
        controller.select_strategy(strategy or None)

    selected_mode = BuyerMode(mode)

    if selected_mode != controller.state.mode:
        controller.select_mode(selected_mode)


def _render_apply_area(
    st: Any,
    controller: BuyerWorkspaceController,
) -> None:
    """Render Apply for Analysis boundary."""

    st.subheader("Analysis Request")

    valid, missing = controller.validate_request_completeness()

    if valid:
        st.success("Buyer request is complete.")
    else:
        st.warning(
            "Complete the Buyer request before applying for analysis."
        )

        if missing:
            st.write(
                "Missing: "
                + ", ".join(missing)
            )

    apply_clicked = st.button(
        "Apply for Analysis",
        key="buyer_apply_analysis",
        disabled=not valid,
        use_container_width=True,
    )

    if apply_clicked:
        request = controller.apply_for_analysis()

        if request.status == BuyerRequestStatus.SUBMITTED:
            st.success(
                "Buyer request submitted to the downstream "
                "application flow."
            )

            st.info(
                "Apply ≠ Execute. No broker order has been submitted "
                "by the Buyer UI."
            )


def _render_result_boundary(
    st: Any,
    controller: BuyerWorkspaceController,
) -> None:
    """Render downstream result placeholder."""

    st.subheader("Result")

    result = controller.state.result

    if result is None:
        st.info(
            "No downstream intelligence result is attached yet."
        )
        return

    st.write("**Result Status**")
    st.write(result.status.value)

    if result.intelligence is not None:
        st.write("**Intelligence**")
        st.json(dict(result.intelligence))

    if result.decision is not None:
        st.write("**Decision**")
        st.json(dict(result.decision))

    if result.risk is not None:
        st.write("**Risk**")
        st.json(dict(result.risk))

    if result.cas is not None:
        st.write("**CAS**")
        st.json(dict(result.cas))

    if result.result is not None:
        st.write("**Final Result**")
        st.json(dict(result.result))

    # AuthorizedAction is display-only here.
    if result.authorized_action is not None:
        st.write("**Authorized Action**")
        st.json(dict(result.authorized_action))


# ============================================================================
# MAIN PAGE RENDERER
# ============================================================================


def render_buyer_page() -> None:
    """
    Render the Buyer workspace.

    This is the Part-1 foundation renderer.

    Later Buyer parts will replace the temporary text selectors with
    canonical registry/application/API-backed selectors and downstream
    result views.
    """

    st = _safe_import_streamlit()

    if st is None:
        raise RuntimeError(
            "Streamlit is required to render the Buyer UI."
        )

    controller = get_buyer_controller(st)

    _render_header(st)

    _render_architecture_boundary(st)

    _render_basic_selection_ui(
        st,
        controller,
    )

    _render_request_summary(
        st,
        controller,
    )

    _render_apply_area(
        st,
        controller,
    )

    _render_result_boundary(
        st,
        controller,
    )

    # ---------------------------------------------------------------
    # Governance / Safety information
    # ---------------------------------------------------------------

    with st.expander("Governance", expanded=False):
        st.write(
            "Decision authority:",
            DECISION_AUTHORITY,
        )

        st.write(
            "Production mutation allowed:",
            PRODUCTION_MUTATION_ALLOWED,
        )

        st.write(
            "Direct engine control allowed:",
            DIRECT_ENGINE_CONTROL_ALLOWED,
        )

        st.write(
            "Direct broker control allowed:",
            DIRECT_BROKER_CONTROL_ALLOWED,
        )

        st.write(
            "Direct execution allowed:",
            DIRECT_EXECUTION_ALLOWED,
        )

        st.write(
            "Direct CAS override allowed:",
            DIRECT_CAS_OVERRIDE_ALLOWED,
        )

        st.caption(
            "These flags are UI architecture boundaries. "
            "They do not replace application/domain authorization."
        )

    # ---------------------------------------------------------------
    # Debug / architecture snapshot
    # ---------------------------------------------------------------

    with st.expander("Workspace Snapshot", expanded=False):
        st.json(controller.snapshot())


# ============================================================================
# COMPATIBILITY ALIASES
# ============================================================================


render_buyer = render_buyer_page
render = render_buyer_page


# ============================================================================
# PUBLIC API
# ============================================================================


__all__ = [
    "BUYER_PAGE_VERSION",
    "BUYER_UI_SCHEMA_VERSION",
    "DECISION_AUTHORITY",
    "PRODUCTION_MUTATION_ALLOWED",
    "DIRECT_ENGINE_CONTROL_ALLOWED",
    "DIRECT_BROKER_CONTROL_ALLOWED",
    "DIRECT_EXECUTION_ALLOWED",
    "DIRECT_CAS_OVERRIDE_ALLOWED",
    "BuyerMode",
    "BuyerStage",
    "BuyerRequestStatus",
    "BuyerResultStatus",
    "BuyerRequest",
    "BuyerResult",
    "BuyerWorkspaceState",
    "BuyerWorkspaceController",
    "get_buyer_controller",
    "render_buyer_page",
    "render_buyer",
    "render",
]
```
