from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# ROBOMLM_PLUS TERMINAL PAGE
# ============================================================

TERMINAL_PAGE_ENGINE = "ROBOMLM_PLUS_UI_TERMINAL"
TERMINAL_PAGE_VERSION = "1.0"

TERMINAL_PAGE_NAME = "Terminal"
TERMINAL_PAGE_TITLE = "ROBOMLM Intelligence Terminal"

TERMINAL_ROUTE = "/terminal"


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

TERMINAL_UI_AUTHORITY: Dict[str, bool] = {

    # Allowed
    "terminal_presentation": True,
    "market_overview_presentation": True,
    "intelligence_presentation": True,
    "evidence_presentation": True,
    "risk_presentation": True,
    "cas_presentation": True,
    "d13_presentation": True,
    "portfolio_presentation": True,
    "navigation": True,

    # Forbidden
    "market_data_generation": False,
    "evidence_generation": False,
    "intelligence_generation": False,
    "decision_generation": False,
    "d13_modification": False,
    "risk_override": False,
    "cas_bypass": False,
    "execution": False,
    "order_mutation": False,
    "position_mutation": False,
    "portfolio_mutation": False,
    "upstream_mutation": False,
}


# ============================================================
# ENUMS
# ============================================================

class TerminalPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class TerminalMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    MARKET = "MARKET"
    INTELLIGENCE = "INTELLIGENCE"
    EVIDENCE = "EVIDENCE"
    DECISION = "DECISION"
    RISK = "RISK"
    PORTFOLIO = "PORTFOLIO"


class MarketState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PREOPEN = "PREOPEN"
    POSTMARKET = "POSTMARKET"
    HOLIDAY = "HOLIDAY"
    UNKNOWN = "UNKNOWN"


class IntelligenceBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class SignalStrength(str, Enum):
    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"
    UNKNOWN = "UNKNOWN"


class TerminalPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# HELPERS
# ============================================================

def _terminal_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _terminal_bool(
    value: Any,
    default: bool = False,
) -> bool:

    if isinstance(value, bool):
        return value

    if value is None:
        return default

    return bool(value)


def _terminal_enum(
    enum_cls: Any,
    value: Any,
    default: Any,
):

    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(value)

    except Exception:
        return default


def _terminal_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


# ============================================================
# IDENTITY
# ============================================================

@dataclass
class TerminalIdentityView:

    user_id: str = ""

    display_name: str = ""

    email: str = ""

    authenticated: bool = False

    plus_enabled: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# MARKET CONTEXT
# ============================================================

@dataclass
class MarketContextView:

    market_name: str = ""

    market_state: MarketState = (
        MarketState.UNKNOWN
    )

    active_symbol: str = ""

    active_contract: str = ""

    market_session: str = ""

    market_timezone: str = ""

    last_update: Optional[
        datetime
    ] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# EVIDENCE CARD
# ============================================================

@dataclass
class EvidenceCardView:

    evidence_id: str = ""

    title: str = ""

    value: str = ""

    confidence: float = 0.0

    priority: TerminalPriority = (
        TerminalPriority.NORMAL
    )

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# INTELLIGENCE CARD
# ============================================================

@dataclass
class IntelligenceCardView:

    intelligence_id: str = ""

    title: str = ""

    bias: IntelligenceBias = (
        IntelligenceBias.UNKNOWN
    )

    strength: SignalStrength = (
        SignalStrength.UNKNOWN
    )

    summary: str = ""

    confidence: float = 0.0

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# D13 OUTLOOK CARD
# ============================================================

@dataclass
class D13OutlookView:

    outlook_id: str = ""

    direction: str = ""

    confidence: float = 0.0

    summary: str = ""

    horizon: str = ""

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CAS CARD
# ============================================================

@dataclass
class CASView:

    cas_score: float = 0.0

    readiness: str = ""

    summary: str = ""

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# RISK CARD
# ============================================================

@dataclass
class RiskView:

    risk_score: float = 0.0

    risk_level: str = ""

    summary: str = ""

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PORTFOLIO SNAPSHOT
# ============================================================

@dataclass
class PortfolioSnapshotView:

    account_name: str = ""

    equity: float = 0.0

    balance: float = 0.0

    pnl: float = 0.0

    positions: int = 0

    visible: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# TERMINAL SUMMARY
# ============================================================

@dataclass
class TerminalSummaryView:

    market_state: MarketState = (
        MarketState.UNKNOWN
    )

    intelligence_bias: (
        IntelligenceBias
    ) = IntelligenceBias.UNKNOWN

    evidence_count: int = 0

    intelligence_count: int = 0

    portfolio_visible: bool = False

    risk_visible: bool = False

    cas_visible: bool = False

    authenticated: bool = False

    plus_enabled: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
# ============================================================
# TERMINAL SOURCE CONTRACT
# ============================================================

@dataclass(frozen=True)
class TerminalSourceState:

    identity: TerminalIdentityView = field(
        default_factory=TerminalIdentityView
    )

    market_context: MarketContextView = field(
        default_factory=MarketContextView
    )

    evidence_cards: List[
        EvidenceCardView
    ] = field(default_factory=list)

    intelligence_cards: List[
        IntelligenceCardView
    ] = field(default_factory=list)

    d13_outlook: D13OutlookView = field(
        default_factory=D13OutlookView
    )

    cas: CASView = field(
        default_factory=CASView
    )

    risk: RiskView = field(
        default_factory=RiskView
    )

    portfolio: PortfolioSnapshotView = field(
        default_factory=PortfolioSnapshotView
    )

    source_available: bool = False

    source_errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_terminal_identity(
    identity: Optional[
        TerminalIdentityView
    ],
) -> TerminalIdentityView:

    if identity is None:
        return TerminalIdentityView()

    return TerminalIdentityView(
        user_id=_terminal_text(
            identity.user_id
        ),
        display_name=_terminal_text(
            identity.display_name
        ),
        email=_terminal_text(
            identity.email
        ),
        authenticated=_terminal_bool(
            identity.authenticated
        ),
        plus_enabled=_terminal_bool(
            identity.plus_enabled
        ),
        metadata=dict(
            identity.metadata or {}
        ),
    )


def normalize_market_context(
    context: Optional[
        MarketContextView
    ],
) -> MarketContextView:

    if context is None:
        return MarketContextView()

    return MarketContextView(
        market_name=_terminal_text(
            context.market_name
        ),
        market_state=_terminal_enum(
            MarketState,
            context.market_state,
            MarketState.UNKNOWN,
        ),
        active_symbol=_terminal_text(
            context.active_symbol
        ),
        active_contract=_terminal_text(
            context.active_contract
        ),
        market_session=_terminal_text(
            context.market_session
        ),
        market_timezone=_terminal_text(
            context.market_timezone
        ),
        last_update=context.last_update,
        metadata=dict(
            context.metadata or {}
        ),
    )


def normalize_evidence_cards(
    cards: Optional[
        Sequence[EvidenceCardView]
    ],
) -> List[EvidenceCardView]:

    result: List[
        EvidenceCardView
    ] = []

    for card in cards or []:

        if not isinstance(
            card,
            EvidenceCardView,
        ):
            continue

        result.append(
            EvidenceCardView(
                evidence_id=_terminal_text(
                    card.evidence_id
                ),
                title=_terminal_text(
                    card.title
                ),
                value=_terminal_text(
                    card.value
                ),
                confidence=float(
                    card.confidence or 0.0
                ),
                priority=_terminal_enum(
                    TerminalPriority,
                    card.priority,
                    TerminalPriority.NORMAL,
                ),
                visible=_terminal_bool(
                    card.visible,
                    True,
                ),
                metadata=dict(
                    card.metadata or {}
                ),
            )
        )

    return result


def normalize_intelligence_cards(
    cards: Optional[
        Sequence[
            IntelligenceCardView
        ]
    ],
) -> List[
    IntelligenceCardView
]:

    result: List[
        IntelligenceCardView
    ] = []

    for card in cards or []:

        if not isinstance(
            card,
            IntelligenceCardView,
        ):
            continue

        result.append(
            IntelligenceCardView(
                intelligence_id=
                _terminal_text(
                    card.intelligence_id
                ),
                title=_terminal_text(
                    card.title
                ),
                bias=_terminal_enum(
                    IntelligenceBias,
                    card.bias,
                    IntelligenceBias.UNKNOWN,
                ),
                strength=_terminal_enum(
                    SignalStrength,
                    card.strength,
                    SignalStrength.UNKNOWN,
                ),
                summary=_terminal_text(
                    card.summary
                ),
                confidence=float(
                    card.confidence or 0.0
                ),
                visible=_terminal_bool(
                    card.visible,
                    True,
                ),
                metadata=dict(
                    card.metadata or {}
                ),
            )
        )

    return result


# ============================================================
# SOURCE NORMALIZATION
# ============================================================

def normalize_terminal_source(
    source: Optional[
        TerminalSourceState
    ],
) -> TerminalSourceState:

    if source is None:

        return TerminalSourceState(
            source_available=False,
            source_errors=[
                "TERMINAL_SOURCE_NOT_AVAILABLE"
            ],
            metadata={
                "presentation_only": True,
            },
        )

    return TerminalSourceState(
        identity=
        normalize_terminal_identity(
            source.identity
        ),

        market_context=
        normalize_market_context(
            source.market_context
        ),

        evidence_cards=
        normalize_evidence_cards(
            source.evidence_cards
        ),

        intelligence_cards=
        normalize_intelligence_cards(
            source.intelligence_cards
        ),

        d13_outlook=
        source.d13_outlook,

        cas=
        source.cas,

        risk=
        source.risk,

        portfolio=
        source.portfolio,

        source_available=
        _terminal_bool(
            source.source_available
        ),

        source_errors=list(
            source.source_errors or []
        ),

        metadata=dict(
            source.metadata or {}
        ),
    )


# ============================================================
# PAGE STATUS EVALUATION
# ============================================================

def evaluate_terminal_status(
    source: TerminalSourceState,
) -> TerminalPageStatus:

    if not (
        source.identity.authenticated
    ):
        return (
            TerminalPageStatus.LOCKED
        )

    if not (
        source.source_available
    ):
        return (
            TerminalPageStatus.DEGRADED
        )

    if source.source_errors:
        return (
            TerminalPageStatus.DEGRADED
        )

    return (
        TerminalPageStatus.READY
    )


# ============================================================
# FILTERING
# ============================================================

def filter_visible_evidence(
    cards: Sequence[
        EvidenceCardView
    ],
) -> List[
    EvidenceCardView
]:

    return [
        card
        for card in cards
        if card.visible
    ]


def filter_visible_intelligence(
    cards: Sequence[
        IntelligenceCardView
    ],
) -> List[
    IntelligenceCardView
]:

    return [
        card
        for card in cards
        if card.visible
    ]


# ============================================================
# INTELLIGENCE BIAS
# ============================================================

def derive_terminal_bias(
    cards: Sequence[
        IntelligenceCardView
    ],
) -> IntelligenceBias:

    bullish = 0
    bearish = 0
    neutral = 0

    for card in cards:

        if (
            card.bias
            == IntelligenceBias.BULLISH
        ):
            bullish += 1

        elif (
            card.bias
            == IntelligenceBias.BEARISH
        ):
            bearish += 1

        elif (
            card.bias
            == IntelligenceBias.NEUTRAL
        ):
            neutral += 1

    if bullish > bearish:
        return (
            IntelligenceBias.BULLISH
        )

    if bearish > bullish:
        return (
            IntelligenceBias.BEARISH
        )

    if neutral:
        return (
            IntelligenceBias.NEUTRAL
        )

    return (
        IntelligenceBias.UNKNOWN
    )


# ============================================================
# TERMINAL SUMMARY
# ============================================================

def build_terminal_summary(
    source: TerminalSourceState,
) -> TerminalSummaryView:

    evidence_cards = (
        filter_visible_evidence(
            source.evidence_cards
        )
    )

    intelligence_cards = (
        filter_visible_intelligence(
            source.intelligence_cards
        )
    )

    bias = derive_terminal_bias(
        intelligence_cards
    )

    return TerminalSummaryView(

        market_state=
        source.market_context.market_state,

        intelligence_bias=bias,

        evidence_count=len(
            evidence_cards
        ),

        intelligence_count=len(
            intelligence_cards
        ),

        portfolio_visible=
        source.portfolio.visible,

        risk_visible=
        source.risk.visible,

        cas_visible=
        source.cas.visible,

        authenticated=
        source.identity.authenticated,

        plus_enabled=
        source.identity.plus_enabled,

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# TERMINAL ACTIONS
# ============================================================

@dataclass
class TerminalAction:

    action_id: str = ""

    label: str = ""

    route: str = ""

    enabled: bool = True

    visible: bool = True

    priority: TerminalPriority = (
        TerminalPriority.NORMAL
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


DEFAULT_TERMINAL_ACTIONS = [

    TerminalAction(
        action_id="market",
        label="Market Context",
        route="/terminal/market",
    ),

    TerminalAction(
        action_id="evidence",
        label="Evidence Center",
        route="/terminal/evidence",
    ),

    TerminalAction(
        action_id="intelligence",
        label="Intelligence",
        route="/terminal/intelligence",
    ),

    TerminalAction(
        action_id="decision",
        label="D13 Outlook",
        route="/terminal/decision",
    ),

    TerminalAction(
        action_id="risk",
        label="Risk Center",
        route="/terminal/risk",
    ),

    TerminalAction(
        action_id="portfolio",
        label="Portfolio",
        route="/terminal/portfolio",
    ),
]


def build_terminal_actions(
    authenticated: bool,
) -> List[TerminalAction]:

    actions: List[
        TerminalAction
    ] = []

    for action in (
        DEFAULT_TERMINAL_ACTIONS
    ):

        actions.append(
            TerminalAction(
                action_id=
                action.action_id,

                label=
                action.label,

                route=
                action.route,

                enabled=
                authenticated,

                visible=True,

                priority=
                action.priority,

                metadata={
                    "presentation_only":
                    True
                },
            )
        )

    return actions
# ============================================================
# PAGE VIEW CONTRACT
# ============================================================

@dataclass
class TerminalPageView:

    page_name: str = TERMINAL_PAGE_NAME

    page_title: str = TERMINAL_PAGE_TITLE

    route: str = TERMINAL_ROUTE

    status: TerminalPageStatus = (
        TerminalPageStatus.UNKNOWN
    )

    mode: TerminalMode = (
        TerminalMode.OVERVIEW
    )

    identity: TerminalIdentityView = field(
        default_factory=TerminalIdentityView
    )

    market_context: MarketContextView = field(
        default_factory=MarketContextView
    )

    evidence_cards: List[
        EvidenceCardView
    ] = field(default_factory=list)

    intelligence_cards: List[
        IntelligenceCardView
    ] = field(default_factory=list)

    d13_outlook: D13OutlookView = field(
        default_factory=D13OutlookView
    )

    cas: CASView = field(
        default_factory=CASView
    )

    risk: RiskView = field(
        default_factory=RiskView
    )

    portfolio: PortfolioSnapshotView = field(
        default_factory=PortfolioSnapshotView
    )

    summary: TerminalSummaryView = field(
        default_factory=TerminalSummaryView
    )

    actions: List[
        TerminalAction
    ] = field(default_factory=list)

    generated_at: Optional[
        datetime
    ] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# PAGE COMPOSITION
# ============================================================

@dataclass(frozen=True)
class TerminalPageComposition:

    page: TerminalPageView

    summary: TerminalSummaryView

    evidence_cards: List[
        EvidenceCardView
    ] = field(default_factory=list)

    intelligence_cards: List[
        IntelligenceCardView
    ] = field(default_factory=list)

    actions: List[
        TerminalAction
    ] = field(default_factory=list)

    warnings: List[str] = field(
        default_factory=list
    )

    errors: List[str] = field(
        default_factory=list
    )

    generated_at: datetime = field(
        default_factory=_terminal_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# TERMINAL COMPOSER
# ============================================================

def compose_terminal_page(
    source: Optional[
        TerminalSourceState
    ] = None,
    mode: TerminalMode = (
        TerminalMode.OVERVIEW
    ),
) -> TerminalPageComposition:

    source = (
        normalize_terminal_source(
            source
        )
    )

    status = (
        evaluate_terminal_status(
            source
        )
    )

    summary = (
        build_terminal_summary(
            source
        )
    )

    evidence_cards = (
        filter_visible_evidence(
            source.evidence_cards
        )
    )

    intelligence_cards = (
        filter_visible_intelligence(
            source.intelligence_cards
        )
    )

    actions = (
        build_terminal_actions(
            source.identity.authenticated
        )
    )

    page = TerminalPageView(

        page_name=
        TERMINAL_PAGE_NAME,

        page_title=
        TERMINAL_PAGE_TITLE,

        route=
        TERMINAL_ROUTE,

        status=status,

        mode=mode,

        identity=
        source.identity,

        market_context=
        source.market_context,

        evidence_cards=
        evidence_cards,

        intelligence_cards=
        intelligence_cards,

        d13_outlook=
        source.d13_outlook,

        cas=
        source.cas,

        risk=
        source.risk,

        portfolio=
        source.portfolio,

        summary=
        summary,

        actions=
        actions,

        generated_at=
        _terminal_now(),

        metadata={
            "presentation_only": True,
            "execution": False,
            "d13_modification": False,
            "risk_override": False,
            "cas_bypass": False,
        },
    )

    warnings: List[str] = []
    errors: List[str] = []

    if not source.source_available:
        warnings.append(
            "SOURCE_UNAVAILABLE"
        )

    errors.extend(
        source.source_errors
    )

    return TerminalPageComposition(

        page=page,

        summary=summary,

        evidence_cards=
        evidence_cards,

        intelligence_cards=
        intelligence_cards,

        actions=
        actions,

        warnings=
        warnings,

        errors=
        errors,

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# TERMINAL STATE
# ============================================================

@dataclass
class TerminalPageState:

    user_id: str = ""

    authenticated: bool = False

    plus_enabled: bool = False

    initialized: bool = False

    ready: bool = False

    current_route: str = (
        TERMINAL_ROUTE
    )

    current_mode: TerminalMode = (
        TerminalMode.OVERVIEW
    )

    status: TerminalPageStatus = (
        TerminalPageStatus.UNKNOWN
    )

    interaction_count: int = 0

    refresh_count: int = 0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_terminal_state(
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> TerminalPageState:

    return TerminalPageState(

        user_id=
        _terminal_text(user_id),

        authenticated=
        authenticated,

        plus_enabled=
        plus_enabled,

        initialized=False,

        ready=False,

        current_route=
        TERMINAL_ROUTE,

        current_mode=
        TerminalMode.OVERVIEW,

        status=
        TerminalPageStatus.UNKNOWN,

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# ROUTING
# ============================================================

TERMINAL_ROUTE_MAP = {

    "/terminal":
        TerminalMode.OVERVIEW,

    "/terminal/market":
        TerminalMode.MARKET,

    "/terminal/intelligence":
        TerminalMode.INTELLIGENCE,

    "/terminal/evidence":
        TerminalMode.EVIDENCE,

    "/terminal/decision":
        TerminalMode.DECISION,

    "/terminal/risk":
        TerminalMode.RISK,

    "/terminal/portfolio":
        TerminalMode.PORTFOLIO,
}


def route_to_terminal_mode(
    route: str,
) -> TerminalMode:

    return TERMINAL_ROUTE_MAP.get(
        route,
        TerminalMode.OVERVIEW,
    )


# ============================================================
# INTERACTION
# ============================================================

class TerminalInteraction(
    str,
    Enum,
):

    OPEN_OVERVIEW = (
        "OPEN_OVERVIEW"
    )

    OPEN_MARKET = (
        "OPEN_MARKET"
    )

    OPEN_INTELLIGENCE = (
        "OPEN_INTELLIGENCE"
    )

    OPEN_EVIDENCE = (
        "OPEN_EVIDENCE"
    )

    OPEN_DECISION = (
        "OPEN_DECISION"
    )

    OPEN_RISK = (
        "OPEN_RISK"
    )

    OPEN_PORTFOLIO = (
        "OPEN_PORTFOLIO"
    )

    REFRESH = "REFRESH"

    NONE = "NONE"


TERMINAL_INTERACTION_ROUTE = {

    TerminalInteraction.OPEN_OVERVIEW:
        "/terminal",

    TerminalInteraction.OPEN_MARKET:
        "/terminal/market",

    TerminalInteraction.OPEN_INTELLIGENCE:
        "/terminal/intelligence",

    TerminalInteraction.OPEN_EVIDENCE:
        "/terminal/evidence",

    TerminalInteraction.OPEN_DECISION:
        "/terminal/decision",

    TerminalInteraction.OPEN_RISK:
        "/terminal/risk",

    TerminalInteraction.OPEN_PORTFOLIO:
        "/terminal/portfolio",
}


@dataclass(frozen=True)
class TerminalInteractionResult:

    interaction: TerminalInteraction

    allowed: bool
    allowed: bool
    route: str
    mode: TerminalMode
    reason: str
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# CONTROLLER
# ============================================================

class TerminalPageController:

    def __init__(
        self,
        state: Optional[
            TerminalPageState
        ] = None,
    ):

        self._state = (
            state
            if state is not None
            else create_terminal_state()
        )

        self._last_composition: Optional[
            TerminalPageComposition
        ] = None

    @property
    def state(
        self,
    ) -> TerminalPageState:
        return self._state

    @property
    def last_composition(
        self,
    ) -> Optional[
        TerminalPageComposition
    ]:
        return self._last_composition

    def initialize(
        self,
        source: TerminalSourceState,
    ) -> TerminalPageComposition:

        source = (
            normalize_terminal_source(
                source
            )
        )

        self._state.user_id = (
            source.identity.user_id
        )

        self._state.authenticated = (
            source.identity.authenticated
        )

        self._state.plus_enabled = (
            source.identity.plus_enabled
        )

        self._state.initialized = True

        composition = self.compose(
            source
        )

        self._state.ready = (
            composition.page.status
            == TerminalPageStatus.READY
        )

        return composition

    def compose(
        self,
        source: TerminalSourceState,
    ) -> TerminalPageComposition:

        composition = (
            compose_terminal_page(
                source=source,
                mode=self._state.current_mode,
            )
        )

        self._last_composition = (
            composition
        )

        self._state.status = (
            composition.page.status
        )

        return composition
# ============================================================
# NAVIGATION EXECUTION
# ============================================================

def execute_terminal_interaction(
    state: TerminalPageState,
    interaction: TerminalInteraction,
) -> TerminalInteractionResult:

    if (
        interaction
        == TerminalInteraction.NONE
    ):
        return TerminalInteractionResult(
            interaction=interaction,
            allowed=False,
            route=state.current_route,
            mode=state.current_mode,
            reason="NO_INTERACTION",
        )

    if (
        interaction
        == TerminalInteraction.REFRESH
    ):
        return TerminalInteractionResult(
            interaction=interaction,
            allowed=state.authenticated,
            route=state.current_route,
            mode=state.current_mode,
            reason=(
                "REFRESH_ALLOWED"
                if state.authenticated
                else "AUTH_REQUIRED"
            ),
        )

    route = (
        TERMINAL_INTERACTION_ROUTE
        .get(interaction)
    )

    if not route:
        return TerminalInteractionResult(
            interaction=interaction,
            allowed=False,
            route=state.current_route,
            mode=state.current_mode,
            reason="ROUTE_NOT_FOUND",
        )

    if not state.authenticated:
        return TerminalInteractionResult(
            interaction=interaction,
            allowed=False,
            route=state.current_route,
            mode=state.current_mode,
            reason="AUTH_REQUIRED",
        )

    return TerminalInteractionResult(
        interaction=interaction,
        allowed=True,
        route=route,
        mode=route_to_terminal_mode(
            route
        ),
        reason="ALLOWED",
    )


def navigate_terminal(
    controller: TerminalPageController,
    interaction: TerminalInteraction,
) -> TerminalInteractionResult:

    result = (
        execute_terminal_interaction(
            controller.state,
            interaction,
        )
    )

    if result.allowed:

        controller.state.current_route = (
            result.route
        )

        controller.state.current_mode = (
            result.mode
        )

        controller.state.interaction_count += 1

        if (
            interaction
            == TerminalInteraction.REFRESH
        ):
            controller.state.refresh_count += 1

    return result


# ============================================================
# SNAPSHOT CONTRACT
# ============================================================

@dataclass(frozen=True)
class TerminalPageSnapshot:

    state: TerminalPageState

    composition: TerminalPageComposition

    generated_at: datetime = field(
        default_factory=_terminal_now
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_terminal_snapshot(
    controller: TerminalPageController,
    source: TerminalSourceState,
) -> TerminalPageSnapshot:

    composition = (
        controller.compose(
            source
        )
    )

    return TerminalPageSnapshot(
        state=controller.state,
        composition=composition,
        metadata={
            "presentation_only": True,
            "execution": False,
            "decision_generation": False,
            "d13_modification": False,
        },
    )


# ============================================================
# SERIALIZATION
# ============================================================

def _serialize_terminal_value(
    value: Any,
) -> Any:

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    if isinstance(
        value,
        datetime,
    ):
        return value.isoformat()

    if isinstance(
        value,
        dict,
    ):
        return {
            str(k):
            _serialize_terminal_value(v)
            for k, v
            in value.items()
        }

    if isinstance(
        value,
        (list, tuple),
    ):
        return [
            _serialize_terminal_value(
                item
            )
            for item in value
        ]

    if hasattr(
        value,
        "__dataclass_fields__",
    ):
        return {
            field_name:
            _serialize_terminal_value(
                getattr(
                    value,
                    field_name,
                )
            )
            for field_name
            in value.__dataclass_fields__
        }

    return value


def serialize_terminal_page(
    page: TerminalPageView,
) -> Dict[str, Any]:

    return (
        _serialize_terminal_value(
            page
        )
    )


def serialize_terminal_state(
    state: TerminalPageState,
) -> Dict[str, Any]:

    return (
        _serialize_terminal_value(
            state
        )
    )


def serialize_terminal_snapshot(
    snapshot: TerminalPageSnapshot,
) -> Dict[str, Any]:

    return (
        _serialize_terminal_value(
            snapshot
        )
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_terminal_page(
    page: TerminalPageView,
) -> List[str]:

    errors: List[str] = []

    if page.page_name != (
        TERMINAL_PAGE_NAME
    ):
        errors.append(
            "INVALID_PAGE_NAME"
        )

    if page.route != (
        TERMINAL_ROUTE
    ):
        errors.append(
            "INVALID_ROUTE"
        )

    if (
        page.metadata.get(
            "execution"
        )
        is True
    ):
        errors.append(
            "EXECUTION_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "d13_modification"
        )
        is True
    ):
        errors.append(
            "D13_MUTATION_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "risk_override"
        )
        is True
    ):
        errors.append(
            "RISK_OVERRIDE_FORBIDDEN"
        )

    if (
        page.metadata.get(
            "cas_bypass"
        )
        is True
    ):
        errors.append(
            "CAS_BYPASS_FORBIDDEN"
        )

    return errors


def validate_terminal_state(
    state: TerminalPageState,
) -> List[str]:

    errors: List[str] = []

    if (
        state.interaction_count
        < 0
    ):
        errors.append(
            "NEGATIVE_INTERACTIONS"
        )

    if (
        state.refresh_count
        < 0
    ):
        errors.append(
            "NEGATIVE_REFRESH_COUNT"
        )

    return errors


def validate_terminal_composition(
    composition: TerminalPageComposition,
) -> List[str]:

    errors: List[str] = []

    errors.extend(
        validate_terminal_page(
            composition.page
        )
    )

    return errors


# ============================================================
# HEALTH
# ============================================================

@dataclass(frozen=True)
class TerminalPageHealth:

    engine: str = (
        TERMINAL_PAGE_ENGINE
    )

    version: str = (
        TERMINAL_PAGE_VERSION
    )

    initialized: bool = False

    ready: bool = False

    status: TerminalPageStatus = (
        TerminalPageStatus.UNKNOWN
    )

    validation_errors: List[
        str
    ] = field(
        default_factory=list
    )

    operational: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_terminal_health(
    controller: TerminalPageController,
    composition: Optional[
        TerminalPageComposition
    ] = None,
) -> TerminalPageHealth:

    errors: List[str] = []

    errors.extend(
        validate_terminal_state(
            controller.state
        )
    )

    if composition:
        errors.extend(
            validate_terminal_composition(
                composition
            )
        )

    operational = (
        controller.state.initialized
        and controller.state.ready
        and not errors
    )

    return TerminalPageHealth(
        initialized=
        controller.state.initialized,

        ready=
        controller.state.ready,

        status=
        controller.state.status,

        validation_errors=
        errors,

        operational=
        operational,

        metadata={
            "presentation_only": True,
        },
    )


# ============================================================
# DIAGNOSTIC CHECK
# ============================================================

def terminal_operational_check(
    controller: Optional[
        TerminalPageController
    ] = None,
) -> Dict[str, Any]:

    if controller is None:
        controller = (
            TerminalPageController()
        )

    health = (
        build_terminal_health(
            controller
        )
    )

    return {

        "engine":
        TERMINAL_PAGE_ENGINE,

        "version":
        TERMINAL_PAGE_VERSION,

        "initialized":
        health.initialized,

        "ready":
        health.ready,

        "status":
        health.status.value,

        "operational":
        health.operational,

        "validation_errors":
        list(
            health.validation_errors
        ),

        "presentation_only":
        True,

        "execution":
        False,

        "decision_generation":
        False,

        "d13_modification":
        False,

        "risk_override":
        False,

        "cas_bypass":
        False,

        "upstream_mutation":
        False,
    }
# ============================================================
# AUTHORITY VALIDATION
# ============================================================

def validate_terminal_authority(
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> List[str]:

    metadata = metadata or {}

    errors: List[str] = []

    forbidden_flags = {

        "market_data_generation":
            False,

        "evidence_generation":
            False,

        "intelligence_generation":
            False,

        "decision_generation":
            False,

        "execution":
            False,

        "order_mutation":
            False,

        "position_mutation":
            False,

        "portfolio_mutation":
            False,

        "d13_modification":
            False,

        "risk_override":
            False,

        "cas_bypass":
            False,

        "upstream_mutation":
            False,
    }

    for key in forbidden_flags:

        if metadata.get(key) is True:

            errors.append(
                f"FORBIDDEN_AUTHORITY:{key}"
            )

    return errors


# ============================================================
# DIAGNOSTICS
# ============================================================

def diagnose_terminal_page(
    controller: TerminalPageController,
    composition: Optional[
        TerminalPageComposition
    ] = None,
) -> Dict[str, Any]:

    if composition is None:
        composition = (
            controller.last_composition
        )

    health = (
        build_terminal_health(
            controller,
            composition,
        )
    )

    authority_errors: List[
        str
    ] = []

    if composition:

        authority_errors.extend(
            validate_terminal_authority(
                composition.page.metadata
            )
        )

    return {

        "engine":
        TERMINAL_PAGE_ENGINE,

        "version":
        TERMINAL_PAGE_VERSION,

        "page":
        TERMINAL_PAGE_NAME,

        "route":
        controller.state.current_route,

        "mode":
        controller.state.current_mode.value,

        "status":
        controller.state.status.value,

        "state":
        serialize_terminal_state(
            controller.state
        ),

        "health":
        _serialize_terminal_value(
            health
        ),

        "authority_errors":
        authority_errors,

        "authority_valid":
        not authority_errors,

        "operational":
        health.operational,

        "presentation_only":
        True,
    }


# ============================================================
# CONTRACT MANIFEST
# ============================================================

def terminal_contract_manifest(
) -> Dict[str, Any]:

    return {

        "engine":
        TERMINAL_PAGE_ENGINE,

        "version":
        TERMINAL_PAGE_VERSION,

        "page":
        TERMINAL_PAGE_NAME,

        "layer":
        "UI_PRESENTATION",

        "role":
        (
            "ROBOMLM_MAIN_TERMINAL"
        ),

        "responsibilities": [

            "MARKET_CONTEXT_PRESENTATION",

            "EVIDENCE_PRESENTATION",

            "INTELLIGENCE_PRESENTATION",

            "D13_OUTLOOK_PRESENTATION",

            "CAS_PRESENTATION",

            "RISK_PRESENTATION",

            "PORTFOLIO_PRESENTATION",

            "NAVIGATION",

            "WORKSPACE_OVERVIEW",
        ],

        "forbidden": [

            "MARKET_DATA_GENERATION",

            "EVIDENCE_GENERATION",

            "INTELLIGENCE_GENERATION",

            "DECISION_GENERATION",

            "EXECUTION",

            "ORDER_MUTATION",

            "POSITION_MUTATION",

            "PORTFOLIO_MUTATION",

            "D13_MODIFICATION",

            "RISK_OVERRIDE",

            "CAS_BYPASS",
        ],

        "presentation_only":
        True,
    }


# ============================================================
# MODULE VALIDATION
# ============================================================

def validate_terminal_module(
) -> Dict[str, Any]:

    controller = (
        TerminalPageController()
    )

    source = (
        TerminalSourceState(
            identity=
            TerminalIdentityView(
                authenticated=False
            ),
            source_available=False,
            source_errors=[
                "DEFAULT_SOURCE"
            ],
        )
    )

    composition = (
        compose_terminal_page(
            source
        )
    )

    errors: List[str] = []

    errors.extend(
        validate_terminal_state(
            controller.state
        )
    )

    errors.extend(
        validate_terminal_composition(
            composition
        )
    )

    errors.extend(
        validate_terminal_authority(
            composition.page.metadata
        )
    )

    manifest = (
        terminal_contract_manifest()
    )

    if (
        manifest["layer"]
        != "UI_PRESENTATION"
    ):
        errors.append(
            "INVALID_LAYER"
        )

    return {

        "engine":
        TERMINAL_PAGE_ENGINE,

        "version":
        TERMINAL_PAGE_VERSION,

        "valid":
        not errors,

        "errors":
        errors,

        "presentation_only":
        True,

        "execution":
        False,

        "decision_generation":
        False,

        "d13_modification":
        False,
    }


# ============================================================
# DEFAULT SNAPSHOT
# ============================================================

def default_terminal_snapshot(
) -> TerminalPageSnapshot:

    controller = (
        TerminalPageController()
    )

    source = (
        TerminalSourceState(
            identity=
            TerminalIdentityView(),
            market_context=
            MarketContextView(),
            source_available=False,
        )
    )

    return (
        build_terminal_snapshot(
            controller,
            source,
        )
    )


# ============================================================
# FACTORY
# ============================================================

def create_default_terminal(
) -> TerminalPageController:

    return (
        TerminalPageController(
            create_terminal_state()
        )
    )


# ============================================================
# SELF CHECK
# ============================================================

def terminal_self_check(
) -> Dict[str, Any]:

    validation = (
        validate_terminal_module()
    )

    diagnostics = (
        diagnose_terminal_page(
            create_default_terminal()
        )
    )

    return {

        "engine":
        TERMINAL_PAGE_ENGINE,

        "version":
        TERMINAL_PAGE_VERSION,

        "module_valid":
        validation["valid"],

        "diagnostics":
        diagnostics,

        "presentation_only":
        True,
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [

    # Core
    "TERMINAL_PAGE_ENGINE",
    "TERMINAL_PAGE_VERSION",
    "TERMINAL_PAGE_NAME",
    "TERMINAL_ROUTE",

    # Identity
    "TerminalIdentityView",

    # Market
    "MarketContextView",

    # Cards
    "EvidenceCardView",
    "IntelligenceCardView",
    "D13OutlookView",
    "CASView",
    "RiskView",
    "PortfolioSnapshotView",

    # Source
    "TerminalSourceState",

    # Summary
    "TerminalSummaryView",

    # Page
    "TerminalPageView",
    "TerminalPageComposition",

    # State
    "TerminalPageState",

    # Controller
    "TerminalPageController",

    # Snapshot
    "TerminalPageSnapshot",

    # Health
    "TerminalPageHealth",

    # Actions
    "TerminalAction",

    # Factory
    "create_default_terminal",

    # Compose
    "compose_terminal_page",

    # Navigation
    "navigate_terminal",

    # Diagnostics
    "diagnose_terminal_page",

    # Validation
    "validate_terminal_module",

    # Manifest
    "terminal_contract_manifest",

    # Snapshot
    "default_terminal_snapshot",

    # Self Check
    "terminal_self_check",
]