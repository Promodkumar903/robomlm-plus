from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.intelligence.opportunity.universe_seed import (
    get_universe_seed,
)


# ============================================================
# ROUTER
# ============================================================

discovery_router = APIRouter(
    prefix="/discovery",
    tags=["discovery"],
)

# main.py compatibility
router = discovery_router


# ============================================================
# DISCOVERY BACKEND REGISTRY
# ============================================================

DISCOVERY_BACKEND: Dict[str, str] = {
    "universe": "app.intelligence.opportunity.universe_engine",
    "liquidity": "app.intelligence.opportunity.liquidity_filter",
    "risk": "app.intelligence.opportunity.risk_filter",
    "timing": "app.intelligence.opportunity.timing_engine",
    "scanner": "app.intelligence.opportunity.scanner_engine",
    "ranking": "app.intelligence.opportunity.ranking_engine",
    "top10": "app.intelligence.opportunity.top10_engine",
    "opportunity": "app.intelligence.opportunity.opportunity_engine",
    "explainer": "app.intelligence.opportunity.opportunity_explainer",
    "intraday": "app.intelligence.opportunity.intraday_engine",
    "favorites": "app.intelligence.opportunity.favorites_engine",
}


# ============================================================
# SAFETY CONTRACT
# ============================================================

DISCOVERY_CONTRACT: Dict[str, Any] = {
    "surface": "DISCOVERY",
    "purpose": (
        "Identify, filter and rank backend-provided candidates "
        "for deeper inspection."
    ),
    "allows": [
        "candidate identification",
        "candidate filtering",
        "candidate ranking",
        "opportunity identification",
        "asset inspection",
    ],
    "forbids": [
        "buy instruction",
        "sell instruction",
        "trade execution",
        "order creation",
        "execution routing",
        "CAS bypass",
        "risk-control bypass",
        "D13 replacement",
    ],
    "execution": False,
    "d13_replacement": False,
}


PIPELINE_ORDER = [
    "universe",
    "liquidity",
    "risk",
    "timing",
    "scanner",
    "ranking",
    "top10",
]


# ============================================================
# REQUEST MODELS
# ============================================================

class DiscoveryRequest(BaseModel):
    market: Optional[str] = None
    instrument: Optional[str] = None
    universe: Optional[str] = None
    timeframe: str = "1h"
    limit: int = Field(default=10, ge=1, le=500)
    filters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FavoriteRequest(BaseModel):
    symbol: str
    market: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================
# SAFE SERIALIZATION
# ============================================================

def _json_safe(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(key): _json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            _json_safe(item)
            for item in value
        ]

    if hasattr(value, "model_dump"):
        try:
            return _json_safe(
                value.model_dump()
            )
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return _json_safe(
                value.dict()
            )
        except Exception:
            pass

    if hasattr(value, "__dataclass_fields__"):
        try:
            from dataclasses import asdict

            return _json_safe(
                asdict(value)
            )
        except Exception:
            pass

    if hasattr(value, "__dict__"):
        try:
            return _json_safe(
                vars(value)
            )
        except Exception:
            pass

    return str(value)


def _status(value: Any) -> str:
    safe = _json_safe(value)

    if isinstance(safe, dict):
        status = safe.get("status")

        if status is not None:
            return str(status).upper()

    return "COMPLETE"


# ============================================================
# GENERIC DATA EXTRACTION
# ============================================================

_CANDIDATE_KEYS = (
    "candidates",
    "opportunities",
    "items",
    "results",
    "assets",
    "instruments",
    "snapshots",
    "ranked",
    "top10",
    "top_10",
    "accepted",
    "selected",
)


def _looks_like_candidate(value: Any) -> bool:
    safe = _json_safe(value)

    if not isinstance(safe, dict):
        return False

    candidate_keys = {
        "symbol",
        "ticker",
        "instrument",
        "instrument_id",
        "asset",
        "asset_id",
        "market",
        "market_id",
    }

    return bool(
        candidate_keys.intersection(
            safe.keys()
        )
    )


def _extract_candidates(
    value: Any,
    *,
    max_items: int = 500,
) -> List[Any]:
    """
    Recursively extracts real candidate-like records from
    backend results.

    No candidate is created here.
    """

    safe = _json_safe(value)

    found: List[Any] = []
    seen: set[str] = set()

    def add_candidate(item: Any) -> None:
        if len(found) >= max_items:
            return

        normalized = _json_safe(item)

        if not isinstance(normalized, dict):
            return

        # Flatten nested metadata fields to top level so downstream
        # engines can find lqs / eqe / risk_score / timestamps etc.
        meta = normalized.get("metadata")
        if isinstance(meta, dict):
            for key, value in meta.items():
                if key not in normalized:
                    normalized[key] = value

        if not _looks_like_candidate(normalized):
            return

        identity = (
            str(normalized.get("symbol"))
            + "|"
            + str(normalized.get("instrument"))
            + "|"
            + str(normalized.get("instrument_id"))
            + "|"
            + str(normalized.get("asset"))
        )

        if identity in seen:
            return

        seen.add(identity)
        found.append(normalized)

    def walk(node: Any) -> None:
        if len(found) >= max_items:
            return

        if isinstance(node, list):
            for item in node:
                if len(found) >= max_items:
                    break
                walk(item)
            return

        if isinstance(node, dict):
            # First inspect explicit candidate containers.
            for key in _CANDIDATE_KEYS:
                if key in node:
                    container = node.get(key)

                    if isinstance(
                        container,
                        (list, tuple, set),
                    ):
                        for item in container:
                            add_candidate(item)

                    elif isinstance(container, dict):
                        add_candidate(container)
                        walk(container)

            # Then inspect the current dictionary itself.
            add_candidate(node)

            # Finally recurse into nested result/data structures.
            for key, child in node.items():
                if key in _CANDIDATE_KEYS:
                    continue

                if isinstance(
                    child,
                    (dict, list, tuple, set),
                ):
                    walk(child)

    walk(safe)

    return found[:max_items]


def _merge_candidates(
    *sources: Any,
    limit: int = 500,
) -> List[Any]:
    merged: List[Any] = []
    seen: set[str] = set()

    for source in sources:
        for candidate in _extract_candidates(
            source,
            max_items=limit,
        ):
            candidate = _json_safe(candidate)

            identity = (
                str(candidate.get("symbol"))
                + "|"
                + str(candidate.get("instrument"))
                + "|"
                + str(candidate.get("instrument_id"))
                + "|"
                + str(candidate.get("asset"))
            )

            if identity in seen:
                continue

            seen.add(identity)
            merged.append(candidate)

            if len(merged) >= limit:
                return merged

    return merged

def _enrich_candidates(
    final_candidates: List[Any],
    rich_source: List[Any],
) -> List[Any]:
    """
    Merge field values from `rich_source` into `final_candidates`
    without overwriting non-empty final values.
    """
    lookup: Dict[str, Dict[str, Any]] = {}
    for item in rich_source or []:
        if not isinstance(item, dict):
            continue
        for key in ("instrument_id", "symbol"):
            k = str(item.get(key) or "").strip()
            if k:
                lookup.setdefault(k, item)

    enriched: List[Any] = []
    for cand in final_candidates or []:
        if not isinstance(cand, dict):
            enriched.append(cand)
            continue
        merged = dict(cand)
        for key in ("instrument_id", "symbol"):
            k = str(merged.get(key) or "").strip()
            if not k:
                continue
            rich = lookup.get(k)
            if not rich:
                continue
            for rk, rv in rich.items():
                if rk == "metadata":
                    continue
                if rk not in merged or merged[rk] in (None, ""):
                    merged[rk] = rv
            break
        enriched.append(merged)
    return enriched


# ============================================================
# APPLICATION DISCOVERY
# ============================================================

def _application_discovery(
    request: DiscoveryRequest,
) -> Dict[str, Any]:
    """
    Existing RobomlmApplication.discovery() remains the
    authoritative opportunity source.

    This function does not manufacture candidates.
    """

    try:
        from app.application.robomlm_application import (
            get_application,
        )
    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
        }

    try:
        application = get_application()

        discovery_method = getattr(
            application,
            "discovery",
            None,
        )

        if not callable(discovery_method):
            return {
                "status": "NOT_EXPOSED",
                "message": (
                    "RobomlmApplication.discovery() "
                    "is not available."
                ),
            }

        minimum_grade = request.metadata.get(
            "minimum_grade",
            "B",
        )

        result = discovery_method(
            symbol=request.metadata.get("symbol"),
            market=request.market,
            timeframe=request.timeframe,
            minimum_grade=minimum_grade,
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
        }


# ============================================================
# UNIVERSE
# ============================================================

def _run_universe(
    request: DiscoveryRequest,
    seed_candidates: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["universe"]
        )

        build_universe = getattr(
            module,
            "build_universe",
        )

        # Incoming candidates from the application flow
        incoming = list(seed_candidates or [])

        # Canonical market-appropriate seed universe
        seed = get_universe_seed(
            market=request.market,
            venue=(request.metadata or {}).get("venue"),
            timeframe=request.timeframe,
        )

        # Point-in-time timestamp for ranking eligibility.
        now_iso = datetime.now(timezone.utc).isoformat()
        for item in seed:
            if isinstance(item, dict):
                item.setdefault("timestamp", now_iso)

        # Prefer valid incoming candidates, then append seed.
        incoming_valid = [
            item for item in incoming
            if isinstance(item, dict)
            and str(item.get("symbol") or "").strip()
        ]

        if incoming_valid:
            instruments = incoming_valid + seed
        else:
            instruments = seed

        result = build_universe(
            instruments,
            market_id=request.market,
            as_of=datetime.now(timezone.utc),
            source="ROBOMLM_PLUS_DISCOVERY",
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "universe",
            "error": str(exc),
        }


# ============================================================
# LIQUIDITY
# ============================================================

def _run_liquidity(
    request: DiscoveryRequest,
    snapshots: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["liquidity"]
        )

        filter_liquidity = getattr(
            module,
            "filter_liquidity",
        )

        result = filter_liquidity(
            list(snapshots),
            market_id=request.market,
            as_of=datetime.now(
                timezone.utc
            ).isoformat(),
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "liquidity",
            "error": str(exc),
        }


# ============================================================
# RISK
# ============================================================

def _run_risk(
    request: DiscoveryRequest,
    snapshots: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["risk"]
        )

        risk_filter_class = getattr(
            module,
            "RiskFilter",
        )

        engine = risk_filter_class()

        result = engine.filter(
            list(snapshots),
            expected_market_id=request.market,
            now=datetime.now(
                timezone.utc
            ),
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "risk",
            "error": str(exc),
        }


# ============================================================
# TIMING
# ============================================================

def _run_timing(
    request: DiscoveryRequest,
    snapshots: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["timing"]
        )

        filter_timing = getattr(
            module,
            "filter_timing",
        )

        result = filter_timing(
            list(snapshots),
            expected_market_id=request.market,
            now=datetime.now(
                timezone.utc
            ),
            include_review=True,
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "timing",
            "error": str(exc),
        }


# ============================================================
# SCANNER
# ============================================================

def _run_scanner(
    request: DiscoveryRequest,
    candidates: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["scanner"]
        )

        factory = getattr(
            module,
            "create_scanner_engine",
        )

        engine = factory()

        scan = getattr(
            engine,
            "scan",
        )

        # IMPORTANT:
        # candidates passed exactly once.
        result = scan(
            list(candidates)
        )

        result_contract = getattr(
            engine,
            "result_contract",
            None,
        )

        if callable(result_contract):
            result = result_contract(
                result
            )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "scanner",
            "engine": "ScannerEngine",
            "error": str(exc),
        }


# ============================================================
# RANKING
# ============================================================

def _run_ranking(
    request: DiscoveryRequest,
    snapshots: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["ranking"]
        )

        rank_opportunities = getattr(
            module,
            "rank_opportunities",
        )

        result = rank_opportunities(
            list(snapshots),
            market_id=request.market,
            now=datetime.now(
                timezone.utc
            ),
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "ranking",
            "error": str(exc),
        }


# ============================================================
# TOP 10
# ============================================================

def _run_top10(
    request: DiscoveryRequest,
    candidates: Iterable[Any],
) -> Dict[str, Any]:
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND["top10"]
        )

        factory = getattr(
            module,
            "create_topten_engine",
        )

        engine = factory(
            limit=request.limit
        )

        select = getattr(
            engine,
            "select",
        )

        result = select(
            list(candidates),
            limit=request.limit,
        )

        return {
            "status": _status(result),
            "data": _json_safe(result),
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "domain": "top10",
            "error": str(exc),
        }


# ============================================================
# STAGE RESPONSE
# ============================================================

def _stage_response(
    stage: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:
    response: Dict[str, Any] = {
        "stage": stage.upper(),
        "status": str(
            result.get(
                "status",
                "UNKNOWN",
            )
        ).upper(),
        "produces_trade_instruction": False,
    }

    if "data" in result:
        response["data"] = result["data"]

    if "error" in result:
        response["error"] = result["error"]

    if "message" in result:
        response["message"] = result["message"]

    if "domain" in result:
        response["domain"] = result["domain"]

    if "engine" in result:
        response["engine"] = result["engine"]

    return response


# ============================================================
# MAIN DISCOVERY PIPELINE
# ============================================================

def _run_discovery_pipeline(
    request: DiscoveryRequest,
) -> Dict[str, Any]:

    stages: List[Dict[str, Any]] = []

    # --------------------------------------------------------
    # 0. EXISTING AUTHORITATIVE APPLICATION FLOW
    # --------------------------------------------------------

    application_result = _application_discovery(
        request
    )

    application_data = (
        application_result.get("data")
    )

    # Real candidates may be nested inside universe/scanner/
    # opportunity result structures.
    application_candidates = _merge_candidates(
        application_data,
        limit=500,
    )

    # --------------------------------------------------------
    # 1. UNIVERSE
    # --------------------------------------------------------

    universe_result = _run_universe(
        request,
        application_candidates,
    )

    stages.append(
        _stage_response(
            "universe",
            universe_result,
        )
    )

    universe_data = universe_result.get(
        "data"
    )

    universe_candidates = _merge_candidates(
        universe_data,
        application_data,
        limit=500,
    )
    # Rich candidates used later for enrichment.
    universe_rich = list(universe_candidates)

    # If the authoritative application flow supplied real
    # candidates but Universe returned no candidate records,
    # preserve those real candidates rather than fabricating.
    current_candidates = (
        universe_candidates
        or application_candidates
    )

    # --------------------------------------------------------
    # 2. LIQUIDITY
    # --------------------------------------------------------

    liquidity_result = _run_liquidity(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "liquidity",
            liquidity_result,
        )
    )

    liquidity_data = liquidity_result.get(
        "data"
    )

    liquidity_candidates = _merge_candidates(
        liquidity_data,
        current_candidates,
        limit=500,
    )

    if liquidity_candidates:
        current_candidates = (
            liquidity_candidates
        )

    # --------------------------------------------------------
    # 3. RISK
    # --------------------------------------------------------

    risk_result = _run_risk(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "risk",
            risk_result,
        )
    )

    risk_data = risk_result.get(
        "data"
    )

    risk_candidates = _merge_candidates(
        risk_data,
        current_candidates,
        limit=500,
    )

    if risk_candidates:
        current_candidates = (
            risk_candidates
        )

    # --------------------------------------------------------
    # 4. TIMING
    # --------------------------------------------------------

    timing_result = _run_timing(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "timing",
            timing_result,
        )
    )

    timing_data = timing_result.get(
        "data"
    )

    timing_candidates = _merge_candidates(
        timing_data,
        current_candidates,
        limit=500,
    )

    if timing_candidates:
        current_candidates = (
            timing_candidates
        )

    # --------------------------------------------------------
    # 5. SCANNER
    # --------------------------------------------------------

    scanner_result = _run_scanner(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "scanner",
            scanner_result,
        )
    )

    scanner_data = scanner_result.get(
        "data"
    )

    scanner_candidates = _merge_candidates(
        scanner_data,
        limit=500,
    )

    if scanner_candidates:
        current_candidates = _enrich_candidates(
            scanner_candidates,
            universe_rich,
        )

    # --------------------------------------------------------
    # 6. RANKING
    # --------------------------------------------------------

    ranking_result = _run_ranking(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "ranking",
            ranking_result,
        )
    )

    ranking_data = ranking_result.get(
        "data"
    )

    ranking_candidates = _merge_candidates(
        ranking_data,
        current_candidates,
        limit=500,
    )

    if ranking_candidates:
        current_candidates = (
            ranking_candidates
        )

    # --------------------------------------------------------
    # 7. TOP 10
    # --------------------------------------------------------

    top10_result = _run_top10(
        request,
        current_candidates,
    )

    stages.append(
        _stage_response(
            "top10",
            top10_result,
        )
    )

    top10_data = top10_result.get(
        "data"
    )

    final_candidates = _merge_candidates(
        top10_data,
        limit=request.limit,
    )

    # If TopTenResult serializes differently, retain ranked
    # backend candidates. Still no synthetic data.
    if not final_candidates:
        final_candidates = current_candidates[
            : request.limit
        ]

    # Enrich final candidates with rich universe data so that
    # score / confidence / market / timestamp fields are preserved
    # even when downstream stages strip them.
    final_candidates = _enrich_candidates(
        final_candidates,
        universe_rich,
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    statuses = [
        str(
            stage.get(
                "status",
                "",
            )
        ).upper()
        for stage in stages
    ]

    if any(
        status == "ERROR"
        for status in statuses
    ):
        pipeline_status = "PARTIAL"

    elif any(
        status in {
            "NOT_EXPOSED",
            "NO_INPUT_DATA",
        }
        for status in statuses
    ):
        pipeline_status = "PARTIAL"

    elif final_candidates:
        pipeline_status = "READY"

    else:
        pipeline_status = "PARTIAL"

    if final_candidates:
        next_action = "OPEN_ASSET"
    else:
        next_action = "ADJUST_FILTERS"

    return {
        "status": pipeline_status,
        "surface": "DISCOVERY",
        "contract": DISCOVERY_CONTRACT,
        "pipeline_order": [
            stage.upper()
            for stage in PIPELINE_ORDER
        ],
        "stages": stages,
        "top10": _json_safe(
            final_candidates[
                : request.limit
            ]
        ),
        "count": len(
            final_candidates[
                : request.limit
            ]
        ),
        "next_action": next_action,
        "execution": {
            "allowed": False,
            "invoked": False,
            "reason": (
                "DISCOVERY_IDENTIFICATION_ONLY"
            ),
        },
        "decision_boundary": {
            "d13_replaced": False,
            "d13_invoked": False,
            "reason": (
                "Discovery does not replace, "
                "execute, or bypass the backend "
                "D13 decision boundary."
            ),
        },
    }


# ============================================================
# MAIN DISCOVERY GET
# ============================================================

@router.get("")
def discovery_get(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    universe: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        universe=universe,
        timeframe=timeframe,
        limit=limit,
    )

    try:
        return _run_discovery_pipeline(
            request
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "DISCOVERY_PIPELINE_FAILED"
                ),
                "message": str(exc),
            },
        )


# ============================================================
# MAIN DISCOVERY POST
# ============================================================

@router.post("")
def discovery_post(
    request: DiscoveryRequest,
):
    try:
        return _run_discovery_pipeline(
            request
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "DISCOVERY_PIPELINE_FAILED"
                ),
                "message": str(exc),
            },
        )


# ============================================================
# INDIVIDUAL STAGE ROUTES
# ============================================================

@router.get("/universe")
def discovery_universe(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_universe(
        request,
        [],
    )

    return _stage_response(
        "universe",
        result,
    )


@router.get("/liquidity")
def discovery_liquidity(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_liquidity(
        request,
        [],
    )

    return _stage_response(
        "liquidity",
        result,
    )


@router.get("/risk")
def discovery_risk(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_risk(
        request,
        [],
    )

    return _stage_response(
        "risk",
        result,
    )


@router.get("/timing")
def discovery_timing(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_timing(
        request,
        [],
    )

    return _stage_response(
        "timing",
        result,
    )


@router.get("/scanner")
def discovery_scanner(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_scanner(
        request,
        [],
    )

    return _stage_response(
        "scanner",
        result,
    )


@router.get("/ranking")
def discovery_ranking(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_ranking(
        request,
        [],
    )

    return _stage_response(
        "ranking",
        result,
    )


@router.get("/top10")
def discovery_top10(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    request = DiscoveryRequest(
        market=market,
        instrument=instrument,
        timeframe=timeframe,
        limit=limit,
    )

    result = _run_top10(
        request,
        [],
    )

    return _stage_response(
        "top10",
        result,
    )


# ============================================================
# OPPORTUNITY
# ============================================================

@router.get("/opportunity/{symbol}")
def discovery_opportunity(
    symbol: str,
):
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND[
                "opportunity"
            ]
        )

        # Try common explicit opportunity entrypoints.
        for name in (
            "discover",
            "get_opportunity",
            "explain",
            "run",
            "process",
        ):
            entrypoint = getattr(
                module,
                name,
                None,
            )

            if callable(entrypoint):
                try:
                    result = entrypoint(
                        symbol=symbol
                    )

                    return {
                        "status": _status(
                            result
                        ),
                        "symbol": symbol,
                        "data": _json_safe(
                            result
                        ),
                        "execution": False,
                        "d13_replacement": False,
                    }

                except TypeError:
                    continue

        return {
            "status": "NOT_EXPOSED",
            "symbol": symbol,
            "data": {
                "available_callables": [
                    name
                    for name in dir(module)
                    if not name.startswith("_")
                    and callable(
                        getattr(
                            module,
                            name,
                            None,
                        )
                    )
                ]
            },
            "execution": False,
            "d13_replacement": False,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "OPPORTUNITY_LOOKUP_FAILED"
                ),
                "message": str(exc),
            },
        )


# ============================================================
# INTRADAY
# ============================================================

@router.get("/intraday")
def discovery_intraday(
    market: Optional[str] = Query(
        default=None
    ),
    instrument: Optional[str] = Query(
        default=None
    ),
    timeframe: str = Query(
        default="1h"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
):
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND[
                "intraday"
            ]
        )

        for name in (
            "run",
            "discover",
            "process",
            "evaluate",
            "scan",
        ):
            entrypoint = getattr(
                module,
                name,
                None,
            )

            if callable(entrypoint):
                try:
                    result = entrypoint(
                        market=market,
                        instrument=instrument,
                        timeframe=timeframe,
                        limit=limit,
                    )

                    return {
                        "status": _status(
                            result
                        ),
                        "data": _json_safe(
                            result
                        ),
                        "execution": False,
                    }

                except TypeError:
                    continue

        return {
            "status": "NOT_EXPOSED",
            "data": {},
            "execution": False,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
            "execution": False,
        }


# ============================================================
# FAVORITES
# ============================================================

@router.get("/favorites")
def discovery_favorites():
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND[
                "favorites"
            ]
        )

        for name in (
            "list_favorites",
            "get_favorites",
            "favorites",
            "list",
            "get",
        ):
            entrypoint = getattr(
                module,
                name,
                None,
            )

            if callable(entrypoint):
                try:
                    result = entrypoint()

                    return {
                        "status": _status(
                            result
                        ),
                        "data": _json_safe(
                            result
                        ),
                        "execution": False,
                    }

                except TypeError:
                    continue

        return {
            "status": "NOT_EXPOSED",
            "data": {},
            "execution": False,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "error": str(exc),
            "execution": False,
        }


@router.post("/favorites")
def discovery_add_favorite(
    request: FavoriteRequest,
):
    try:
        module = importlib.import_module(
            DISCOVERY_BACKEND[
                "favorites"
            ]
        )

        for name in (
            "add_favorite",
            "save_favorite",
            "favorite",
            "add",
            "save",
        ):
            entrypoint = getattr(
                module,
                name,
                None,
            )

            if callable(entrypoint):
                try:
                    result = entrypoint(
                        symbol=request.symbol,
                        market=request.market,
                        metadata=request.metadata,
                    )

                    return {
                        "status": _status(
                            result
                        ),
                        "symbol": request.symbol,
                        "data": _json_safe(
                            result
                        ),
                        "execution": False,
                    }

                except TypeError:
                    continue

        return {
            "status": "NOT_EXPOSED",
            "symbol": request.symbol,
            "data": {},
            "execution": False,
        }

    except Exception as exc:
        return {
            "status": "ERROR",
            "symbol": request.symbol,
            "error": str(exc),
            "execution": False,
        }


# ============================================================
# BACKEND MAP
# ============================================================

@router.get("/backend-map")
def discovery_backend_map():
    result: Dict[str, Any] = {}

    for domain, module_path in (
        DISCOVERY_BACKEND.items()
    ):
        entry: Dict[str, Any] = {
            "module": module_path,
            "available": False,
            "callables": {},
        }

        try:
            module = importlib.import_module(
                module_path
            )

            entry["available"] = True

            entry["callables"] = {
                name: type(
                    getattr(
                        module,
                        name,
                    )
                ).__name__
                for name in dir(module)
                if not name.startswith("_")
                and callable(
                    getattr(
                        module,
                        name,
                        None,
                    )
                )
            }

        except Exception as exc:
            entry["error"] = str(exc)

        result[domain] = entry

    return {
        "status": "READY",
        "surface": "DISCOVERY",
        "backend": result,
        "pipeline_order": [
            stage.upper()
            for stage in PIPELINE_ORDER
        ],
        "execution": False,
        "d13_replacement": False,
    }


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def discovery_health():
    backend_count = 0
    backend_errors: Dict[str, str] = {}

    for domain, module_path in (
        DISCOVERY_BACKEND.items()
    ):
        try:
            importlib.import_module(
                module_path
            )

            backend_count += 1

        except Exception as exc:
            backend_errors[domain] = str(
                exc
            )

    return {
        "status": (
            "READY"
            if backend_count
            == len(DISCOVERY_BACKEND)
            else "PARTIAL"
        ),
        "surface": "DISCOVERY",
        "backend_modules": len(
            DISCOVERY_BACKEND
        ),
        "backend_modules_available": (
            backend_count
        ),
        "backend_errors": backend_errors,
        "execution": False,
        "d13_replacement": False,
    }
