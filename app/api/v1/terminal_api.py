"""
ROBOMLM_PLUS
app/api/v1/terminal_api.py

Terminal API boundary.

Flow:

Frontend
    ->
Terminal API
    ->
Application Service
    ->
Existing ROBOMLM_PLUS backend
    ->
Evidence
    ->
Context
    ->
Intelligence
    ->
D1-D16
    ->
Risk
    ->
CAS
    ->
Terminal Result

This module does NOT own:
    - D6 formulas
    - D13 decision formula
    - EQE calculation
    - Risk calculations
    - CAS gate logic
    - broker execution
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.application.robomlm_application import get_application
from schemas.market.market_snapshot_pydantic import MarketSnapshotModel

try:
    from app.application.robomlm_application import (
        get_application,
    )
except Exception:
    get_application = None


LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix="/terminal",
    tags=["terminal"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class TerminalRequest(BaseModel):
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    timeframe: str = Field(
        default="1m",
        min_length=1,
        max_length=20,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class TerminalAnalysisRequest(BaseModel):
    symbol: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    timeframe: str = Field(
        default="1m",
        min_length=1,
        max_length=20,
    )


# ============================================================
# APPLICATION ACCESS
# ============================================================

def _application():
    """
    Resolve the single application facade.

    No backend engine is instantiated here.
    """

    if get_application is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "APPLICATION_SERVICE_UNAVAILABLE",
                "message": (
                    "ROBOMLM application service "
                    "could not be imported."
                ),
            },
        )

    try:
        return get_application()
    except Exception as exc:
        LOGGER.exception(
            "Unable to resolve ROBOMLM application"
        )

        raise HTTPException(
            status_code=503,
            detail={
                "error": "APPLICATION_SERVICE_UNAVAILABLE",
                "message": str(exc),
            },
        )


# ============================================================
# RESPONSE HELPERS
# ============================================================

def _status_from_result(
    result: Any,
) -> str:

    if not isinstance(
        result,
        dict,
    ):
        return "READY"

    if result.get(
        "status"
    ):
        return str(
            result["status"]
        )

    if result.get(
        "error"
    ):
        return "ERROR"

    return "READY"


def _normalise_terminal_result(
    result: Any,
) -> dict:

    if not isinstance(
        result,
        dict,
    ):
        return {
            "status": "READY",
            "result": result,
        }

    return result


# ============================================================
# TERMINAL MAIN PIPELINE
# ============================================================

@router.post(
    "",
    summary="Run ROBOMLM Terminal pipeline",
)
def terminal(
    request: TerminalRequest,
):
    """
    Run the existing Terminal application pipeline.

    No execution is requested by this endpoint.

    Expected logical chain:

        DATA
          ->
        EVIDENCE
          ->
        CONTEXT
          ->
        INTELLIGENCE
          ->
        DECISION
          ->
        RISK
          ->
        CAS
          ->
        RESULT
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=request.symbol,
            timeframe=request.timeframe,
            metadata=request.metadata,
        )

        result = _normalise_terminal_result(
            result
        )

        result.setdefault(
            "status",
            _status_from_result(
                result
            ),
        )

        result.setdefault(
            "symbol",
            request.symbol,
        )

        result.setdefault(
            "timeframe",
            request.timeframe,
        )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Terminal pipeline failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TERMINAL_PIPELINE_FAILED",
                "message": str(exc),
                "symbol": request.symbol,
                "timeframe": request.timeframe,
            },
        )


# ============================================================
# TERMINAL GET
# ============================================================

@router.get(
    "",
    summary="Read ROBOMLM Terminal pipeline",
)
def terminal_get(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    GET-compatible Terminal endpoint for the existing
    frontend.

    It uses the same application owner as POST.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        result = _normalise_terminal_result(
            result
        )

        result.setdefault(
            "symbol",
            symbol,
        )

        result.setdefault(
            "timeframe",
            timeframe,
        )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Terminal GET failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TERMINAL_PIPELINE_FAILED",
                "message": str(exc),
                "symbol": symbol,
                "timeframe": timeframe,
            },
        )


# ============================================================
# EVIDENCE
# ============================================================

@router.get(
    "/evidence",
    summary="Terminal evidence",
)
def terminal_evidence(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Return Evidence stage from the existing application
    pipeline.

    Evidence is not invented here.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        pipeline = (
            result.get(
                "pipeline",
                {}
            )
            if isinstance(
                result,
                dict,
            )
            else {}
        )

        evidence = pipeline.get(
            "evidence"
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "stage": "EVIDENCE",
            "data": evidence,
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal evidence failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "EVIDENCE_PIPELINE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# INTELLIGENCE
# ============================================================

@router.get(
    "/intelligence",
    summary="Terminal intelligence",
)
def terminal_intelligence(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Return Intelligence stage.

    Existing intelligence engines remain authoritative.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        pipeline = (
            result.get(
                "pipeline",
                {}
            )
            if isinstance(
                result,
                dict,
            )
            else {}
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "stage": "INTELLIGENCE",
            "data": pipeline.get(
                "intelligence"
            ),
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal intelligence failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTELLIGENCE_PIPELINE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# DECISION
# ============================================================

@router.get(
    "/decision",
    summary="Terminal decision",
)
def terminal_decision(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Return Decision stage.

    D1-D16 remain existing backend owners.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        pipeline = (
            result.get(
                "pipeline",
                {}
            )
            if isinstance(
                result,
                dict,
            )
            else {}
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "stage": "DECISION",
            "data": pipeline.get(
                "decision"
            ),
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal decision failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "DECISION_PIPELINE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# RISK
# ============================================================

@router.get(
    "/risk",
    summary="Terminal risk",
)
def terminal_risk(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Return Risk stage.

    Risk is evaluated after Decision.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        pipeline = (
            result.get(
                "pipeline",
                {}
            )
            if isinstance(
                result,
                dict,
            )
            else {}
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "stage": "RISK",
            "data": pipeline.get(
                "risk"
            ),
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal risk failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "RISK_PIPELINE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# CAS
# ============================================================

@router.get(
    "/cas",
    summary="Terminal CAS",
)
def terminal_cas(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Return CAS authorization state.

    CAS remains the final authorization owner.

    This endpoint DOES NOT execute an order.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={},
        )

        pipeline = (
            result.get(
                "pipeline",
                {}
            )
            if isinstance(
                result,
                dict,
            )
            else {}
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "stage": "CAS",
            "data": pipeline.get(
                "cas"
            ),
            "execution": {
                "invoked": False,
                "order_created": False,
            },
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal CAS failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "CAS_PIPELINE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# COMPLETE PIPELINE
# ============================================================

@router.get(
    "/pipeline",
    summary="Complete Terminal pipeline",
)
def terminal_pipeline(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Complete frontend-readable pipeline.

    This is the main endpoint for the Terminal page when the
    frontend needs all backend stages at once.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={
                "request_surface": "TERMINAL",
            },
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "pipeline": (
                result.get(
                    "pipeline",
                    {},
                )
                if isinstance(
                    result,
                    dict,
                )
                else {}
            ),
            "execution": (
                result.get(
                    "execution",
                    {},
                )
                if isinstance(
                    result,
                    dict,
                )
                else {
                    "invoked": False,
                }
            ),
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal complete pipeline failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "TERMINAL_COMPLETE_PIPELINE_FAILED"
                ),
                "message": str(exc),
                "symbol": symbol,
                "timeframe": timeframe,
            },
        )


# ============================================================
# D1-D16 VISIBILITY
# ============================================================

@router.get(
    "/decision-layers",
    summary="D1-D16 decision layer visibility",
)
def terminal_decision_layers(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
):
    """
    Expose D1-D16 as a frontend visibility contract.

    This endpoint does not recalculate the D layers.
    """

    app = _application()

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata={
                "request_surface": (
                    "TERMINAL_DECISION_LAYERS"
                ),
            },
        )

        decision = {}

        if isinstance(
            result,
            dict,
        ):
            pipeline = result.get(
                "pipeline",
                {},
            )

            decision = pipeline.get(
                "decision",
                {}
            )

        layers = []

        if isinstance(
            decision,
            dict,
        ):
            raw_result = decision.get(
                "result"
            )

            if isinstance(
                raw_result,
                dict,
            ):
                for key, value in (
                    raw_result.items()
                ):
                    key_text = str(
                        key
                    ).upper()

                    if (
                        key_text.startswith(
                            "D"
                        )
                        or "DECISION" in key_text
                        or "LAYER" in key_text
                    ):
                        layers.append({
                            "name": key,
                            "value": value,
                        })

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "layers": layers,
            "source": decision,
            "authority": (
                "EXISTING_D1_D16_BACKEND"
            ),
        }

    except Exception as exc:
        LOGGER.exception(
            "Decision layer visibility failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "DECISION_LAYER_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# BACKEND HEALTH
# ============================================================

@router.get(
    "/health",
    summary="Terminal backend health",
)
def terminal_health():
    """
    Terminal-specific backend health.
    """

    app = _application()

    try:
        health = app.health()

        domains = (
            health.get(
                "domains",
                {},
            )
            if isinstance(
                health,
                dict,
            )
            else {}
        )

        terminal_domains = {}

        for name in (
            "market",
            "evidence",
            "intelligence",
            "decision",
            "risk",
            "cas",
        ):
            if name in domains:
                terminal_domains[
                    name
                ] = domains[
                    name
                ]

        return {
            "status": "READY",
            "terminal": terminal_domains,
        }

    except Exception as exc:
        LOGGER.exception(
            "Terminal health failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TERMINAL_HEALTH_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# ROUTER EXPORT
# ============================================================

terminal_router = router
# ============================================================
# TERMINAL FRONTEND CONTRACT BRIDGE
# ============================================================
#
# Purpose:
#   Convert the EXISTING Terminal application result into the
#   canonical frontend contract already owned by
#   app/terminal/terminal_service.py.
#
# This layer does NOT:
#   - calculate D6
#   - calculate EQE
#   - make a D13 decision
#   - calculate Risk
#   - authorize CAS
#   - place orders
#   - execute broker actions
#
# Ownership remains:
#   TerminalService -> backend terminal contract
#   Terminal API    -> HTTP/API boundary
#   Frontend        -> presentation only
# ============================================================

def _terminal_frontend_contract(
    result: Any,
    *,
    symbol: str,
    timeframe: str,
    market: str = "",
    instrument: str = "",
) -> dict[str, Any]:
    """
    Adapt an existing Terminal application result to the
    TerminalService frontend contract.

    The adapter is intentionally conservative:
    missing backend sections remain missing instead of being
    fabricated by the API layer.
    """

    try:
        from app.terminal.terminal_service import (
            build_terminal_frontend_ui_payload,
        )
    except Exception:
        LOGGER.exception(
            "Terminal frontend contract unavailable"
        )

        # Do not manufacture terminal intelligence if the
        # canonical service contract cannot be imported.
        return {
            "status": "DEGRADED",
            "symbol": symbol,
            "timeframe": timeframe,
            "context": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market": market,
                "instrument": instrument,
            },
            "result": result,
            "authority": {
                "frontend_is_authority": False,
                "frontend_can_decide": False,
                "frontend_can_authorize": False,
                "frontend_can_execute": False,
            },
            "contract_error": (
                "TERMINAL_FRONTEND_CONTRACT_UNAVAILABLE"
            ),
        }

    try:
        payload = build_terminal_frontend_ui_payload(
            result=result,
            symbol=symbol,
            timeframe=timeframe,
            market=market,
            instrument=instrument,
        )

        if isinstance(payload, dict):
            return payload

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,
            "context": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market": market,
                "instrument": instrument,
            },
            "result": payload,
            "authority": {
                "frontend_is_authority": False,
                "frontend_can_decide": False,
                "frontend_can_authorize": False,
                "frontend_can_execute": False,
            },
        }

    except Exception:
        LOGGER.exception(
            "Terminal frontend contract construction failed"
        )

        # Preserve the actual backend result. Never replace
        # backend output with synthetic values.
        return {
            "status": "DEGRADED",
            "symbol": symbol,
            "timeframe": timeframe,
            "context": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market": market,
                "instrument": instrument,
            },
            "result": result,
            "authority": {
                "frontend_is_authority": False,
                "frontend_can_decide": False,
                "frontend_can_authorize": False,
                "frontend_can_execute": False,
            },
            "contract_error": (
                "TERMINAL_FRONTEND_CONTRACT_BUILD_FAILED"
            ),
        }


# ============================================================
# TERMINAL FRONTEND GET CONTRACT
# ============================================================

@router.get(
    "/frontend",
    summary="Get Terminal frontend contract",
)
def terminal_frontend(
    symbol: str = Query(
        ...,
        min_length=1,
        max_length=100,
    ),
    timeframe: str = Query(
        default="1m",
        min_length=1,
        max_length=20,
    ),
    market: str = Query(
        default="",
        max_length=50,
    ),
    instrument: str = Query(
        default="",
        max_length=100,
    ),
):
    """
    Return the existing Terminal backend result through the
    canonical Terminal frontend contract.

    This endpoint is READ/ANALYSIS only.

    It cannot:
        - place orders
        - authorize trades
        - bypass Risk
        - bypass CAS
        - alter D13
        - alter D6
    """

    app = _application()

    metadata: dict[str, Any] = {
        "source": "terminal_frontend",
        "market": market,
        "instrument": instrument,
    }

    try:
        result = app.terminal(
            symbol=symbol,
            timeframe=timeframe,
            metadata=metadata,
        )

        result = _normalise_terminal_result(
            result
        )

        payload = _terminal_frontend_contract(
            result,
            symbol=symbol,
            timeframe=timeframe,
            market=market,
            instrument=instrument,
        )

        return payload

    except HTTPException:
        raise

    except Exception as exc:
        LOGGER.exception(
            "Terminal frontend pipeline failed"
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "TERMINAL_FRONTEND_PIPELINE_FAILED",
                "message": str(exc),
                "symbol": symbol,
                "timeframe": timeframe,
            },
        )
@router.get("/market-data", tags=["terminal"])
def terminal_market_data(
    symbol: str = "BTCUSDT",
) -> dict:
    application = get_application()

    snapshot, health = (
        application.market_data_service
        .get_snapshot_with_health(symbol)
    )

    return {
        "status": "READY" if health.usable else "DEGRADED",
        "symbol": snapshot.instrument.symbol,
        "market_snapshot": MarketSnapshotModel.from_domain(snapshot).to_dict(),
        "market_data_health": health.to_dict(),
    }

# ============================================================
# TERMINAL FRONTEND CONTRACT MAP
# ============================================================

@router.get(
    "/frontend/map",
    summary="Get Terminal frontend selector map",
)
def terminal_frontend_map():
    """
    Return the exact existing terminal.html selector map.

    This is metadata only. It does not calculate or modify
    any trading state.
    """

    try:
        from app.terminal.terminal_service import (
            get_terminal_frontend_ui_map,
        )

        return {
            "status": "READY",
            "contract": (
                "ROBOMLM-TERMINAL-UI-1.0"
            ),
            "map": get_terminal_frontend_ui_map(),
            "authority": {
                "frontend_is_authority": False,
                "frontend_can_decide": False,
                "frontend_can_authorize": False,
                "frontend_can_execute": False,
            },
        }

    except Exception:
        LOGGER.exception(
            "Unable to load Terminal frontend selector map"
        )

        raise HTTPException(
            status_code=503,
            detail={
                "error": (
                    "TERMINAL_FRONTEND_MAP_UNAVAILABLE"
                ),
            },
        )