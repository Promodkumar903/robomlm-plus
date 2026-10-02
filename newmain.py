```python
"""
ROBOMLM_PLUS — Clean FastAPI Application Entry Point
======================================================

Purpose
-------
This is the NEW backend application entry point.

Important:
- Does NOT import server.py
- Does NOT import the legacy Streamlit UI
- Does NOT contain business/intelligence logic
- Existing engines/services remain authoritative
- Existing routers can be registered in one controlled place

Run
---
python -m uvicorn main:app --reload

Health
------
GET /health
"""

from fastapi import FastAPI


# ============================================================================
# APPLICATION
# ============================================================================

app = FastAPI(
    title="ROBOMLM_PLUS",
    description="Market Intelligence Operating System",
    version="1.0.0",
)


# ============================================================================
# HEALTH
# ============================================================================

@app.get("/health", tags=["system"])
def health() -> dict:
    """
    Basic application health check.

    This checks only that the new FastAPI application is running.
    It intentionally does not depend on any existing ROBOMLM engine.
    """
    return {
        "status": "ok",
        "service": "ROBOMLM_PLUS",
        "version": "1.0.0",
    }


# ============================================================================
# EXISTING ROUTER REGISTRATION
# ============================================================================

def register_routers(application: FastAPI) -> None:
    """
    Single controlled location for registering existing API routers.

    IMPORTANT
    ---------
    Do not import server.py here.

    Do not put business logic here.

    Existing authoritative routers should be added here only after their
    actual module/export names are verified.

    Example:

        from app.api.v1.terminal_api import router as terminal_router

        application.include_router(
            terminal_router,
            prefix="/api",
        )

    Additional routers will be added here in controlled stages:
        - Terminal
        - Discovery
        - Buyer
        - Memory
        - Research
        - Automation
        - Account / Portfolio

    Keeping registration centralized prevents the new entry point from
    becoming another monolithic server.py.
    """

    # ------------------------------------------------------------------------
    # ROUTER REGISTRATION STARTS HERE
    # ------------------------------------------------------------------------
    #
    # Example only — intentionally disabled until the real router exports
    # are verified:
    #
    # from app.api.v1.terminal_api import router as terminal_router
    #
    # application.include_router(
    #     terminal_router,
    #     prefix="/api",
    # )
    #
    # ------------------------------------------------------------------------
    # ROUTER REGISTRATION ENDS HERE
    # ------------------------------------------------------------------------


# Register currently verified routers.
register_routers(app)


# ============================================================================
# ROOT
# ============================================================================

@app.get("/", tags=["system"])
def root() -> dict:
    """
    Minimal application identity endpoint.
    """
    return {
        "service": "ROBOMLM_PLUS",
        "status": "running",
        "api": "/api",
        "health": "/health",
    }
```
