# app/ui/app.py
"""
ROBOMLM_PLUS — UI Main Entry Point
Uses UIRouter from app.ui.ui.router
"""
import streamlit as st
from app.ui.ui.router import (
    UIRouter,
    ROUTE_TERMINAL,
    ROUTE_LOGIN,
    ROUTE_DISCOVERY,
    ROUTE_MEMORY,
    ROUTE_RESEARCH,
    ROUTE_AUTOMATION,
    ROUTE_ACCOUNT,
    RouteAccess,
    create_ui_router,
)

# ---------------------------------------------------------------------------
# Session bootstrap
# ---------------------------------------------------------------------------
if "router" not in st.session_state:
    st.session_state.router = create_ui_router(
        authenticated=False,
        plus_enabled=False,
        current_route=ROUTE_LOGIN,
    )
    st.session_state.router.initialize()

router: UIRouter = st.session_state.router

# ---------------------------------------------------------------------------
# Sidebar — auth toggles (testing ke liye)
# ---------------------------------------------------------------------------
st.sidebar.title("ROBOMLM")
st.sidebar.caption("Market Intelligence OS")

# Simple login simulation
if not router.state.authenticated:
    if st.sidebar.button("🔓 Login (demo)"):
        router.set_authenticated(True)
        router.set_plus_enabled(True)  # demo: PLUS bhi on
        router.navigate(ROUTE_TERMINAL)
        st.rerun()
else:
    st.sidebar.success("👤 Logged in")
    if st.sidebar.button("🔒 Logout"):
        router.set_authenticated(False)
        router.navigate(ROUTE_LOGIN)
        st.rerun()

# PLUS toggle
if router.state.authenticated:
    plus = st.sidebar.checkbox("PLUS enabled", value=router.state.plus_enabled)
    if plus != router.state.plus_enabled:
        router.set_plus_enabled(plus)
        st.rerun()

st.sidebar.divider()

# ---------------------------------------------------------------------------
# Navigation menu
# ---------------------------------------------------------------------------
available = router.available_routes()
if available:
    route_labels = {r.route: f"{r.icon or '📄'}  {r.name}" for r in available}
    selected = st.sidebar.radio(
        "Navigate",
        options=[r.route for r in available],
        format_func=lambda x: route_labels.get(x, x),
        index=0,
    )
    if selected != router.state.current_route:
        result = router.navigate(selected)
        if result.allowed:
            st.rerun()
        else:
            st.sidebar.error(result.reason)
else:
    st.sidebar.warning("No routes available. Please login.")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
current_def = router.current_definition()
if current_def:
    st.title(f"{current_def.icon or '📄'}  {current_def.title}")
    st.caption(current_def.description)
else:
    st.title("ROBOMLM")

st.divider()

# ---------------------------------------------------------------------------
# Screen content — placeholder
# Yahan backend connection aayega.
# ---------------------------------------------------------------------------
route = router.state.current_route

if route == ROUTE_LOGIN:
    st.info("🔐 Login screen. Sidebar se 'Login (demo)' dabao.")
elif route == ROUTE_TERMINAL:
    st.subheader("Terminal")
    st.write("Market intelligence workspace — backend se data yahan aayega.")
    # TODO: backend call — e.g.
    # from app.intelligence.decision_cortex import get_latest_decision
    # st.json(get_latest_decision())
elif route == ROUTE_DISCOVERY:
    st.subheader("Discovery")
    st.write("Opportunity scanner — backend se data yahan aayega.")
elif route == ROUTE_MEMORY:
    st.subheader("Market Memory")
    st.write("Historical evidence and decisions.")
elif route == ROUTE_RESEARCH:
    st.subheader("Research Lab")
    st.write("Research and analysis workspace.")
elif route == ROUTE_AUTOMATION:
    st.subheader("AUTOROBOMLM (PLUS)")
    st.write("Automation workspace.")
elif route == ROUTE_ACCOUNT:
    st.subheader("Account & Settings")
    st.write("Profile, security, billing.")
else:
    st.warning(f"No renderer for route: {route}")

# ---------------------------------------------------------------------------
# Footer — router health
# ---------------------------------------------------------------------------
with st.expander("Router state (debug)"):
    snap = router.snapshot()
    st.json({
        "current_route": snap.current_route,
        "authenticated": snap.authenticated,
        "plus_enabled": snap.plus_enabled,
        "navigation_count": snap.navigation_count,
        "denied_count": snap.denied_count,
    })