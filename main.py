"""
ROBOMLM_PLUS — Application Entry Point (Streamlit)
====================================================
Presentation-only shell. Uses UIRouter + all page modules.

Safe imports: agar koi page fail ho, app crash nahi hoga — status dikhega.
"""

import streamlit as st

from app.ui.router import (
    UIRouter, ROUTE_TERMINAL, ROUTE_LOGIN, ROUTE_DISCOVERY,
    ROUTE_MEMORY, ROUTE_RESEARCH, ROUTE_AUTOMATION, ROUTE_ACCOUNT,
    ROUTE_CONSTITUTION, ROUTE_RISK_DISCLOSURE,
    create_ui_router,
)

from app.ui.terminal.terminal_page import (
    TerminalSourceState, TerminalIdentityView, MarketContextView,
    MarketState, EvidenceCardView, IntelligenceCardView,
    IntelligenceBias, SignalStrength, D13OutlookView, CASView,
    RiskView, PortfolioSnapshotView, TerminalPriority,
    compose_terminal_page,
)


# ============================================================================
# SAFE IMPORT HELPER — import errors app ko crash nahi karenge
# ============================================================================

def _safe_import(modpath: str):
    try:
        mod = __import__(modpath, fromlist=["*"])
        return mod, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


_PAGES = {
    "discovery":  _safe_import("app.ui.discovery.discovery_page"),
    "memory":     _safe_import("app.ui.memory.memory_page"),
    "research":   _safe_import("app.ui.research.research_page"),
    "automation": _safe_import("app.ui.automation.automation_page"),
    "account":    _safe_import("app.ui.account.account_page"),
}


# ============================================================================
# ICON MAP
# ============================================================================

ICON_MAP = {
    "terminal": "⌂", "search": "⌕", "database": "◈",
    "flask": "⌘", "bolt": "⚙", "user": "◎",
    "login": "🔐", "constitution": "📜", "risk": "⚠",
}

def _icon(name: str) -> str:
    return ICON_MAP.get((name or "").lower(), "📄")


# ============================================================================
# TERMINAL — DEMO SOURCE + RENDERER (already working)
# ============================================================================

def _build_demo_terminal_source() -> TerminalSourceState:
    return TerminalSourceState(
        identity=TerminalIdentityView(
            user_id="demo_user", display_name="Demo Trader",
            authenticated=True, plus_enabled=True,
        ),
        market_context=MarketContextView(
            market_name="Crypto", market_state=MarketState.OPEN,
            active_symbol="BTC/USDT", active_contract="PERP",
            market_session="24x7", market_timezone="UTC",
        ),
        evidence_cards=[
            EvidenceCardView(evidence_id="e1", title="Bid Pressure", value="76 / 100", confidence=0.76, priority=TerminalPriority.HIGH),
            EvidenceCardView(evidence_id="e2", title="OI Flow", value="71 / 100", confidence=0.71),
            EvidenceCardView(evidence_id="e3", title="Trend", value="82 / 100", confidence=0.82, priority=TerminalPriority.HIGH),
            EvidenceCardView(evidence_id="e4", title="Volume", value="64 / 100", confidence=0.64),
            EvidenceCardView(evidence_id="e5", title="Liquidity", value="88 / 100", confidence=0.88, priority=TerminalPriority.HIGH),
            EvidenceCardView(evidence_id="e6", title="Structure", value="73 / 100", confidence=0.73),
        ],
        intelligence_cards=[
            IntelligenceCardView(intelligence_id="i1", title="Order Flow Bias", bias=IntelligenceBias.BULLISH, strength=SignalStrength.STRONG, summary="Buyers dominating, absorption at lows.", confidence=0.78),
            IntelligenceCardView(intelligence_id="i2", title="Regime", bias=IntelligenceBias.BULLISH, strength=SignalStrength.MODERATE, summary="Trend regime, momentum expanding.", confidence=0.71),
            IntelligenceCardView(intelligence_id="i3", title="Volatility", bias=IntelligenceBias.NEUTRAL, strength=SignalStrength.WEAK, summary="Vol stable, no expansion yet.", confidence=0.55),
            IntelligenceCardView(intelligence_id="i4", title="Structure", bias=IntelligenceBias.BULLISH, strength=SignalStrength.STRONG, summary="Higher lows building.", confidence=0.74),
        ],
        d13_outlook=D13OutlookView(outlook_id="d13-001", direction="LONG", confidence=0.72, summary="MTF aligned bullish. Entry quality high. RR acceptable.", horizon="intraday"),
        cas=CASView(cas_score=87.0, readiness="READY", summary="All gates passed. Capital allocation OK."),
        risk=RiskView(risk_score=28.0, risk_level="LOW", summary="Spread normal, latency low, liquidity deep."),
        portfolio=PortfolioSnapshotView(account_name="PAPER-01", equity=100482.50, balance=100414.62, pnl=67.88, positions=1),
        source_available=True, source_errors=[],
    )


def _render_terminal() -> None:
    source = _build_demo_terminal_source()
    composition = compose_terminal_page(source)
    page = composition.page

    if page.status.value == "READY":
        st.success(f"● {page.page_title} — {page.status.value}")
    elif page.status.value == "LOCKED":
        st.error("🔒 Terminal locked. Please login.")
        return
    else:
        st.warning(f"⚠ {page.status.value}")

    mc = page.market_context
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Symbol", mc.active_symbol or "—")
    c2.metric("Market", mc.market_name or "—")
    c3.metric("State", mc.market_state.value)
    c4.metric("Session", mc.market_session or "—")
    st.divider()

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("#### 🎯 D13 Outlook")
        d = page.d13_outlook
        direction = (d.direction or "—").upper()
        color = "#16a34a" if direction == "LONG" else ("#dc2626" if direction == "SHORT" else "#6b7280")
        st.markdown(
            f"<div style='padding:1em;border-radius:8px;background:{color}22;border-left:4px solid {color}'>"
            f"<div style='font-size:1.6em;font-weight:700;color:{color}'>{direction}</div>"
            f"<div style='margin-top:.4em;color:#4b5563'>{d.summary}</div>"
            f"<div style='margin-top:.6em;font-size:.9em;color:#6b7280'>Horizon: {d.horizon} · Confidence: {d.confidence:.2f}</div>"
            f"</div>", unsafe_allow_html=True,
        )
    with col_right:
        st.markdown("#### 🛡 Risk & CAS")
        r = page.risk; c = page.cas
        rc1, rc2 = st.columns(2)
        rc1.metric("Risk Score", f"{r.risk_score:.0f}", r.risk_level)
        rc2.metric("CAS Score", f"{c.cas_score:.0f}", c.readiness)
        st.caption(f"**Risk:** {r.summary}")
        st.caption(f"**CAS:** {c.summary}")
    st.divider()

    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("#### 🔍 Evidence")
        if not page.evidence_cards:
            st.info("No evidence available.")
        for card in page.evidence_cards:
            cc1, cc2 = st.columns([3, 1])
            with cc1:
                st.markdown(f"**{card.title}**")
                st.progress(min(max(card.confidence, 0.0), 1.0))
            with cc2:
                st.markdown(f"<div style='text-align:right;font-weight:600;padding-top:1.4em'>{card.value}</div>", unsafe_allow_html=True)
    with col_right:
        st.markdown("#### 🧠 Intelligence")
        if not page.intelligence_cards:
            st.info("No intelligence available.")
        for card in page.intelligence_cards:
            bias_color = {"BULLISH": "#16a34a", "BEARISH": "#dc2626", "NEUTRAL": "#6b7280", "MIXED": "#f59e0b"}.get(card.bias.value, "#6b7280")
            st.markdown(
                f"<div style='padding:.7em;margin-bottom:.5em;border-radius:6px;background:{bias_color}11;border-left:3px solid {bias_color}'>"
                f"<b>{card.title}</b> <span style='color:{bias_color};font-weight:600'>· {card.bias.value}</span> "
                f"<span style='color:#6b7280;font-size:.85em'>({card.strength.value})</span>"
                f"<div style='margin-top:.3em;color:#4b5563;font-size:.9em'>{card.summary}</div></div>",
                unsafe_allow_html=True,
            )
    st.divider()

    st.markdown("#### 💼 Portfolio")
    p = page.portfolio
    if not p.visible:
        st.info("Portfolio view hidden.")
    else:
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Account", p.account_name or "—")
        p2.metric("Equity", f"{p.equity:,.2f}")
        p3.metric("PnL", f"{p.pnl:+,.2f}")
        p4.metric("Positions", p.positions)


# ============================================================================
# GENERIC PAGE STATUS RENDERER
# ============================================================================

def _render_page_status(page_key: str, page_title: str) -> None:
    """Show module import status + public API for a page."""

    if page_key not in _PAGES:
        st.warning(f"No module registered for: {page_key}")
        return

    mod, err = _PAGES[page_key]

    if err:
        st.error(f"❌ **{page_title}** module failed to import")
        st.code(err, language="text")
        st.info("Backup se file restore karo ya error ke hisaab se fix karenge.")
        return

    st.success(f"✅ **{page_title}** module imported: `{mod.__name__}`")

    public = sorted([n for n in dir(mod) if not n.startswith("_")])
    st.write(f"**Public API available:** {len(public)} names")

    with st.expander("📋 Public names (click to expand)"):
        st.write(public)

    # Try to find a known composer/controller factory
    candidates = [
        f"compose_{page_key}_page",
        f"create_default_{page_key}",
        f"default_{page_key}_snapshot",
        f"build_{page_key}_snapshot",
    ]
    found = None
    for cname in candidates:
        fn = getattr(mod, cname, None)
        if callable(fn):
            found = cname
            break

    if found:
        st.markdown(f"**Found composer:** `{found}` — calling with no args...")
        try:
            result = getattr(mod, found)()
            st.json(str(result)[:1500])
        except Exception as e:
            st.warning(f"`{found}()` failed: {e}")
    else:
        st.info(f"No standard composer found. Next step: inspect API above.")


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="ROBOMLM — Market Intelligence OS",
    page_icon="📈", layout="wide", initial_sidebar_state="expanded",
)


# ============================================================================
# SESSION BOOTSTRAP
# ============================================================================

if "router" not in st.session_state:
    st.session_state.router = create_ui_router(
        authenticated=False, plus_enabled=False, current_route=ROUTE_LOGIN,
    )
    st.session_state.router.initialize()

router: UIRouter = st.session_state.router


# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("ROBOMLM")
st.sidebar.caption("Market Intelligence OS")
st.sidebar.divider()

if not router.state.authenticated:
    st.sidebar.info("👤 Guest")
    if st.sidebar.button("🔓 Login (demo)", use_container_width=True):
        router.set_authenticated(True)
        router.navigate(ROUTE_TERMINAL)
        st.rerun()
else:
    st.sidebar.success("👤 Logged in")
    if st.sidebar.button("🔒 Logout", use_container_width=True):
        router.set_authenticated(False)
        router.navigate(ROUTE_LOGIN)
        st.rerun()

if router.state.authenticated:
    plus_now = st.sidebar.checkbox("PLUS enabled", value=router.state.plus_enabled)
    if plus_now != router.state.plus_enabled:
        router.set_plus_enabled(plus_now)
        st.rerun()

st.sidebar.divider()

available = router.available_routes()
if available:
    route_labels = {r.route: f"{_icon(r.icon)}  {r.name}" for r in available}
    route_list = [r.route for r in available]
    current_index = route_list.index(router.state.current_route) if router.state.current_route in route_list else 0
    selected = st.sidebar.radio("Navigate", options=route_list, format_func=lambda x: route_labels.get(x, x), index=current_index, key="nav_radio")
    if selected != router.state.current_route:
        result = router.navigate(selected)
        if result.allowed:
            st.rerun()
        else:
            st.sidebar.error(result.reason)
else:
    st.sidebar.warning("No routes available. Please login.")

st.sidebar.divider()
st.sidebar.caption("v0.1 · UI Layer · Presentation Only")


# ============================================================================
# HEADER
# ============================================================================

current_def = router.current_definition()
if current_def:
    st.title(f"{_icon(current_def.icon)}  {current_def.title}")
    st.caption(current_def.description)
else:
    st.title("ROBOMLM")
st.divider()


# ============================================================================
# DISPATCH
# ============================================================================

route = router.state.current_route

if route == ROUTE_LOGIN:
    st.subheader("🔐 Sign in to ROBOMLM")
    st.write("Sidebar mein **Login (demo)** button dabao — phir Terminal khul jayega.")

elif route == ROUTE_CONSTITUTION:
    st.subheader("📜 ROBOMLM Constitution")
    st.markdown(
        "- **Observe honestly. Reason scientifically. Challenge relentlessly.**\n"
        "- **Reject noise. Filter evidence. Execute discipline.**\n"
        "- Output only 3 states: PASSED / FAILED (reason) / INSUFFICIENT DATA.\n"
        "- Never guess. Never claim prediction certainty markets don't allow."
    )

elif route == ROUTE_RISK_DISCLOSURE:
    st.subheader("⚠ Risk Disclosure")
    st.warning("Trading involves risk. ROBOMLM provides intelligence, not guaranteed profits.")

elif route == ROUTE_TERMINAL:
    _render_terminal()

elif route == ROUTE_DISCOVERY:
    _render_page_status("discovery", "Discovery")

elif route == ROUTE_MEMORY:
    _render_page_status("memory", "Memory")

elif route == ROUTE_RESEARCH:
    _render_page_status("research", "Research")

elif route == ROUTE_AUTOMATION:
    _render_page_status("automation", "Automation")

elif route == ROUTE_ACCOUNT:
    _render_page_status("account", "Account")

else:
    st.warning(f"No renderer for route: {route}")


# ============================================================================
# DEBUG
# ============================================================================

with st.expander("🔧 Import status (debug)"):
    for key, (mod, err) in _PAGES.items():
        if err:
            st.write(f"❌ **{key}**: {err}")
        else:
            st.write(f"✅ **{key}**: {mod.__name__} loaded")