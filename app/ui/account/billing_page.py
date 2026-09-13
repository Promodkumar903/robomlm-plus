# app/ui/account/billing_page.py

"""
ROBOMLM_PLUS — Billing Page
===========================

Presentation-only billing and subscription workspace.

Responsibilities
----------------
- Present billing/subscription information supplied by upstream services.
- Present current plan, billing status, renewal information and invoice summaries.
- Present masked payment-method information when supplied upstream.
- Present billing-related navigation/actions without owning their execution.
- Preserve upstream billing truth.

Authority Boundary
------------------
This module MUST NOT:
- create or modify subscriptions
- process payments
- charge cards/accounts
- issue refunds
- alter invoices
- modify entitlement state
- calculate subscription truth
- calculate financial balances
- override subscription/entitlement services
- generate market intelligence
- generate decisions
- modify D13
- generate or override Risk
- generate or bypass CAS
- execute trading orders
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================================
# MODULE IDENTITY
# ============================================================================

BILLING_PAGE_ENGINE = "ROBOMLM_PLUS_UI_BILLING"
BILLING_PAGE_VERSION = "1.0"
BILLING_PAGE_NAME = "Billing"
BILLING_PAGE_TITLE = "Billing & Subscription"
BILLING_PAGE_DESCRIPTION = (
    "ROBOMLM billing, subscription and entitlement presentation workspace."
)

BILLING_ROUTE = "/account/billing"


# ============================================================================
# AUTHORITY CONTRACT
# ============================================================================

BILLING_UI_AUTHORITY: Dict[str, bool] = {
    # Presentation authority
    "billing_presentation": True,
    "subscription_presentation": True,
    "entitlement_presentation": True,
    "invoice_presentation": True,
    "payment_method_presentation": True,
    "billing_navigation": True,
    "billing_summary": True,
    "display_configuration": True,

    # Forbidden authority
    "billing_authority": False,
    "payment_authority": False,
    "transaction_authority": False,
    "subscription_authority": False,
    "entitlement_authority": False,
    "invoice_mutation": False,
    "refund_authority": False,
    "credential_authority": False,

    "market_data_authority": False,
    "evidence_authority": False,
    "market_context_authority": False,
    "intelligence_authority": False,
    "decision_authority": False,
    "d13_authority": False,
    "risk_authority": False,
    "cas_authority": False,
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,

    "upstream_mutation": False,
}


# ============================================================================
# ENUMERATIONS
# ============================================================================

class BillingPageStatus(str, Enum):
    LOADING = "LOADING"
    READY = "READY"
    DEGRADED = "DEGRADED"
    LOCKED = "LOCKED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class BillingPresentationMode(str, Enum):
    OVERVIEW = "OVERVIEW"
    PLAN = "PLAN"
    INVOICES = "INVOICES"
    PAYMENT_METHOD = "PAYMENT_METHOD"
    ENTITLEMENTS = "ENTITLEMENTS"
    UNKNOWN = "UNKNOWN"


class BillingAccountState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    GRACE_PERIOD = "GRACE_PERIOD"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"
    INACTIVE = "INACTIVE"


class SubscriptionState(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACTIVE = "ACTIVE"
    TRIAL = "TRIAL"
    PAST_DUE = "PAST_DUE"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class InvoiceState(str, Enum):
    UNKNOWN = "UNKNOWN"
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAID = "PAID"
    VOID = "VOID"
    UNCOLLECTIBLE = "UNCOLLECTIBLE"


class PaymentMethodType(str, Enum):
    UNKNOWN = "UNKNOWN"
    CARD = "CARD"
    BANK = "BANK"
    UPI = "UPI"
    WALLET = "WALLET"
    OTHER = "OTHER"


class BillingPriority(str, Enum):
    NORMAL = "NORMAL"
    IMPORTANT = "IMPORTANT"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BillingBadgeType(str, Enum):
    BILLING_STATUS = "BILLING_STATUS"
    PLAN = "PLAN"
    SUBSCRIPTION = "SUBSCRIPTION"
    PAYMENT = "PAYMENT"
    ENTITLEMENT = "ENTITLEMENT"
    SYSTEM = "SYSTEM"


# ============================================================================
# SAFE NORMALIZATION HELPERS
# ============================================================================

def _billing_text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    try:
        text = str(value).strip()
    except Exception:
        return default

    return text if text else default


def _billing_bool(
    value: Any,
    default: bool = False,
) -> bool:
    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.strip().lower()

        if value in {"true", "1", "yes", "y", "on"}:
            return True

        if value in {"false", "0", "no", "n", "off"}:
            return False

    return default


def _billing_enum(
    enum_cls: Any,
    value: Any,
    default: Any,
) -> Any:
    if isinstance(value, enum_cls):
        return value

    try:
        return enum_cls(value)
    except Exception:
        return default


def _billing_now() -> datetime:
    return datetime.now(timezone.utc)


# ============================================================================
# PRESENTATION CONTRACTS
# ============================================================================

@dataclass(frozen=True)
class BillingIdentityView:
    """Presentation-safe account identity."""

    user_id: str = ""
    display_name: str = ""
    email: str = ""
    verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingPlanView:
    """Plan information supplied by upstream subscription services."""

    plan_id: str = ""
    plan_name: str = ""
    plan_label: str = ""
    billing_interval: str = ""
    price_display: str = ""
    currency: str = ""
    plus_visible: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingSubscriptionView:
    """Subscription state supplied by the subscription service."""

    subscription_id: str = ""
    state: SubscriptionState = SubscriptionState.UNKNOWN
    state_label: str = ""
    start_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    cancellation_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingStatusView:
    """Billing account status supplied upstream."""

    state: BillingAccountState = BillingAccountState.UNKNOWN
    label: str = ""
    description: str = ""
    active: bool = False
    restricted: bool = False
    priority: BillingPriority = BillingPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingPaymentMethodView:
    """Masked payment-method presentation only."""

    method_type: PaymentMethodType = PaymentMethodType.UNKNOWN
    label: str = ""
    brand: str = ""
    masked_identifier: str = ""
    expiry_display: str = ""
    default_method: bool = False
    available: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingInvoiceView:
    """Invoice presentation received from billing service."""

    invoice_id: str = ""
    invoice_number: str = ""
    state: InvoiceState = InvoiceState.UNKNOWN
    state_label: str = ""
    issue_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    amount_display: str = ""
    currency: str = ""
    document_available: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingEntitlementView:
    """Presentation of entitlement information; no entitlement authority."""

    entitlement_id: str = ""
    name: str = ""
    label: str = ""
    enabled: bool = False
    status_label: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingBadge:
    """Small presentation badge."""

    badge_type: BillingBadgeType
    label: str
    value: str
    priority: BillingPriority = BillingPriority.NORMAL
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingAction:
    """
    Billing UI action.

    Action execution is delegated outside this presentation module.
    """

    action_id: str
    label: str
    route: str
    enabled: bool = True
    visible: bool = True
    requires_authentication: bool = True
    requires_plus: bool = False
    priority: BillingPriority = BillingPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# PAGE REQUEST / VIEW CONTRACT
# ============================================================================

@dataclass(frozen=True)
class BillingPageRequest:
    user_id: str = ""
    mode: BillingPresentationMode = BillingPresentationMode.OVERVIEW
    authenticated: bool = False
    plus_enabled: bool = False
    page_status: BillingPageStatus = BillingPageStatus.LOADING
    source: str = "upstream"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingPageView:
    page_name: str
    page_title: str
    route: str
    status: BillingPageStatus
    mode: BillingPresentationMode

    identity: BillingIdentityView
    plan: BillingPlanView
    subscription: BillingSubscriptionView
    billing_status: BillingStatusView
    payment_method: BillingPaymentMethodView
    invoices: List[BillingInvoiceView]
    entitlements: List[BillingEntitlementView]

    badges: List[BillingBadge]
    actions: List[BillingAction]

    authenticated: bool
    plus_enabled: bool

    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT BILLING ACTIONS
# ============================================================================

DEFAULT_BILLING_ACTIONS: tuple[BillingAction, ...] = (
    BillingAction(
        action_id="billing_overview",
        label="Billing Overview",
        route="/account/billing",
        priority=BillingPriority.NORMAL,
    ),
    BillingAction(
        action_id="billing_plan",
        label="Plan",
        route="/account/billing/plan",
        priority=BillingPriority.NORMAL,
    ),
    BillingAction(
        action_id="billing_invoices",
        label="Invoices",
        route="/account/billing/invoices",
        priority=BillingPriority.NORMAL,
    ),
    BillingAction(
        action_id="billing_payment_method",
        label="Payment Method",
        route="/account/billing/payment-method",
        priority=BillingPriority.IMPORTANT,
    ),
    BillingAction(
        action_id="billing_entitlements",
        label="Entitlements",
        route="/account/billing/entitlements",
        priority=BillingPriority.NORMAL,
    ),
)


# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_billing_identity(
    value: Optional[BillingIdentityView | Dict[str, Any]],
) -> BillingIdentityView:
    if isinstance(value, BillingIdentityView):
        return value

    data = value if isinstance(value, dict) else {}

    return BillingIdentityView(
        user_id=_billing_text(data.get("user_id")),
        display_name=_billing_text(data.get("display_name")),
        email=_billing_text(data.get("email")),
        verified=_billing_bool(data.get("verified")),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_billing_plan(
    value: Optional[BillingPlanView | Dict[str, Any]],
) -> BillingPlanView:
    if isinstance(value, BillingPlanView):
        return value

    data = value if isinstance(value, dict) else {}

    return BillingPlanView(
        plan_id=_billing_text(data.get("plan_id")),
        plan_name=_billing_text(data.get("plan_name")),
        plan_label=_billing_text(data.get("plan_label")),
        billing_interval=_billing_text(data.get("billing_interval")),
        price_display=_billing_text(data.get("price_display")),
        currency=_billing_text(data.get("currency")),
        plus_visible=_billing_bool(data.get("plus_visible")),
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_billing_subscription(
    value: Optional[BillingSubscriptionView | Dict[str, Any]],
) -> BillingSubscriptionView:
    if isinstance(value, BillingSubscriptionView):
        return value

    data = value if isinstance(value, dict) else {}

    auto_renew = data.get("auto_renew")

    if auto_renew is not None:
        auto_renew = _billing_bool(auto_renew)

    return BillingSubscriptionView(
        subscription_id=_billing_text(data.get("subscription_id")),
        state=_billing_enum(
            SubscriptionState,
            data.get("state"),
            SubscriptionState.UNKNOWN,
        ),
        state_label=_billing_text(data.get("state_label")),
        start_date=data.get("start_date"),
        renewal_date=data.get("renewal_date"),
        cancellation_date=data.get("cancellation_date"),
        auto_renew=auto_renew,
        metadata=dict(data.get("metadata") or {}),
    )


def normalize_billing_status(
    value: Optional[BillingStatusView | Dict[str, Any]],
) -> BillingStatusView:
    if isinstance(value, BillingStatusView):
        return value

    data = value if isinstance(value, dict) else {}

    return BillingStatusView(
        state=_billing_enum(
            BillingAccountState,
            data.get("state"),
            BillingAccountState.UNKNOWN,
        ),
        label=_billing_text(data.get("label")),
        description=_billing_text(data.get("description")),
        active=_billing_bool(data.get("active")),
        restricted=_billing_bool(data.get("restricted")),
        priority=_billing_enum(
            BillingPriority,
            data.get("priority"),
            BillingPriority.NORMAL,
        ),
        metadata=dict(data.get("metadata") or {}),
    )


# ============================================================================
# INITIAL BADGE BUILDERS
# ============================================================================

def build_billing_status_badge(
    status: BillingStatusView,
) -> BillingBadge:
    status = normalize_billing_status(status)

    label = status.label or status.state.value.replace("_", " ").title()

    return BillingBadge(
        badge_type=BillingBadgeType.BILLING_STATUS,
        label="Billing",
        value=label,
        priority=status.priority,
        visible=True,
    )


def build_billing_plan_badge(
    plan: BillingPlanView,
) -> BillingBadge:
    plan = normalize_billing_plan(plan)

    label = plan.plan_label or plan.plan_name or "Plan unavailable"

    return BillingBadge(
        badge_type=BillingBadgeType.PLAN,
        label="Plan",
        value=label,
        priority=BillingPriority.NORMAL,
        visible=True,
    )


def build_subscription_badge(
    subscription: BillingSubscriptionView,
) -> BillingBadge:
    subscription = normalize_billing_subscription(subscription)

    label = (
        subscription.state_label
        or subscription.state.value.replace("_", " ").title()
    )

    priority = BillingPriority.NORMAL

    if subscription.state in {
        SubscriptionState.PAST_DUE,
        SubscriptionState.EXPIRED,
    }:
        priority = BillingPriority.HIGH

    if subscription.state == SubscriptionState.CANCELLED:
        priority = BillingPriority.IMPORTANT

    return BillingBadge(
        badge_type=BillingBadgeType.SUBSCRIPTION,
        label="Subscription",
        value=label,
        priority=priority,
        visible=True,
    )


def build_billing_badges(
    plan: BillingPlanView,
    subscription: BillingSubscriptionView,
    status: BillingStatusView,
) -> List[BillingBadge]:
    return [
        build_billing_status_badge(status),
        build_billing_plan_badge(plan),
        build_subscription_badge(subscription),
    ]


# ============================================================================
# ACTIONS
# ============================================================================

def get_billing_actions(
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> List[BillingAction]:
    """
    Return presentation actions.

    This function DOES NOT execute any billing operation.
    """

    actions: List[BillingAction] = []

    for action in DEFAULT_BILLING_ACTIONS:
        enabled = action.enabled

        if action.requires_authentication and not authenticated:
            enabled = False

        if action.requires_plus and not plus_enabled:
            enabled = False

        actions.append(
            BillingAction(
                action_id=action.action_id,
                label=action.label,
                route=action.route,
                enabled=enabled,
                visible=action.visible,
                requires_authentication=action.requires_authentication,
                requires_plus=action.requires_plus,
                priority=action.priority,
                metadata=dict(action.metadata),
            )
        )

    return actions


# ============================================================================
# PAGE VIEW BUILDER
# ============================================================================

def build_billing_page_view(
    request: BillingPageRequest,
    *,
    identity: Optional[BillingIdentityView | Dict[str, Any]] = None,
    plan: Optional[BillingPlanView | Dict[str, Any]] = None,
    subscription: Optional[
        BillingSubscriptionView | Dict[str, Any]
    ] = None,
    billing_status: Optional[
        BillingStatusView | Dict[str, Any]
    ] = None,
    payment_method: Optional[
        BillingPaymentMethodView
    ] = None,
    invoices: Optional[List[BillingInvoiceView]] = None,
    entitlements: Optional[List[BillingEntitlementView]] = None,
) -> BillingPageView:
    """
    Compose the billing presentation from upstream truth.

    No billing truth is invented here.
    """

    identity_view = normalize_billing_identity(identity)
    plan_view = normalize_billing_plan(plan)
    subscription_view = normalize_billing_subscription(subscription)
    status_view = normalize_billing_status(billing_status)

    payment_view = (
        payment_method
        if isinstance(payment_method, BillingPaymentMethodView)
        else BillingPaymentMethodView()
    )

    invoice_views = list(invoices or [])
    entitlement_views = list(entitlements or [])

    badges = build_billing_badges(
        plan_view,
        subscription_view,
        status_view,
    )

    actions = get_billing_actions(
        authenticated=request.authenticated,
        plus_enabled=request.plus_enabled,
    )

    metadata = dict(request.metadata)

    metadata.update(
        {
            "ui_only": True,
            "billing_truth_source": request.source,
            "billing_authority": False,
            "payment_authority": False,
            "subscription_authority": False,
            "entitlement_authority": False,
            "invoice_mutation": False,
            "refund_authority": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        }
    )

    return BillingPageView(
        page_name=BILLING_PAGE_NAME,
        page_title=BILLING_PAGE_TITLE,
        route=BILLING_ROUTE,
        status=request.page_status,
        mode=request.mode,
        identity=identity_view,
        plan=plan_view,
        subscription=subscription_view,
        billing_status=status_view,
        payment_method=payment_view,
        invoices=invoice_views,
        entitlements=entitlement_views,
        badges=badges,
        actions=actions,
        authenticated=request.authenticated,
        plus_enabled=request.plus_enabled,
        generated_at=_billing_now(),
        metadata=metadata,
    )


__all__ = [
    # Identity
    "BILLING_PAGE_ENGINE",
    "BILLING_PAGE_VERSION",
    "BILLING_PAGE_NAME",
    "BILLING_PAGE_TITLE",
    "BILLING_PAGE_DESCRIPTION",
    "BILLING_ROUTE",
    "BILLING_UI_AUTHORITY",

    # Enums
    "BillingPageStatus",
    "BillingPresentationMode",
    "BillingAccountState",
    "SubscriptionState",
    "InvoiceState",
    "PaymentMethodType",
    "BillingPriority",
    "BillingBadgeType",

    # Contracts
    "BillingIdentityView",
    "BillingPlanView",
    "BillingSubscriptionView",
    "BillingStatusView",
    "BillingPaymentMethodView",
    "BillingInvoiceView",
    "BillingEntitlementView",
    "BillingBadge",
    "BillingAction",
    "BillingPageRequest",
    "BillingPageView",

    # Defaults
    "DEFAULT_BILLING_ACTIONS",

    # Normalization
    "normalize_billing_identity",
    "normalize_billing_plan",
    "normalize_billing_subscription",
    "normalize_billing_status",

    # Presentation
    "build_billing_status_badge",
    "build_billing_plan_badge",
    "build_subscription_badge",
    "build_billing_badges",
    "get_billing_actions",
    "build_billing_page_view",
]
# ============================================================================
# BILLING SOURCE STATE
# ============================================================================

@dataclass(frozen=True)
class BillingSourceState:
    """
    Upstream billing/subscription presentation state.

    This contract carries truth into the UI layer.
    It does not create or mutate that truth.
    """

    identity: BillingIdentityView = field(
        default_factory=BillingIdentityView
    )

    plan: BillingPlanView = field(
        default_factory=BillingPlanView
    )

    subscription: BillingSubscriptionView = field(
        default_factory=BillingSubscriptionView
    )

    billing_status: BillingStatusView = field(
        default_factory=BillingStatusView
    )

    payment_method: BillingPaymentMethodView = field(
        default_factory=BillingPaymentMethodView
    )

    invoices: List[BillingInvoiceView] = field(
        default_factory=list
    )

    entitlements: List[BillingEntitlementView] = field(
        default_factory=list
    )

    source_available: bool = True
    source_errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BillingSectionState:
    """
    Presentation state for one billing workspace section.
    """

    section_id: str
    title: str
    description: str
    route: str

    visible: bool = True
    enabled: bool = True

    status: BillingPageStatus = BillingPageStatus.READY
    priority: BillingPriority = BillingPriority.NORMAL

    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# DEFAULT BILLING SECTIONS
# ============================================================================

DEFAULT_BILLING_SECTIONS: tuple[BillingSectionState, ...] = (
    BillingSectionState(
        section_id="billing_overview",
        title="Billing Overview",
        description="Current billing and subscription status.",
        route="/account/billing",
    ),
    BillingSectionState(
        section_id="billing_plan",
        title="Plan",
        description="Current subscription plan information.",
        route="/account/billing/plan",
    ),
    BillingSectionState(
        section_id="billing_invoices",
        title="Invoices",
        description="Available invoice history.",
        route="/account/billing/invoices",
    ),
    BillingSectionState(
        section_id="billing_payment_method",
        title="Payment Method",
        description="Masked payment-method information.",
        route="/account/billing/payment-method",
        priority=BillingPriority.IMPORTANT,
    ),
    BillingSectionState(
        section_id="billing_entitlements",
        title="Entitlements",
        description="Current entitlement presentation.",
        route="/account/billing/entitlements",
    ),
)


# ============================================================================
# SOURCE NORMALIZATION
# ============================================================================

def normalize_billing_source_state(
    value: Optional[
        BillingSourceState | Dict[str, Any]
    ],
) -> BillingSourceState:
    """
    Normalize upstream billing information.

    No missing commercial truth is invented.
    """

    if isinstance(value, BillingSourceState):
        return value

    data = value if isinstance(value, dict) else {}

    payment_method = data.get("payment_method")

    if not isinstance(payment_method, BillingPaymentMethodView):
        payment_method = BillingPaymentMethodView()

    invoices = data.get("invoices") or []
    entitlements = data.get("entitlements") or []

    normalized_invoices = [
        item for item in invoices
        if isinstance(item, BillingInvoiceView)
    ]

    normalized_entitlements = [
        item for item in entitlements
        if isinstance(item, BillingEntitlementView)
    ]

    source_errors = [
        _billing_text(error)
        for error in (data.get("source_errors") or [])
        if _billing_text(error)
    ]

    return BillingSourceState(
        identity=normalize_billing_identity(
            data.get("identity")
        ),
        plan=normalize_billing_plan(
            data.get("plan")
        ),
        subscription=normalize_billing_subscription(
            data.get("subscription")
        ),
        billing_status=normalize_billing_status(
            data.get("billing_status")
        ),
        payment_method=payment_method,
        invoices=normalized_invoices,
        entitlements=normalized_entitlements,
        source_available=_billing_bool(
            data.get("source_available"),
            default=False,
        ),
        source_errors=source_errors,
        metadata=dict(data.get("metadata") or {}),
    )


# ============================================================================
# PRESENTATION READINESS
# ============================================================================

def evaluate_billing_presentation_status(
    source: BillingSourceState,
    *,
    authenticated: bool,
) -> BillingPageStatus:
    """
    Determine UI presentation readiness.

    This is NOT billing-status calculation.
    It only determines whether the UI can safely present
    the upstream billing information.
    """

    source = normalize_billing_source_state(source)

    if not authenticated:
        return BillingPageStatus.LOCKED

    if not source.source_available:
        return BillingPageStatus.DEGRADED

    if source.source_errors:
        return BillingPageStatus.DEGRADED

    if source.billing_status.state in {
        BillingAccountState.SUSPENDED,
        BillingAccountState.INACTIVE,
    }:
        return BillingPageStatus.LOCKED

    if source.billing_status.state == BillingAccountState.UNKNOWN:
        return BillingPageStatus.DEGRADED

    return BillingPageStatus.READY


# ============================================================================
# SECTION COMPOSITION
# ============================================================================

def build_billing_sections(
    *,
    authenticated: bool,
    source_status: BillingPageStatus,
) -> List[BillingSectionState]:
    """
    Build presentation sections.

    Section availability does not grant billing authority.
    """

    sections: List[BillingSectionState] = []

    for section in DEFAULT_BILLING_SECTIONS:
        visible = True
        enabled = True
        status = source_status

        if not authenticated:
            visible = section.section_id == "billing_overview"
            enabled = False
            status = BillingPageStatus.LOCKED

        elif source_status == BillingPageStatus.LOCKED:
            enabled = section.section_id == "billing_overview"

        sections.append(
            BillingSectionState(
                section_id=section.section_id,
                title=section.title,
                description=section.description,
                route=section.route,
                visible=visible,
                enabled=enabled,
                status=status,
                priority=section.priority,
                metadata=dict(section.metadata),
            )
        )

    return sections


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

def resolve_billing_display_name(
    identity: BillingIdentityView,
) -> str:
    identity = normalize_billing_identity(identity)

    return (
        identity.display_name
        or identity.email
        or "Account"
    )


def build_billing_status_message(
    status: BillingStatusView,
) -> str:
    """
    Return upstream status description without generating new billing truth.
    """

    status = normalize_billing_status(status)

    if status.description:
        return status.description

    if status.label:
        return status.label

    if status.state == BillingAccountState.UNKNOWN:
        return "Billing status is currently unavailable."

    return status.state.value.replace("_", " ").title()


def build_subscription_display_message(
    subscription: BillingSubscriptionView,
) -> str:
    subscription = normalize_billing_subscription(subscription)

    if subscription.state_label:
        return subscription.state_label

    if subscription.state == SubscriptionState.UNKNOWN:
        return "Subscription status unavailable."

    return subscription.state.value.replace(
        "_",
        " ",
    ).title()


# ============================================================================
# BILLING SUMMARY
# ============================================================================

@dataclass(frozen=True)
class BillingSummaryView:
    display_name: str
    email: str

    billing_status_label: str
    billing_status_message: str

    plan_label: str
    subscription_label: str

    renewal_date: Optional[datetime]
    auto_renew: Optional[bool]

    invoice_count: int
    entitlement_count: int

    payment_method_available: bool

    authenticated: bool
    plus_enabled: bool

    priority: BillingPriority = BillingPriority.NORMAL

    metadata: Dict[str, Any] = field(default_factory=dict)


def build_billing_summary(
    source: BillingSourceState,
    *,
    authenticated: bool,
    plus_enabled: bool,
) -> BillingSummaryView:
    """
    Compose a presentation summary from upstream billing state.
    """

    source = normalize_billing_source_state(source)

    status = source.billing_status
    plan = source.plan
    subscription = source.subscription

    priority = status.priority

    if subscription.state in {
        SubscriptionState.PAST_DUE,
        SubscriptionState.EXPIRED,
    }:
        priority = BillingPriority.HIGH

    return BillingSummaryView(
        display_name=resolve_billing_display_name(
            source.identity
        ),
        email=source.identity.email,

        billing_status_label=(
            status.label
            or status.state.value.replace("_", " ").title()
        ),

        billing_status_message=build_billing_status_message(
            status
        ),

        plan_label=(
            plan.plan_label
            or plan.plan_name
            or "Plan unavailable"
        ),

        subscription_label=build_subscription_display_message(
            subscription
        ),

        renewal_date=subscription.renewal_date,
        auto_renew=subscription.auto_renew,

        invoice_count=len(source.invoices),
        entitlement_count=len(source.entitlements),

        payment_method_available=(
            source.payment_method.available
        ),

        authenticated=authenticated,
        plus_enabled=plus_enabled,

        priority=priority,

        metadata={
            "ui_only": True,
            "source_available": source.source_available,
            "source_error_count": len(source.source_errors),
            "billing_authority": False,
            "subscription_authority": False,
            "entitlement_authority": False,
            "payment_authority": False,
        },
    )


# ============================================================================
# PAGE COMPOSITION
# ============================================================================

@dataclass(frozen=True)
class BillingPageComposition:
    """
    Complete presentation composition for Billing workspace.
    """

    page: BillingPageView
    summary: BillingSummaryView
    sections: List[BillingSectionState]

    status_message: str
    errors: List[str]

    generated_at: datetime

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def compose_billing_page(
    request: BillingPageRequest,
    source: Optional[BillingSourceState | Dict[str, Any]] = None,
) -> BillingPageComposition:
    """
    Main Billing UI composition pipeline.

    Flow:
        Upstream Billing Truth
            ↓
        Source Normalization
            ↓
        Presentation Readiness
            ↓
        Summary Composition
            ↓
        Section Composition
            ↓
        Page View
            ↓
        Final UI Composition

    No billing mutation occurs.
    """

    normalized_source = normalize_billing_source_state(
        source
    )

    status = evaluate_billing_presentation_status(
        normalized_source,
        authenticated=request.authenticated,
    )

    effective_request = BillingPageRequest(
        user_id=request.user_id,
        mode=request.mode,
        authenticated=request.authenticated,
        plus_enabled=request.plus_enabled,
        page_status=status,
        source=request.source,
        metadata=dict(request.metadata),
    )

    summary = build_billing_summary(
        normalized_source,
        authenticated=request.authenticated,
        plus_enabled=request.plus_enabled,
    )

    sections = build_billing_sections(
        authenticated=request.authenticated,
        source_status=status,
    )

    page = build_billing_page_view(
        effective_request,
        identity=normalized_source.identity,
        plan=normalized_source.plan,
        subscription=normalized_source.subscription,
        billing_status=normalized_source.billing_status,
        payment_method=normalized_source.payment_method,
        invoices=normalized_source.invoices,
        entitlements=normalized_source.entitlements,
    )

    status_message = build_billing_status_message(
        normalized_source.billing_status
    )

    errors = list(normalized_source.source_errors)

    metadata = {
        "ui_only": True,
        "composition_layer": "PRESENTATION",
        "source": request.source,
        "billing_authority": False,
        "payment_authority": False,
        "subscription_authority": False,
        "entitlement_authority": False,
        "invoice_mutation": False,
        "refund_authority": False,
        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
    }

    return BillingPageComposition(
        page=page,
        summary=summary,
        sections=sections,
        status_message=status_message,
        errors=errors,
        generated_at=_billing_now(),
        metadata=metadata,
    )
# ============================================================================
# BILLING INTERACTIONS
# ============================================================================

class BillingInteraction(str, Enum):
    OPEN_OVERVIEW = "OPEN_OVERVIEW"
    OPEN_PLAN = "OPEN_PLAN"
    OPEN_INVOICES = "OPEN_INVOICES"
    OPEN_PAYMENT_METHOD = "OPEN_PAYMENT_METHOD"
    OPEN_ENTITLEMENTS = "OPEN_ENTITLEMENTS"
    REFRESH = "REFRESH"
    LOCK = "LOCK"
    NONE = "NONE"


BILLING_INTERACTION_ROUTES: Dict[BillingInteraction, str] = {
    BillingInteraction.OPEN_OVERVIEW: "/account/billing",
    BillingInteraction.OPEN_PLAN: "/account/billing/plan",
    BillingInteraction.OPEN_INVOICES: "/account/billing/invoices",
    BillingInteraction.OPEN_PAYMENT_METHOD: (
        "/account/billing/payment-method"
    ),
    BillingInteraction.OPEN_ENTITLEMENTS: (
        "/account/billing/entitlements"
    ),
}


def normalize_billing_interaction(
    value: Any,
) -> BillingInteraction:
    if isinstance(value, BillingInteraction):
        return value

    try:
        return BillingInteraction(value)
    except Exception:
        return BillingInteraction.NONE


# ============================================================================
# BILLING PAGE STATE
# ============================================================================

@dataclass
class BillingPageState:
    """
    Mutable presentation state owned by the Billing UI controller.

    This state does not represent authoritative billing/subscription truth.
    """

    user_id: str = ""

    authenticated: bool = False
    plus_enabled: bool = False

    mode: BillingPresentationMode = (
        BillingPresentationMode.OVERVIEW
    )

    status: BillingPageStatus = (
        BillingPageStatus.LOADING
    )

    current_route: str = BILLING_ROUTE

    initialized: bool = False
    ready: bool = False
    locked: bool = False

    interaction_count: int = 0
    refresh_count: int = 0

    last_interaction: BillingInteraction = (
        BillingInteraction.NONE
    )

    last_error: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def create_billing_page_state(
    *,
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> BillingPageState:
    return BillingPageState(
        user_id=_billing_text(user_id),
        authenticated=_billing_bool(authenticated),
        plus_enabled=_billing_bool(plus_enabled),
        mode=BillingPresentationMode.OVERVIEW,
        status=BillingPageStatus.LOADING,
        current_route=BILLING_ROUTE,
        initialized=False,
        ready=False,
        locked=False,
    )


def normalize_billing_page_state(
    value: Optional[
        BillingPageState | Dict[str, Any]
    ],
) -> BillingPageState:
    if isinstance(value, BillingPageState):
        return value

    data = value if isinstance(value, dict) else {}

    return BillingPageState(
        user_id=_billing_text(data.get("user_id")),

        authenticated=_billing_bool(
            data.get("authenticated")
        ),

        plus_enabled=_billing_bool(
            data.get("plus_enabled")
        ),

        mode=_billing_enum(
            BillingPresentationMode,
            data.get("mode"),
            BillingPresentationMode.OVERVIEW,
        ),

        status=_billing_enum(
            BillingPageStatus,
            data.get("status"),
            BillingPageStatus.UNKNOWN,
        ),

        current_route=(
            _billing_text(
                data.get("current_route"),
                BILLING_ROUTE,
            )
            or BILLING_ROUTE
        ),

        initialized=_billing_bool(
            data.get("initialized")
        ),

        ready=_billing_bool(
            data.get("ready")
        ),

        locked=_billing_bool(
            data.get("locked")
        ),

        interaction_count=max(
            0,
            int(data.get("interaction_count") or 0),
        ),

        refresh_count=max(
            0,
            int(data.get("refresh_count") or 0),
        ),

        last_interaction=normalize_billing_interaction(
            data.get("last_interaction")
        ),

        last_error=_billing_text(
            data.get("last_error")
        ),

        metadata=dict(
            data.get("metadata") or {}
        ),
    )


# ============================================================================
# ROUTE → MODE
# ============================================================================

def route_to_billing_mode(
    route: str,
) -> BillingPresentationMode:
    route = _billing_text(route).rstrip("/") or BILLING_ROUTE

    mapping = {
        "/account/billing": BillingPresentationMode.OVERVIEW,
        "/account/billing/plan": BillingPresentationMode.PLAN,
        "/account/billing/invoices": (
            BillingPresentationMode.INVOICES
        ),
        "/account/billing/payment-method": (
            BillingPresentationMode.PAYMENT_METHOD
        ),
        "/account/billing/entitlements": (
            BillingPresentationMode.ENTITLEMENTS
        ),
    }

    return mapping.get(
        route,
        BillingPresentationMode.UNKNOWN,
    )


# ============================================================================
# ROUTE ACCESS
# ============================================================================

def evaluate_billing_route_access(
    route: str,
    *,
    authenticated: bool,
    locked: bool = False,
) -> tuple[bool, str]:
    """
    Presentation-level route access only.

    This does not perform authentication or entitlement checks.
    """

    route = _billing_text(route).rstrip("/") or BILLING_ROUTE

    known_routes = {
        "/account/billing",
        "/account/billing/plan",
        "/account/billing/invoices",
        "/account/billing/payment-method",
        "/account/billing/entitlements",
    }

    if route not in known_routes:
        return False, "UNKNOWN_BILLING_ROUTE"

    if not authenticated:
        return False, "REQUIRES_AUTHENTICATION"

    if locked:
        return False, "BILLING_PAGE_LOCKED"

    return True, "ALLOWED"


# ============================================================================
# INTERACTION RESULT
# ============================================================================

@dataclass(frozen=True)
class BillingInteractionResult:
    interaction: BillingInteraction

    requested_route: str
    resolved_route: str

    allowed: bool
    reason: str

    mode: BillingPresentationMode

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def resolve_billing_interaction(
    interaction: BillingInteraction | str,
    *,
    authenticated: bool,
    locked: bool = False,
) -> BillingInteractionResult:
    interaction = normalize_billing_interaction(
        interaction
    )

    requested_route = BILLING_ROUTE

    if interaction in BILLING_INTERACTION_ROUTES:
        requested_route = BILLING_INTERACTION_ROUTES[
            interaction
        ]

    elif interaction == BillingInteraction.LOCK:
        return BillingInteractionResult(
            interaction=interaction,
            requested_route=BILLING_ROUTE,
            resolved_route=BILLING_ROUTE,
            allowed=True,
            reason="UI_LOCK_REQUEST_ACCEPTED",
            mode=BillingPresentationMode.OVERVIEW,
            metadata={
                "ui_only": True,
                "billing_mutation": False,
            },
        )

    elif interaction == BillingInteraction.REFRESH:
        return BillingInteractionResult(
            interaction=interaction,
            requested_route=BILLING_ROUTE,
            resolved_route=BILLING_ROUTE,
            allowed=authenticated and not locked,
            reason=(
                "ALLOWED"
                if authenticated and not locked
                else "REFRESH_NOT_AVAILABLE"
            ),
            mode=BillingPresentationMode.OVERVIEW,
            metadata={
                "ui_only": True,
                "refresh_delegates_to_upstream": True,
            },
        )

    elif interaction == BillingInteraction.NONE:
        return BillingInteractionResult(
            interaction=interaction,
            requested_route=BILLING_ROUTE,
            resolved_route=BILLING_ROUTE,
            allowed=False,
            reason="NO_INTERACTION",
            mode=BillingPresentationMode.OVERVIEW,
            metadata={"ui_only": True},
        )

    allowed, reason = evaluate_billing_route_access(
        requested_route,
        authenticated=authenticated,
        locked=locked,
    )

    resolved_route = (
        requested_route
        if allowed
        else BILLING_ROUTE
    )

    return BillingInteractionResult(
        interaction=interaction,
        requested_route=requested_route,
        resolved_route=resolved_route,
        allowed=allowed,
        reason=reason,
        mode=route_to_billing_mode(resolved_route),
        metadata={
            "ui_only": True,
            "billing_authority": False,
            "subscription_authority": False,
            "payment_authority": False,
            "entitlement_authority": False,
        },
    )


# ============================================================================
# BILLING PAGE CONTROLLER
# ============================================================================

class BillingPageController:
    """
    Presentation controller for Billing workspace.

    The controller does not mutate billing-domain state.
    """

    def __init__(
        self,
        state: Optional[BillingPageState] = None,
    ) -> None:
        self._state = normalize_billing_page_state(
            state
            or create_billing_page_state()
        )

        self._interaction_history: List[
            BillingInteractionResult
        ] = []

        self._last_composition: Optional[
            BillingPageComposition
        ] = None

    @property
    def state(self) -> BillingPageState:
        return self._state

    @property
    def current_route(self) -> str:
        return self._state.current_route

    @property
    def current_mode(
        self,
    ) -> BillingPresentationMode:
        return self._state.mode

    @property
    def status(self) -> BillingPageStatus:
        return self._state.status

    # ------------------------------------------------------------------------
    # INITIALIZE
    # ------------------------------------------------------------------------

    def initialize(
        self,
        source: Optional[BillingSourceState | Dict[str, Any]] = None,
    ) -> BillingPageComposition:
        normalized_source = normalize_billing_source_state(
            source
        )

        self._state.initialized = True
        self._state.locked = not self._state.authenticated

        composition = compose_billing_page(
            BillingPageRequest(
                user_id=self._state.user_id,
                mode=self._state.mode,
                authenticated=self._state.authenticated,
                plus_enabled=self._state.plus_enabled,
                page_status=BillingPageStatus.LOADING,
                source="upstream",
            ),
            normalized_source,
        )

        self._state.status = composition.page.status
        self._state.ready = (
            composition.page.status
            == BillingPageStatus.READY
        )

        self._state.last_error = (
            composition.errors[0]
            if composition.errors
            else ""
        )

        self._last_composition = composition

        return composition

    # ------------------------------------------------------------------------
    # INTERACTION
    # ------------------------------------------------------------------------

    def interact(
        self,
        interaction: BillingInteraction | str,
    ) -> BillingInteractionResult:
        result = resolve_billing_interaction(
            interaction,
            authenticated=self._state.authenticated,
            locked=self._state.locked,
        )

        self._state.interaction_count += 1
        self._state.last_interaction = result.interaction

        if result.interaction == BillingInteraction.LOCK:
            self.lock()

        elif result.interaction == BillingInteraction.REFRESH:
            self._state.refresh_count += 1

        elif result.allowed:
            self._state.current_route = result.resolved_route
            self._state.mode = result.mode

        self._interaction_history.append(result)

        return result

    # ------------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------------

    def navigate(
        self,
        route: str,
    ) -> BillingInteractionResult:
        route = _billing_text(route)

        mode = route_to_billing_mode(route)

        interaction_map = {
            BillingPresentationMode.OVERVIEW:
                BillingInteraction.OPEN_OVERVIEW,

            BillingPresentationMode.PLAN:
                BillingInteraction.OPEN_PLAN,

            BillingPresentationMode.INVOICES:
                BillingInteraction.OPEN_INVOICES,

            BillingPresentationMode.PAYMENT_METHOD:
                BillingInteraction.OPEN_PAYMENT_METHOD,

            BillingPresentationMode.ENTITLEMENTS:
                BillingInteraction.OPEN_ENTITLEMENTS,
        }

        interaction = interaction_map.get(
            mode,
            BillingInteraction.NONE,
        )

        result = resolve_billing_interaction(
            interaction,
            authenticated=self._state.authenticated,
            locked=self._state.locked,
        )

        if result.allowed:
            self._state.current_route = result.resolved_route
            self._state.mode = result.mode

        self._state.interaction_count += 1
        self._state.last_interaction = interaction

        self._interaction_history.append(result)

        return result

    # ------------------------------------------------------------------------
    # UI LOCK
    # ------------------------------------------------------------------------

    def lock(self) -> None:
        """
        Lock the Billing UI only.

        Does not cancel, suspend, modify or restrict a subscription.
        """

        self._state.locked = True
        self._state.ready = False
        self._state.status = BillingPageStatus.LOCKED

    def unlock(self) -> None:
        """
        Unlock presentation state only.

        Authentication remains externally authoritative.
        """

        if self._state.authenticated:
            self._state.locked = False

            if self._state.initialized:
                self._state.ready = True

                if self._state.status == BillingPageStatus.LOCKED:
                    self._state.status = (
                        BillingPageStatus.READY
                    )

    # ------------------------------------------------------------------------
    # SESSION PRESENTATION STATE
    # ------------------------------------------------------------------------

    def set_authenticated(
        self,
        authenticated: bool,
    ) -> None:
        """
        Update presentation authentication state.

        Actual authentication is external.
        """

        self._state.authenticated = bool(authenticated)

        if not self._state.authenticated:
            self._state.locked = True
            self._state.ready = False
            self._state.status = BillingPageStatus.LOCKED

        elif self._state.initialized:
            self._state.locked = False

    def set_plus_visibility(
        self,
        enabled: bool,
    ) -> None:
        """
        Presentation-only PLUS visibility.

        Does not grant or revoke entitlement.
        """

        self._state.plus_enabled = bool(enabled)

    # ------------------------------------------------------------------------
    # COMPOSITION
    # ------------------------------------------------------------------------

    def compose(
        self,
        source: Optional[
            BillingSourceState | Dict[str, Any]
        ] = None,
    ) -> BillingPageComposition:
        if not self._state.authenticated:
            self._state.locked = True

        composition = compose_billing_page(
            BillingPageRequest(
                user_id=self._state.user_id,
                mode=self._state.mode,
                authenticated=self._state.authenticated,
                plus_enabled=self._state.plus_enabled,
                page_status=self._state.status,
                source="upstream",
            ),
            source,
        )

        self._state.status = composition.page.status
        self._state.ready = (
            composition.page.status
            == BillingPageStatus.READY
            and not self._state.locked
        )

        self._state.last_error = (
            composition.errors[0]
            if composition.errors
            else ""
        )

        self._last_composition = composition

        return composition

    @property
    def last_composition(
        self,
    ) -> Optional[BillingPageComposition]:
        return self._last_composition

    # ------------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------------

    def interaction_history(
        self,
    ) -> List[BillingInteractionResult]:
        return list(self._interaction_history)

    def clear_interaction_history(self) -> None:
        self._interaction_history.clear()


# ============================================================================
# BILLING SNAPSHOT
# ============================================================================

@dataclass(frozen=True)
class BillingPageSnapshot:
    """
    Presentation snapshot.

    This is not an authoritative billing record.
    """

    state: BillingPageState
    composition: BillingPageComposition

    captured_at: datetime

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_billing_page_snapshot(
    controller: BillingPageController,
    source: Optional[
        BillingSourceState | Dict[str, Any]
    ] = None,
) -> BillingPageSnapshot:
    """
    Capture current Billing UI presentation.
    """

    composition = controller.compose(source)

    state = normalize_billing_page_state(
        controller.state
    )

    return BillingPageSnapshot(
        state=state,
        composition=composition,
        captured_at=_billing_now(),
        metadata={
            "ui_only": True,
            "snapshot_type": "BILLING_PRESENTATION",
            "billing_authority": False,
            "payment_authority": False,
            "subscription_authority": False,
            "entitlement_authority": False,
            "invoice_mutation": False,
            "refund_authority": False,
            "intelligence_generation": False,
            "decision_generation": False,
            "d13_modification": False,
            "risk_generation": False,
            "cas_generation": False,
            "execution": False,
        },
    )


# ============================================================================
# PUBLIC EXPORTS — PART 3
# ============================================================================

__all__.extend(
    [
        # Source / sections
        "BillingSourceState",
        "BillingSectionState",
        "DEFAULT_BILLING_SECTIONS",
        "normalize_billing_source_state",
        "evaluate_billing_presentation_status",
        "build_billing_sections",

        # Display helpers
        "resolve_billing_display_name",
        "build_billing_status_message",
        "build_subscription_display_message",

        # Summary / composition
        "BillingSummaryView",
        "build_billing_summary",
        "BillingPageComposition",
        "compose_billing_page",

        # Interactions
        "BillingInteraction",
        "BILLING_INTERACTION_ROUTES",
        "normalize_billing_interaction",
        "route_to_billing_mode",
        "evaluate_billing_route_access",
        "BillingInteractionResult",
        "resolve_billing_interaction",

        # State / controller
        "BillingPageState",
        "create_billing_page_state",
        "normalize_billing_page_state",
        "BillingPageController",

        # Snapshot
        "BillingPageSnapshot",
        "build_billing_page_snapshot",
    ]
)
# ============================================================================
# SERIALIZATION
# ============================================================================

def _serialize_billing_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [
            _serialize_billing_value(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return [
            _serialize_billing_value(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            str(key): _serialize_billing_value(item)
            for key, item in value.items()
        }

    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _serialize_billing_value(
                getattr(value, name)
            )
            for name in value.__dataclass_fields__
        }

    return value


def serialize_billing_identity(
    value: BillingIdentityView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_plan(
    value: BillingPlanView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_subscription(
    value: BillingSubscriptionView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_status(
    value: BillingStatusView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_payment_method(
    value: BillingPaymentMethodView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_invoice(
    value: BillingInvoiceView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_entitlement(
    value: BillingEntitlementView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_badge(
    value: BillingBadge,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_action(
    value: BillingAction,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_page_request(
    value: BillingPageRequest,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_page_view(
    value: BillingPageView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_source_state(
    value: BillingSourceState,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_section(
    value: BillingSectionState,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_summary(
    value: BillingSummaryView,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_composition(
    value: BillingPageComposition,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_page_state(
    value: BillingPageState,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_snapshot(
    value: BillingPageSnapshot,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


def serialize_billing_interaction_result(
    value: BillingInteractionResult,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


# ============================================================================
# VALIDATION — IDENTITY
# ============================================================================

def validate_billing_identity(
    value: BillingIdentityView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingIdentityView):
        return ["INVALID_BILLING_IDENTITY_TYPE"]

    if value.verified and not value.email:
        errors.append(
            "VERIFIED_IDENTITY_WITHOUT_EMAIL"
        )

    return errors


# ============================================================================
# VALIDATION — PLAN
# ============================================================================

def validate_billing_plan(
    value: BillingPlanView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingPlanView):
        return ["INVALID_BILLING_PLAN_TYPE"]

    if value.plus_visible and not value.plan_name:
        errors.append(
            "PLUS_VISIBLE_WITHOUT_PLAN_NAME"
        )

    return errors


# ============================================================================
# VALIDATION — SUBSCRIPTION
# ============================================================================

def validate_billing_subscription(
    value: BillingSubscriptionView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingSubscriptionView):
        return ["INVALID_BILLING_SUBSCRIPTION_TYPE"]

    if (
        value.state == SubscriptionState.ACTIVE
        and not value.subscription_id
    ):
        errors.append(
            "ACTIVE_SUBSCRIPTION_WITHOUT_ID"
        )

    if (
        value.cancellation_date is not None
        and value.state != SubscriptionState.CANCELLED
    ):
        errors.append(
            "CANCELLATION_DATE_STATE_MISMATCH"
        )

    if (
        value.auto_renew is True
        and value.state in {
            SubscriptionState.CANCELLED,
            SubscriptionState.EXPIRED,
        }
    ):
        errors.append(
            "AUTO_RENEW_CONFLICTS_WITH_TERMINAL_STATE"
        )

    return errors


# ============================================================================
# VALIDATION — BILLING STATUS
# ============================================================================

def validate_billing_status(
    value: BillingStatusView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingStatusView):
        return ["INVALID_BILLING_STATUS_TYPE"]

    if value.active and value.restricted:
        errors.append(
            "ACTIVE_AND_RESTRICTED_STATUS_CONFLICT"
        )

    if (
        value.state == BillingAccountState.ACTIVE
        and not value.active
    ):
        errors.append(
            "ACTIVE_STATE_WITHOUT_ACTIVE_FLAG"
        )

    if (
        value.state in {
            BillingAccountState.SUSPENDED,
            BillingAccountState.INACTIVE,
        }
        and value.active
    ):
        errors.append(
            "RESTRICTED_STATE_MARKED_ACTIVE"
        )

    return errors


# ============================================================================
# VALIDATION — PAYMENT METHOD
# ============================================================================

def validate_billing_payment_method(
    value: BillingPaymentMethodView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        value,
        BillingPaymentMethodView,
    ):
        return ["INVALID_PAYMENT_METHOD_TYPE"]

    if value.available and not value.method_type:
        errors.append(
            "PAYMENT_METHOD_AVAILABLE_WITHOUT_TYPE"
        )

    return errors


# ============================================================================
# VALIDATION — INVOICE
# ============================================================================

def validate_billing_invoice(
    value: BillingInvoiceView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingInvoiceView):
        return ["INVALID_BILLING_INVOICE_TYPE"]

    if value.state == InvoiceState.PAID and not value.paid_date:
        errors.append(
            "PAID_INVOICE_WITHOUT_PAID_DATE"
        )

    if value.document_available and not value.invoice_id:
        errors.append(
            "INVOICE_DOCUMENT_WITHOUT_INVOICE_ID"
        )

    return errors


# ============================================================================
# VALIDATION — ENTITLEMENT
# ============================================================================

def validate_billing_entitlement(
    value: BillingEntitlementView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        value,
        BillingEntitlementView,
    ):
        return ["INVALID_BILLING_ENTITLEMENT_TYPE"]

    if value.enabled and not value.name:
        errors.append(
            "ENABLED_ENTITLEMENT_WITHOUT_NAME"
        )

    return errors


# ============================================================================
# VALIDATION — PAGE VIEW
# ============================================================================

def validate_billing_page_view(
    value: BillingPageView,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingPageView):
        return ["INVALID_BILLING_PAGE_VIEW_TYPE"]

    if value.page_name != BILLING_PAGE_NAME:
        errors.append(
            "INVALID_BILLING_PAGE_NAME"
        )

    if value.route != BILLING_ROUTE:
        errors.append(
            "INVALID_BILLING_ROUTE"
        )

    if (
        not value.authenticated
        and value.status != BillingPageStatus.LOCKED
    ):
        errors.append(
            "UNAUTHENTICATED_BILLING_PAGE_NOT_LOCKED"
        )

    errors.extend(
        validate_billing_identity(value.identity)
    )

    errors.extend(
        validate_billing_plan(value.plan)
    )

    errors.extend(
        validate_billing_subscription(
            value.subscription
        )
    )

    errors.extend(
        validate_billing_status(
            value.billing_status
        )
    )

    errors.extend(
        validate_billing_payment_method(
            value.payment_method
        )
    )

    for invoice in value.invoices:
        errors.extend(
            validate_billing_invoice(invoice)
        )

    for entitlement in value.entitlements:
        errors.extend(
            validate_billing_entitlement(entitlement)
        )

    return errors


# ============================================================================
# VALIDATION — COMPOSITION
# ============================================================================

def validate_billing_composition(
    value: BillingPageComposition,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        value,
        BillingPageComposition,
    ):
        return ["INVALID_BILLING_COMPOSITION_TYPE"]

    errors.extend(
        validate_billing_page_view(
            value.page
        )
    )

    if value.summary.invoice_count < 0:
        errors.append(
            "NEGATIVE_INVOICE_COUNT"
        )

    if value.summary.entitlement_count < 0:
        errors.append(
            "NEGATIVE_ENTITLEMENT_COUNT"
        )

    if len(value.errors) > 100:
        errors.append(
            "EXCESSIVE_BILLING_ERROR_COUNT"
        )

    return errors


# ============================================================================
# VALIDATION — STATE
# ============================================================================

def validate_billing_page_state(
    value: BillingPageState,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(value, BillingPageState):
        return ["INVALID_BILLING_PAGE_STATE_TYPE"]

    if value.interaction_count < 0:
        errors.append(
            "NEGATIVE_INTERACTION_COUNT"
        )

    if value.refresh_count < 0:
        errors.append(
            "NEGATIVE_REFRESH_COUNT"
        )

    if not value.authenticated and not value.locked:
        errors.append(
            "UNAUTHENTICATED_BILLING_STATE_NOT_LOCKED"
        )

    if value.ready and value.locked:
        errors.append(
            "BILLING_STATE_READY_WHILE_LOCKED"
        )

    if (
        value.status == BillingPageStatus.READY
        and not value.authenticated
    ):
        errors.append(
            "READY_BILLING_STATE_WITHOUT_AUTHENTICATION"
        )

    return errors


# ============================================================================
# AUTHORITY VALIDATION
# ============================================================================

def validate_billing_authority() -> List[str]:
    errors: List[str] = []

    forbidden_authorities = {
        "billing_authority",
        "payment_authority",
        "transaction_authority",
        "subscription_authority",
        "entitlement_authority",
        "invoice_mutation",
        "refund_authority",
        "credential_authority",
        "market_data_authority",
        "evidence_authority",
        "market_context_authority",
        "intelligence_authority",
        "decision_authority",
        "d13_authority",
        "risk_authority",
        "cas_authority",
        "execution_authority",
        "order_authority",
        "position_authority",
        "upstream_mutation",
    }

    for authority in forbidden_authorities:
        if BILLING_UI_AUTHORITY.get(authority) is not False:
            errors.append(
                f"FORBIDDEN_AUTHORITY_ENABLED:{authority}"
            )

    required_presentation_authorities = {
        "billing_presentation",
        "subscription_presentation",
        "entitlement_presentation",
        "invoice_presentation",
        "payment_method_presentation",
        "billing_navigation",
        "billing_summary",
        "display_configuration",
    }

    for authority in required_presentation_authorities:
        if BILLING_UI_AUTHORITY.get(authority) is not True:
            errors.append(
                f"REQUIRED_PRESENTATION_AUTHORITY_DISABLED:{authority}"
            )

    return errors


# ============================================================================
# VALIDATION — INTERACTION
# ============================================================================

def validate_billing_interaction_result(
    value: BillingInteractionResult,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        value,
        BillingInteractionResult,
    ):
        return [
            "INVALID_BILLING_INTERACTION_RESULT_TYPE"
        ]

    if not value.interaction:
        errors.append(
            "MISSING_BILLING_INTERACTION"
        )

    if not value.requested_route:
        errors.append(
            "MISSING_REQUESTED_BILLING_ROUTE"
        )

    if not value.resolved_route:
        errors.append(
            "MISSING_RESOLVED_BILLING_ROUTE"
        )

    if value.allowed and not value.resolved_route:
        errors.append(
            "ALLOWED_INTERACTION_WITHOUT_ROUTE"
        )

    return errors


# ============================================================================
# VALIDATION — SNAPSHOT
# ============================================================================

def validate_billing_snapshot(
    value: BillingPageSnapshot,
) -> List[str]:
    errors: List[str] = []

    if not isinstance(
        value,
        BillingPageSnapshot,
    ):
        return ["INVALID_BILLING_SNAPSHOT_TYPE"]

    errors.extend(
        validate_billing_page_state(
            value.state
        )
    )

    errors.extend(
        validate_billing_composition(
            value.composition
        )
    )

    if value.metadata.get(
        "billing_authority"
    ) is not False:
        errors.append(
            "SNAPSHOT_BILLING_AUTHORITY_VIOLATION"
        )

    if value.metadata.get(
        "subscription_authority"
    ) is not False:
        errors.append(
            "SNAPSHOT_SUBSCRIPTION_AUTHORITY_VIOLATION"
        )

    if value.metadata.get(
        "payment_authority"
    ) is not False:
        errors.append(
            "SNAPSHOT_PAYMENT_AUTHORITY_VIOLATION"
        )

    if value.metadata.get(
        "entitlement_authority"
    ) is not False:
        errors.append(
            "SNAPSHOT_ENTITLEMENT_AUTHORITY_VIOLATION"
        )

    return errors


# ============================================================================
# BILLING PAGE HEALTH
# ============================================================================

@dataclass(frozen=True)
class BillingPageHealth:
    engine: str
    version: str

    operational: bool
    healthy: bool

    authenticated: bool
    initialized: bool
    ready: bool
    locked: bool

    status: BillingPageStatus

    validation_errors: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


def build_billing_page_health(
    controller: BillingPageController,
    composition: Optional[
        BillingPageComposition
    ] = None,
) -> BillingPageHealth:
    state = controller.state

    errors = validate_billing_page_state(
        state
    )

    if composition is not None:
        errors.extend(
            validate_billing_composition(
                composition
            )
        )

    errors.extend(
        validate_billing_authority()
    )

    healthy = len(errors) == 0

    operational = (
        state.initialized
        and healthy
    )

    return BillingPageHealth(
        engine=BILLING_PAGE_ENGINE,
        version=BILLING_PAGE_VERSION,
        operational=operational,
        healthy=healthy,
        authenticated=state.authenticated,
        initialized=state.initialized,
        ready=state.ready,
        locked=state.locked,
        status=state.status,
        validation_errors=errors,
        metadata={
            "ui_only": True,
            "billing_authority": False,
            "payment_authority": False,
            "subscription_authority": False,
            "entitlement_authority": False,
            "invoice_mutation": False,
            "refund_authority": False,
            "execution": False,
        },
    )


def serialize_billing_page_health(
    value: BillingPageHealth,
) -> Dict[str, Any]:
    return _serialize_billing_value(value)


# ============================================================================
# OPERATIONAL CHECK
# ============================================================================

def billing_page_operational_check(
    controller: Optional[
        BillingPageController
    ] = None,
) -> Dict[str, Any]:
    """
    Lightweight module operational check.

    This verifies presentation architecture only.
    """

    controller = (
        controller
        or BillingPageController()
    )

    authority_errors = (
        validate_billing_authority()
    )

    state_errors = (
        validate_billing_page_state(
            controller.state
        )
    )

    errors = authority_errors + state_errors

    return {
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "module": BILLING_PAGE_NAME,
        "operational": (
            len(errors) == 0
            and controller.state.initialized
        ),
        "healthy": len(errors) == 0,
        "initialized": controller.state.initialized,
        "ready": controller.state.ready,
        "locked": controller.state.locked,
        "validation_errors": errors,

        "ui_only": True,

        "billing_authority": False,
        "payment_authority": False,
        "subscription_authority": False,
        "entitlement_authority": False,
        "invoice_mutation": False,
        "refund_authority": False,

        "intelligence_generation": False,
        "decision_generation": False,
        "d13_modification": False,
        "risk_generation": False,
        "cas_generation": False,
        "execution": False,
    }


# ============================================================================
# SUMMARY
# ============================================================================

def billing_page_summary(
    controller: Optional[
        BillingPageController
    ] = None,
) -> Dict[str, Any]:
    controller = (
        controller
        or BillingPageController()
    )

    state = controller.state

    return {
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "name": BILLING_PAGE_NAME,
        "title": BILLING_PAGE_TITLE,
        "route": BILLING_ROUTE,

        "status": state.status.value,
        "mode": state.mode.value,
        "current_route": state.current_route,

        "authenticated": state.authenticated,
        "plus_enabled": state.plus_enabled,

        "initialized": state.initialized,
        "ready": state.ready,
        "locked": state.locked,

        "interaction_count": state.interaction_count,
        "refresh_count": state.refresh_count,

        "authority": {
            "billing": False,
            "payment": False,
            "subscription": False,
            "entitlement": False,
            "invoice_mutation": False,
            "refund": False,
            "intelligence": False,
            "decision": False,
            "d13": False,
            "risk": False,
            "cas": False,
            "execution": False,
        },

        "ui_only": True,
    }


# ============================================================================
# DEFAULT BILLING PAGE
# ============================================================================

def create_default_billing_page(
    *,
    user_id: str = "",
    authenticated: bool = False,
    plus_enabled: bool = False,
) -> BillingPageController:
    """
    Create a safe default Billing presentation controller.
    """

    controller = BillingPageController(
        create_billing_page_state(
            user_id=user_id,
            authenticated=authenticated,
            plus_enabled=plus_enabled,
        )
    )

    return controller


# ============================================================================
# MODULE CHECK
# ============================================================================

def billing_page_module_check() -> Dict[str, Any]:
    """
    Static module architecture check.
    """

    authority_errors = validate_billing_authority()

    default_controller = (
        create_default_billing_page()
    )

    state_errors = validate_billing_page_state(
        default_controller.state
    )

    errors = authority_errors + state_errors

    return {
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "module": BILLING_PAGE_NAME,

        "module_valid": len(errors) == 0,

        "validation_errors": errors,

        "contracts": {
            "identity": True,
            "plan": True,
            "subscription": True,
            "billing_status": True,
            "payment_method": True,
            "invoice": True,
            "entitlement": True,
            "page_view": True,
            "composition": True,
            "state": True,
            "snapshot": True,
        },

        "presentation": {
            "billing": True,
            "subscription": True,
            "entitlement": True,
            "invoice": True,
            "payment_method": True,
        },

        "forbidden_authority": {
            "billing": False,
            "payment": False,
            "subscription": False,
            "entitlement": False,
            "invoice_mutation": False,
            "refund": False,
            "intelligence": False,
            "decision": False,
            "d13": False,
            "risk": False,
            "cas": False,
            "execution": False,
        },
    }


# ============================================================================
# EXPORTS — PART 4
# ============================================================================

__all__.extend(
    [
        # Serialization
        "_serialize_billing_value",
        "serialize_billing_identity",
        "serialize_billing_plan",
        "serialize_billing_subscription",
        "serialize_billing_status",
        "serialize_billing_payment_method",
        "serialize_billing_invoice",
        "serialize_billing_entitlement",
        "serialize_billing_badge",
        "serialize_billing_action",
        "serialize_billing_page_request",
        "serialize_billing_page_view",
        "serialize_billing_source_state",
        "serialize_billing_section",
        "serialize_billing_summary",
        "serialize_billing_composition",
        "serialize_billing_page_state",
        "serialize_billing_snapshot",
        "serialize_billing_interaction_result",

        # Validation
        "validate_billing_identity",
        "validate_billing_plan",
        "validate_billing_subscription",
        "validate_billing_status",
        "validate_billing_payment_method",
        "validate_billing_invoice",
        "validate_billing_entitlement",
        "validate_billing_page_view",
        "validate_billing_composition",
        "validate_billing_page_state",
        "validate_billing_authority",
        "validate_billing_interaction_result",
        "validate_billing_snapshot",

        # Health / checks
        "BillingPageHealth",
        "build_billing_page_health",
        "serialize_billing_page_health",
        "billing_page_operational_check",
        "billing_page_summary",
        "create_default_billing_page",
        "billing_page_module_check",
    ]
)
# ============================================================================
# REFRESH
# ============================================================================

def refresh_billing_page(
    controller: BillingPageController,
    source: Optional[
        BillingSourceState | Dict[str, Any]
    ] = None,
) -> BillingPageComposition:
    """
    Rebuild the Billing presentation from upstream source truth.

    This does NOT refresh, mutate, charge or modify the billing domain.
    """

    if not isinstance(controller, BillingPageController):
        raise TypeError(
            "controller must be BillingPageController"
        )

    controller._state.refresh_count += 1
    controller._state.last_interaction = (
        BillingInteraction.REFRESH
    )

    return controller.compose(source)


# ============================================================================
# GET CURRENT PAGE
# ============================================================================

def get_billing_page(
    controller: BillingPageController,
    source: Optional[
        BillingSourceState | Dict[str, Any]
    ] = None,
) -> BillingPageComposition:
    """
    Return current Billing presentation.

    When source is omitted, a safe degraded presentation is produced.
    """

    if not isinstance(controller, BillingPageController):
        raise TypeError(
            "controller must be BillingPageController"
        )

    if source is None:
        source = BillingSourceState(
            source_available=False,
            source_errors=[
                "BILLING_SOURCE_NOT_PROVIDED"
            ],
        )

    return controller.compose(source)


# ============================================================================
# ROUTE ACCESS HELPER
# ============================================================================

def can_navigate_billing_page(
    controller: BillingPageController,
    route: str,
) -> bool:
    """
    Check presentation-level navigation access.
    """

    if not isinstance(controller, BillingPageController):
        return False

    allowed, _ = evaluate_billing_route_access(
        route,
        authenticated=controller.state.authenticated,
        locked=controller.state.locked,
    )

    return allowed


def select_billing_route(
    controller: BillingPageController,
    route: str,
) -> BillingInteractionResult:
    """
    Select a Billing UI route.

    No billing operation is executed.
    """

    if not isinstance(controller, BillingPageController):
        raise TypeError(
            "controller must be BillingPageController"
        )

    return controller.navigate(route)


# ============================================================================
# UI LOCK HELPER
# ============================================================================

def lock_billing_page(
    controller: BillingPageController,
) -> BillingPageState:
    """
    Lock Billing presentation only.

    This does NOT:
    - suspend a subscription
    - cancel a subscription
    - revoke entitlement
    - block payment
    - modify an invoice
    """

    if not isinstance(controller, BillingPageController):
        raise TypeError(
            "controller must be BillingPageController"
        )

    controller.lock()

    return controller.state


# ============================================================================
# DIAGNOSTICS
# ============================================================================

def diagnose_billing_page(
    controller: BillingPageController,
    composition: Optional[
        BillingPageComposition
    ] = None,
) -> Dict[str, Any]:
    """
    Full Billing UI diagnostic.

    Diagnostic output is informational only.
    """

    if not isinstance(controller, BillingPageController):
        raise TypeError(
            "controller must be BillingPageController"
        )

    state = controller.state

    if composition is None:
        composition = controller.last_composition

    state_errors = validate_billing_page_state(
        state
    )

    authority_errors = validate_billing_authority()

    composition_errors: List[str] = []

    if composition is not None:
        composition_errors = (
            validate_billing_composition(
                composition
            )
        )

    all_errors = (
        state_errors
        + authority_errors
        + composition_errors
    )

    return {
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "module": BILLING_PAGE_NAME,

        "status": state.status.value,
        "mode": state.mode.value,
        "current_route": state.current_route,

        "authenticated": state.authenticated,
        "plus_enabled": state.plus_enabled,

        "initialized": state.initialized,
        "ready": state.ready,
        "locked": state.locked,

        "interaction_count": state.interaction_count,
        "refresh_count": state.refresh_count,

        "has_composition": composition is not None,

        "healthy": len(all_errors) == 0,

        "validation": {
            "state_errors": state_errors,
            "authority_errors": authority_errors,
            "composition_errors": composition_errors,
            "all_errors": all_errors,
        },

        "authority": {
            "billing": False,
            "payment": False,
            "transaction": False,
            "subscription": False,
            "entitlement": False,
            "invoice_mutation": False,
            "refund": False,
            "intelligence": False,
            "decision": False,
            "d13": False,
            "risk": False,
            "cas": False,
            "execution": False,
        },

        "ui_only": True,
    }


# ============================================================================
# ARCHITECTURE CONTRACT MANIFEST
# ============================================================================

def billing_page_contract_manifest() -> Dict[str, Any]:
    """
    Machine-readable architecture contract for Billing Page.
    """

    return {
        "module": BILLING_PAGE_NAME,
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "layer": "UI_PRESENTATION",

        "responsibility": [
            "BILLING_PRESENTATION",
            "SUBSCRIPTION_PRESENTATION",
            "ENTITLEMENT_PRESENTATION",
            "INVOICE_PRESENTATION",
            "PAYMENT_METHOD_PRESENTATION",
            "BILLING_NAVIGATION",
            "BILLING_SUMMARY",
        ],

        "input_flow": [
            "USER_SERVICE_OUTPUT",
            "PROFILE_SERVICE_OUTPUT",
            "PLAN_SERVICE_OUTPUT",
            "SUBSCRIBER_SERVICE_OUTPUT",
            "ENTITLEMENT_SERVICE_OUTPUT",
            "BILLING_SERVICE_OUTPUT",
            "APPLICATION_SESSION_STATE",
        ],

        "processing": [
            "SOURCE_NORMALIZATION",
            "PRESENTATION_READINESS",
            "SUMMARY_COMPOSITION",
            "SECTION_COMPOSITION",
            "VIEW_COMPOSITION",
            "SNAPSHOT",
            "VALIDATION",
            "DIAGNOSTICS",
        ],

        "outputs": [
            "BILLING_PAGE_VIEW",
            "BILLING_PAGE_COMPOSITION",
            "BILLING_PAGE_SNAPSHOT",
            "BILLING_PAGE_HEALTH",
            "BILLING_PAGE_DIAGNOSTICS",
        ],

        "authority_owners": {
            "billing": "BILLING_SERVICE",
            "payment": "PAYMENT_PROVIDER_OR_BILLING_SERVICE",
            "subscription": "SUBSCRIBER_SERVICE",
            "entitlement": "ENTITLEMENT_SERVICE",
            "plan": "PLAN_SERVICE",
            "authentication": "AUTHENTICATION_LAYER",
            "security": "SECURITY_LAYER",
            "decision": "DECISION_CORTEX",
            "d13": "D13_DECISION_AUTHORITY",
            "risk": "RISK_LAYER",
            "cas": "CAS",
            "execution": "EXECUTION_LAYER",
        },

        "principles": [
            "PRESENTATION_ONLY",
            "UPSTREAM_TRUTH_PRESERVED",
            "NO_FAKE_BILLING_TRUTH",
            "NO_PAYMENT_EXECUTION",
            "NO_TRANSACTION_MUTATION",
            "NO_SUBSCRIPTION_MUTATION",
            "NO_ENTITLEMENT_MUTATION",
            "NO_INVOICE_MUTATION",
            "NO_REFUND_AUTHORITY",
            "NO_INTELLIGENCE_GENERATION",
            "NO_DECISION_GENERATION",
            "NO_D13_MUTATION",
            "NO_RISK_OVERRIDE",
            "NO_CAS_BYPASS",
            "NO_EXECUTION",
        ],

        "forbidden_authority": {
            "billing": False,
            "payment": False,
            "transaction": False,
            "subscription": False,
            "entitlement": False,
            "invoice_mutation": False,
            "refund": False,
            "intelligence": False,
            "decision": False,
            "d13": False,
            "risk": False,
            "cas": False,
            "execution": False,
        },

        "ui_only": True,
    }


# ============================================================================
# FINAL MODULE VALIDATION
# ============================================================================

def validate_billing_page_module() -> Dict[str, Any]:
    """
    Final static architecture validation.
    """

    module_check = billing_page_module_check()
    authority_errors = validate_billing_authority()

    controller = create_default_billing_page()

    snapshot = build_billing_page_snapshot(
        controller,
        BillingSourceState(
            source_available=False,
            source_errors=[
                "DEFAULT_SOURCE_NOT_CONNECTED"
            ],
        ),
    )

    snapshot_errors = validate_billing_snapshot(
        snapshot
    )

    contract = billing_page_contract_manifest()

    contract_errors: List[str] = []

    if contract.get("layer") != "UI_PRESENTATION":
        contract_errors.append(
            "INVALID_BILLING_CONTRACT_LAYER"
        )

    if contract.get("ui_only") is not True:
        contract_errors.append(
            "BILLING_CONTRACT_NOT_UI_ONLY"
        )

    errors = (
        module_check["validation_errors"]
        + authority_errors
        + snapshot_errors
        + contract_errors
    )

    return {
        "engine": BILLING_PAGE_ENGINE,
        "version": BILLING_PAGE_VERSION,
        "module": BILLING_PAGE_NAME,

        "valid": len(errors) == 0,
        "errors": errors,

        "module_check": module_check,
        "snapshot_valid": len(snapshot_errors) == 0,
        "contract_valid": len(contract_errors) == 0,

        "ui_only": True,
        "billing_authority": False,
        "payment_authority": False,
        "subscription_authority": False,
        "entitlement_authority": False,
        "execution": False,
    }


# ============================================================================
# DEFAULT SNAPSHOT
# ============================================================================

def default_billing_page_snapshot() -> BillingPageSnapshot:
    """
    Safe default snapshot for initialization/testing.

    No real billing state is fabricated.
    """

    controller = create_default_billing_page()

    return build_billing_page_snapshot(
        controller,
        BillingSourceState(
            source_available=False,
            source_errors=[
                "DEFAULT_BILLING_SOURCE_NOT_CONNECTED"
            ],
        ),
    )


# ============================================================================
# FINAL EXPORTS — PART 5
# ============================================================================

__all__.extend(
    [
        # Refresh / retrieval
        "refresh_billing_page",
        "get_billing_page",

        # Navigation
        "can_navigate_billing_page",
        "select_billing_route",

        # Presentation lock
        "lock_billing_page",

        # Diagnostics
        "diagnose_billing_page",

        # Architecture
        "billing_page_contract_manifest",
        "validate_billing_page_module",

        # Default
        "default_billing_page_snapshot",
    ]
)