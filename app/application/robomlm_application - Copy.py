"""
ROBOMLM_PLUS
Application Integration Layer

Purpose
-------
Connect the existing ROBOMLM_PLUS backend domains into one
frontend-consumable application service.

Architecture
------------
UI
  -> API
  -> RobomlmApplication
  -> Existing Backend Owners

Existing owners remain authoritative for:
    DATA
    DATA QUALITY
    EVIDENCE
    CONTEXT
    INTELLIGENCE
    DECISION D1-D16
    RISK
    CAS
    DISCOVERY / SCANNER
    BUYER
    PLUS
    AUTOROBOMLM
    MEMORY
    RESEARCH
    EXECUTION
    RECONCILIATION

This file MUST NOT:
    - duplicate D6 formulas
    - duplicate D13 decision logic
    - duplicate EQE
    - duplicate Risk formulas
    - duplicate CAS gates
    - create broker orders
    - bypass authorization
    - create fake market data
    - create fake evidence
    - turn scanner output into a Buy/Sell decision

This is an orchestration/application boundary only.
"""

from __future__ import annotations

import importlib
import inspect
import logging
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from app.markets.live_market_data_service import LiveMarketDataService
from app.providers.provider_bootstrap import build_provider_registry
from schemas.evidence.evidence_item import EvidenceItem
from schemas.market.market_snapshot_pydantic import MarketSnapshotModel


LOGGER = logging.getLogger(__name__)


# ============================================================
# EXISTING BACKEND OWNERS
# ============================================================

BACKEND_OWNERS = {
    "market": [
        "app.markets.market_service",
        "app.markets.market_session",
        "app.markets.market_state",
    ],

    "evidence": [
        "app.intelligence.evidence.evidence_orchestrator",
        "app.intelligence.evidence.evidence_package",
        "app.intelligence.evidence.evidence_normalizer",
    ],

    "intelligence": [
        "app.intelligence.intelligence_orchestrator",
        "app.intelligence.market_context",
        "app.intelligence.opportunity_intelligence",
        "app.intelligence.regime_intelligence",
        "app.intelligence.relationship_intelligence",
        "app.intelligence.strategy_intelligence",
        "app.intelligence.timing_intelligence",
        "app.intelligence.magnitude_engine",
        "app.intelligence.confidence_engine",
        "app.intelligence.commitment_engine",
    ],

    "decision": [
        "app.intelligence.decision_orchestrator",
        "app.intelligence.decision.decision_state",
        "app.intelligence.decision.decision_explainer",
        "app.intelligence.decision.1_Decision_Readiness",
        "app.intelligence.decision.2_decision_condition",
        "app.intelligence.decision.3_decision_confidence",
        "app.intelligence.decision.4_decision_relationships",
        "app.intelligence.decision.5_decision_structure",
        "app.intelligence.decision.6_decision_flow",
        "app.intelligence.decision.7_decision_liquidity_volatility",
        "app.intelligence.decision.8_decision_instrument_mechanics",
        "app.intelligence.decision.9_decision_time_event",
        "app.intelligence.decision.10_decision_market_state",
        "app.intelligence.decision.11_decision_transition",
        "app.intelligence.decision.12_decision_future_scenario",
        "app.intelligence.decision.13_decision_decision",
        "app.intelligence.decision.14_decision_validation",
        "app.intelligence.decision.15_decision_learning",
        "app.intelligence.decision.16_decision_intelligence",
    ],

    "risk": [
        "app.intelligence.cas.risk_gate",
        "app.intelligence.cas.exposure_gate",
        "app.intelligence.cas.position_gate",
    ],

    "cas": [
        "app.intelligence.cas.cas_orchestrator",
        "app.intelligence.cas.suitability_gate",
        "app.intelligence.cas.execution_safety_gate",
        "app.intelligence.cas.compliance_gate",
        "app.intelligence.cas.restriction_engine",
    ],

    "opportunity": [
        "app.intelligence.opportunity.universe_engine",
        "app.intelligence.opportunity.liquidity_filter",
        "app.intelligence.opportunity.risk_filter",
        "app.intelligence.opportunity.timing_engine",
        "app.intelligence.opportunity.intraday_engine",
        "app.intelligence.opportunity.scanner_engine",
        "app.intelligence.opportunity.ranking_engine",
        "app.intelligence.opportunity.top10_engine",
        "app.intelligence.opportunity.opportunity_engine",
        "app.intelligence.opportunity.opportunity_explainer",
        "app.intelligence.opportunity.favorites_engine",
    ],

    "memory": [
        "app.intelligence.memory.memory_service",
        "app.intelligence.memory.memory_retrieval",
        "app.intelligence.memory.decision_memory",
        "app.intelligence.memory.evidence_memory",
        "app.intelligence.memory.market_memory",
        "app.intelligence.memory.outcome_memory",
        "app.intelligence.memory.pattern_memory",
    ],

    "research": [
        "app.intelligence.research.research_service",
        "app.intelligence.research.candidate_manager",
        "app.intelligence.research.dataset",
        "app.intelligence.research.deployment_manager",
        "app.intelligence.research.experiment",
        "app.intelligence.research.hypothesis",
        "app.intelligence.research.stress_testing",
        "app.intelligence.research.validation",
        "app.intelligence.research.version_manager",
    ],

    "plus": [
        "app.intelligence.robomlm_plus.plus_orchestrator",
        "app.intelligence.robomlm_plus.advanced_decision",
        "app.intelligence.robomlm_plus.execution_preparation",
        "app.intelligence.robomlm_plus.position_monitor",
        "app.intelligence.robomlm_plus.protection",
        "app.intelligence.robomlm_plus.reconciliation",
        "app.intelligence.robomlm_plus.emergency_control",
        "app.intelligence.robomlm_plus.halt_controller",
    ],

    "autorobomlm": [
        "app.autorobimlm.automation_engine",
        "app.autorobimlm.mode_manager",
        "app.autorobimlm.strategy_runner",
        "app.autorobimlm.execution.order_manager",
        "app.autorobimlm.execution.execution_manager",
        "app.autorobimlm.kill_switch",
        "app.autorobimlm.reconciliation",
    ],
}


# ============================================================
# PIPELINE DEFINITION
# ============================================================

PIPELINE = (
    "DATA",
    "DATA_QUALITY",
    "EVIDENCE",
    "CONTEXT",
    "INTELLIGENCE",
    "DECISION",
    "RISK",
    "CAS",
    "ACTION",
    "EXECUTION",
    "RESULT",
    "MEMORY",
    "LEARNING",
)


# ============================================================
# SAFETY RULES
# ============================================================

SAFETY_RULES = {
    "scanner_is_discovery_only": True,
    "buyer_analysis_is_not_execution": True,
    "decision_before_risk": True,
    "risk_before_cas": True,
    "cas_before_authorized_action": True,
    "cas_bypass_allowed": False,
    "direct_broker_order_allowed": False,
    "fake_market_data_allowed": False,
    "fake_evidence_allowed": False,
    "duplicate_decision_formula_allowed": False,
    "duplicate_risk_formula_allowed": False,
    "duplicate_cas_formula_allowed": False,
}


# ============================================================
# RESULT UTILITIES
# ============================================================

def json_safe(value: Any) -> Any:
    """
    Convert backend objects into frontend-safe structures.

    No calculation or decision logic is performed here.
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return json_safe(value.to_dict())
        except Exception:
            pass

    if hasattr(value, "model_dump") and callable(value.model_dump):
        try:
            return json_safe(value.model_dump())
        except Exception:
            pass

    if hasattr(value, "dict") and callable(value.dict):
        try:
            return json_safe(value.dict())
        except Exception:
            pass

    if is_dataclass(value):
        try:
            return json_safe(asdict(value))
        except Exception:
            return str(value)

    if isinstance(value, Mapping):
        return {
            str(key): json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            json_safe(item)
            for item in value
        ]

    if hasattr(value, "__dict__"):
        try:
            return {
                str(key): json_safe(item)
                for key, item in vars(value).items()
                if not str(key).startswith("_")
            }
        except Exception:
            pass

    return str(value)


def _import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        LOGGER.debug(
            "Backend module unavailable: %s: %s",
            module_name,
            exc,
        )
        return None


def _public_callables(module):
    if module is None:
        return []

    output = []

    try:
        for name in dir(module):
            if name.startswith("_"):
                continue

            try:
                obj = getattr(module, name)
            except Exception:
                continue

            if callable(obj):
                output.append(name)

    except Exception:
        return []

    return sorted(set(output))


def _error_result(
    domain: str,
    error: str,
    *,
    module: str | None = None,
    function: str | None = None,
) -> dict:
    return {
        "available": False,
        "executed": False,
        "domain": domain,
        "module": module,
        "function": function,
        "arguments": [],
        "result": None,
        "error": error,
    }


# ============================================================
# APPLICATION SERVICE
# ============================================================

class RobomlmApplication:
    """
    Application-level facade.

    Existing backend owners remain authoritative.
    """

    VERSION = "ROBOMLM-APPLICATION-1.0"

    def __init__(
        self,
        backend_owners: dict | None = None,
    ):
        self.provider_registry = build_provider_registry()
        self.market_data_service = LiveMarketDataService()

        self.backend_owners = (
            backend_owners
            or BACKEND_OWNERS
        )

    # ========================================================
    # HEALTH
    # ========================================================

    def health(self) -> dict:
        domains = {}

        total = 0
        available = 0

        for domain, modules in self.backend_owners.items():
            domains[domain] = []

            for module_name in modules:
                total += 1

                module = _import(module_name)

                item = {
                    "module": module_name,
                    "available": module is not None,
                    "callables": (
                        _public_callables(module)
                        if module is not None
                        else []
                    ),
                }

                if item["available"]:
                    available += 1

                domains[domain].append(item)

        return {
            "status": (
                "READY"
                if available
                else "NO_BACKEND_AVAILABLE"
            ),
            "version": self.VERSION,
            "available": available,
            "checked": total,
            "domains": domains,
        }

    # ========================================================
    # MAP
    # ========================================================

    def backend_map(self) -> dict:
        return {
            "version": self.VERSION,
            "pipeline": list(PIPELINE),
            "owners": json_safe(self.backend_owners),
            "safety": json_safe(SAFETY_RULES),
        }

    # ========================================================
    # GENERIC ENTRYPOINT DISCOVERY
    # ========================================================

    def find_entrypoint(
        self,
        domain: str,
        preferred_names: tuple[str, ...] | None = None,
    ) -> dict:
        """
        Discover a module-level callable.

        This method is intentionally generic.

        Canonical class-based domains such as Intelligence,
        Decision, Risk and CAS are handled by their explicit
        adapters below rather than by guessing class methods.
        """

        preferred_names = (
            preferred_names
            or (
                "orchestrate",
                "orchestrate_evidence",
                "process",
                "analyze",
                "analyse",
                "evaluate",
                "run",
                "execute",
                "build",
                "get",
                "retrieve",
                "search",
            )
        )

        modules = self.backend_owners.get(domain, [])

        for module_name in modules:
            module = _import(module_name)

            if module is None:
                continue

            names = _public_callables(module)

            for preferred in preferred_names:
                if preferred in names:
                    return {
                        "available": True,
                        "domain": domain,
                        "module": module_name,
                        "function": preferred,
                    }

        return {
            "available": False,
            "domain": domain,
            "module": None,
            "function": None,
        }

    # ========================================================
    # GENERIC SAFE CALL
    # ========================================================

    def call_existing(
        self,
        domain: str,
        payload: dict | None = None,
        preferred_names: tuple[str, ...] | None = None,
    ) -> dict:
        """
        Invoke an existing module-level backend function.

        No positional guessing.
        No domain logic.
        """

        payload = payload or {}

        entry = self.find_entrypoint(
            domain=domain,
            preferred_names=preferred_names,
        )

        if not entry.get("available"):
            return _error_result(
                domain,
                "NO_EXISTING_ENTRYPOINT",
            )

        module = _import(entry["module"])

        if module is None:
            return _error_result(
                domain,
                "MODULE_IMPORT_FAILED",
                module=entry["module"],
                function=entry["function"],
            )

        fn = getattr(
            module,
            entry["function"],
            None,
        )

        if not callable(fn):
            return _error_result(
                domain,
                "ENTRYPOINT_NOT_CALLABLE",
                module=entry["module"],
                function=entry["function"],
            )

        try:
            signature = inspect.signature(fn)
        except Exception as exc:
            return _error_result(
                domain,
                "SIGNATURE_UNAVAILABLE:"
                + type(exc).__name__,
                module=entry["module"],
                function=entry["function"],
            )

        accepted = {}

        has_kwargs = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )

        if has_kwargs:
            accepted = dict(payload)
        else:
            for parameter in signature.parameters.values():
                if parameter.name in payload:
                    accepted[parameter.name] = payload[
                        parameter.name
                    ]

        try:
            result = fn(**accepted)

            return {
                "available": True,
                "executed": True,
                "domain": domain,
                "module": entry["module"],
                "function": entry["function"],
                "arguments": sorted(accepted.keys()),
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception(
                "Existing backend call failed: %s",
                entry,
            )

            return {
                "available": True,
                "executed": False,
                "domain": domain,
                "module": entry["module"],
                "function": entry["function"],
                "arguments": sorted(accepted.keys()),
                "result": None,
                "error": (
                    type(exc).__name__
                    + ":"
                    + str(exc)
                ),
            }

    # ========================================================
    # EVIDENCE
    # ========================================================

    def _run_evidence(
        self,
        payload: dict,
    ) -> dict:
        """
        Canonical evidence adapter.

        Uses the existing evidence orchestrator.
        """

        module_name = (
            "app.intelligence.evidence.evidence_orchestrator"
        )

        module = _import(module_name)

        if module is None:
            return _error_result(
                "evidence",
                "MODULE_IMPORT_FAILED",
                module=module_name,
                function="orchestrate_evidence",
            )

        fn = getattr(
            module,
            "orchestrate_evidence",
            None,
        )

        if not callable(fn):
            return _error_result(
                "evidence",
                "ENTRYPOINT_NOT_CALLABLE",
                module=module_name,
                function="orchestrate_evidence",
            )

        kwargs = {
            "evidence": payload.get(
                "evidence",
                (),
            ),
            "timeframe": payload.get(
                "timeframe"
            ),
            "metadata": payload.get(
                "metadata",
                {},
            ),
        }

        try:
            result = fn(**kwargs)

            return {
                "available": True,
                "executed": True,
                "domain": "evidence",
                "module": module_name,
                "function": "orchestrate_evidence",
                "arguments": sorted(
                    kwargs.keys()
                ),
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception(
                "Evidence orchestration failed"
            )

            return {
                "available": True,
                "executed": False,
                "domain": "evidence",
                "module": module_name,
                "function": "orchestrate_evidence",
                "arguments": sorted(
                    kwargs.keys()
                ),
                "result": None,
                "error": (
                    type(exc).__name__
                    + ":"
                    + str(exc)
                ),
            }

    # ========================================================
    # INTELLIGENCE
    # ========================================================

    def _run_intelligence(
        self,
        payload: dict,
    ) -> dict:
        """
        Canonical IntelligenceOrchestrator adapter.

        The existing IntelligenceOrchestrator remains the
        authoritative owner of intelligence logic.
        """
        module_name = "app.intelligence.intelligence_orchestrator"
        module = _import(module_name)

        if module is None:
            return _error_result(
                "intelligence",
                "MODULE_IMPORT_FAILED",
                module=module_name,
                function="IntelligenceOrchestrator",
            )

        orchestrator_cls = getattr(
            module,
            "IntelligenceOrchestrator",
            None,
        )
        request_cls = getattr(
            module,
            "IntelligenceRequest",
            None,
        )

        if orchestrator_cls is None:
            return _error_result(
                "intelligence",
                "ORCHESTRATOR_CLASS_NOT_FOUND",
                module=module_name,
                function="IntelligenceOrchestrator",
            )

        if request_cls is None:
            return _error_result(
                "intelligence",
                "REQUEST_CLASS_NOT_FOUND",
                module=module_name,
                function="IntelligenceRequest",
            )

        try:
            request = request_cls(
                symbol=str(payload.get("symbol", "UNKNOWN")),
                timeframe=str(payload.get("timeframe", "UNKNOWN")),
                data={
                    "market_snapshot": json_safe(
                        payload.get("market_snapshot")
                    ),
                    "market_data_health": json_safe(
                        payload.get("market_data_health")
                    ),
                },
                evidence=json_safe(
                    payload.get("evidence_result", {})
                ),
                context=json_safe(
                    payload.get("context", {})
                ),
                specialized=json_safe(
                    payload.get("specialized", {})
                ),
            )

            orchestrator = orchestrator_cls()
            analyze = getattr(
                orchestrator,
                "analyze",
                None,
            )

            if not callable(analyze):
                evaluate = getattr(
                    orchestrator,
                    "evaluate",
                    None,
                )
                if callable(evaluate):
                    analyze = evaluate

            if not callable(analyze):
                return _error_result(
                    "intelligence",
                    "ORCHESTRATOR_ANALYZE_NOT_FOUND",
                    module=module_name,
                    function="IntelligenceOrchestrator.analyze",
                )

            result = analyze(request)

            return {
                "available": True,
                "executed": True,
                "domain": "intelligence",
                "module": module_name,
                "function": "IntelligenceOrchestrator.analyze",
                "arguments": ["request"],
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception("Intelligence orchestration failed")
            return {
                "available": True,
                "executed": False,
                "domain": "intelligence",
                "module": module_name,
                "function": "IntelligenceOrchestrator.analyze",
                "arguments": ["request"],
                "result": None,
                "error": type(exc).__name__ + ":" + str(exc),
            }

    # ========================================================
    # DECISION
    # ========================================================

    def _run_decision(
        self,
        payload: dict,
    ) -> dict:
        """
        Canonical DecisionOrchestrator adapter.

        The existing D1-D16 decision system remains
        authoritative.
        """
        module_name = "app.intelligence.decision_orchestrator"
        module = _import(module_name)

        if module is None:
            return _error_result(
                "decision",
                "MODULE_IMPORT_FAILED",
                module=module_name,
                function="DecisionOrchestrator",
            )

        orchestrator_cls = getattr(
            module,
            "DecisionOrchestrator",
            None,
        )
        request_cls = getattr(
            module,
            "DecisionRequest",
            None,
        )

        if orchestrator_cls is None:
            return _error_result(
                "decision",
                "ORCHESTRATOR_CLASS_NOT_FOUND",
                module=module_name,
                function="DecisionOrchestrator",
            )

        if request_cls is None:
            return _error_result(
                "decision",
                "REQUEST_CLASS_NOT_FOUND",
                module=module_name,
                function="DecisionRequest",
            )

        try:
            intelligence_result = payload.get(
                "intelligence_result",
                {},
            )
            evidence_result = payload.get(
                "evidence_result",
                {},
            )

            direction = "HOLD"

            if isinstance(intelligence_result, Mapping):
                direction = str(
                    intelligence_result.get(
                        "directional_bias",
                        intelligence_result.get(
                            "direction",
                            intelligence_result.get(
                                "bias",
                                "HOLD",
                            ),
                        ),
                    )
                )

            request = request_cls(
                symbol=str(
                    payload.get(
                        "symbol",
                        "UNKNOWN",
                    )
                ),
                timeframe=str(
                    payload.get(
                        "timeframe",
                        "UNKNOWN",
                    )
                ),
                direction=direction,
                evidence_score=float(
                    self._extract_score(
                        intelligence_result,
                        (
                            "evidence_score",
                            "confidence_score",
                            "score",
                        ),
                    )
                ),
                confidence_score=float(
                    self._extract_score(
                        intelligence_result,
                        (
                            "confidence_score",
                            "confidence",
                        ),
                    )
                ),
                commitment_score=float(
                    self._extract_score(
                        intelligence_result,
                        (
                            "commitment_score",
                            "commitment",
                        ),
                    )
                ),
                context_score=float(
                    self._extract_score(
                        intelligence_result,
                        (
                            "context_score",
                            "context_alignment",
                        ),
                    )
                ),
                risk_score=float(
                    self._extract_score(
                        payload.get(
                            "risk_result",
                            {},
                        ),
                        (
                            "risk_score",
                            "score",
                        ),
                    )
                ),
                timing_score=float(
                    self._extract_score(
                        intelligence_result,
                        (
                            "timing_score",
                            "timing_quality",
                        ),
                    )
                ),
                metadata={
                    "application": self.VERSION,
                    "market_data_health": json_safe(
                        payload.get(
                            "market_data_health"
                        )
                    ),
                },
            )

            orchestrator = orchestrator_cls()
            decide = getattr(
                orchestrator,
                "decide",
                None,
            )

            if not callable(decide):
                evaluate = getattr(
                    orchestrator,
                    "evaluate",
                    None,
                )
                if callable(evaluate):
                    decide = evaluate

            if not callable(decide):
                return _error_result(
                    "decision",
                    "ORCHESTRATOR_DECIDE_NOT_FOUND",
                    module=module_name,
                    function="DecisionOrchestrator.decide",
                )

            result = decide(request)

            return {
                "available": True,
                "executed": True,
                "domain": "decision",
                "module": module_name,
                "function": "DecisionOrchestrator.decide",
                "arguments": ["request"],
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception("Decision orchestration failed")
            return {
                "available": True,
                "executed": False,
                "domain": "decision",
                "module": module_name,
                "function": "DecisionOrchestrator.decide",
                "arguments": ["request"],
                "result": None,
                "error": type(exc).__name__ + ":" + str(exc),
            }

    # ========================================================
    # SCORE EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_score(
        value: Any,
        names: tuple[str, ...],
    ) -> float:
        """
        Extract an already-existing backend score.

        This method NEVER calculates a score.
        Missing scores remain zero at the application
        boundary because the DecisionRequest schema requires
        numeric fields.
        """

        if value is None:
            return 0.0

        if isinstance(value, Mapping):
            for name in names:
                if name not in value:
                    continue

                candidate = value.get(name)

                if isinstance(
                    candidate,
                    (int, float),
                ):
                    return float(candidate)

                if isinstance(
                    candidate,
                    Mapping,
                ):
                    nested = RobomlmApplication._extract_score(
                        candidate,
                        names,
                    )

                    if nested != 0.0:
                        return nested

        return 0.0

    # ========================================================
    # RISK
    # ========================================================

    def _run_risk(
        self,
        payload: dict,
    ) -> dict:
        """
        Canonical Risk owner adapter.

        Uses existing evaluate_risk().
        No risk formula is implemented here.
        """

        module_name = (
            "app.intelligence.cas.risk_gate"
        )

        module = _import(module_name)

        if module is None:
            return _error_result(
                "risk",
                "MODULE_IMPORT_FAILED",
                module=module_name,
                function="evaluate_risk",
            )

        fn = getattr(
            module,
            "evaluate_risk",
            None,
        )

        if not callable(fn):
            return _error_result(
                "risk",
                "ENTRYPOINT_NOT_CALLABLE",
                module=module_name,
                function="evaluate_risk",
            )

        request = payload

        try:
            result = fn(
                request=request,
            )

            return {
                "available": True,
                "executed": True,
                "domain": "risk",
                "module": module_name,
                "function": "evaluate_risk",
                "arguments": [
                    "request"
                ],
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception(
                "Risk evaluation failed"
            )

            return {
                "available": True,
                "executed": False,
                "domain": "risk",
                "module": module_name,
                "function": "evaluate_risk",
                "arguments": [
                    "request"
                ],
                "result": None,
                "error": (
                    type(exc).__name__
                    + ":"
                    + str(exc)
                ),
            }

    # ========================================================
    # CAS
    # ========================================================

    def _run_cas(
        self,
        payload: dict,
    ) -> dict:
        """
        Canonical CAS owner adapter.

        Uses existing CASRequest + evaluate_cas().

        This method does NOT authorize execution by itself.
        It only invokes the existing CAS evaluation contract.
        """

        module_name = (
            "app.intelligence.cas.cas_orchestrator"
        )

        module = _import(module_name)

        if module is None:
            return _error_result(
                "cas",
                "MODULE_IMPORT_FAILED",
                module=module_name,
                function="evaluate_cas",
            )

        request_cls = getattr(
            module,
            "CASRequest",
            None,
        )

        evaluate_fn = getattr(
            module,
            "evaluate_cas",
            None,
        )

        if request_cls is None:
            return _error_result(
                "cas",
                "REQUEST_CLASS_NOT_FOUND",
                module=module_name,
                function="CASRequest",
            )

        if not callable(evaluate_fn):
            return _error_result(
                "cas",
                "ENTRYPOINT_NOT_CALLABLE",
                module=module_name,
                function="evaluate_cas",
            )

        try:
            decision_result = payload.get(
                "decision_result",
                {},
            )

            risk_result = payload.get(
                "risk_result",
                {},
            )

            decision_direction = "HOLD"
            decision_confidence = None

            if isinstance(
                decision_result,
                Mapping,
            ):
                decision_direction = str(
                    decision_result.get(
                        "direction",
                        decision_result.get(
                            "decision",
                            "HOLD",
                        ),
                    )
                )

                raw_confidence = decision_result.get(
                    "confidence"
                )

                if isinstance(
                    raw_confidence,
                    (int, float),
                ):
                    decision_confidence = float(
                        raw_confidence
                    )

            risk_status = None
            risk_decision = None
            risk_score = None
            risk_confidence = None

            if isinstance(
                risk_result,
                Mapping,
            ):
                risk_status = (
                    risk_result.get(
                        "status"
                    )
                )
                risk_decision = (
                    risk_result.get(
                        "decision"
                    )
                )

                raw_risk_score = (
                    risk_result.get(
                        "risk_score"
                    )
                )

                if isinstance(
                    raw_risk_score,
                    (int, float),
                ):
                    risk_score = float(
                        raw_risk_score
                    )

                raw_risk_confidence = (
                    risk_result.get(
                        "confidence"
                    )
                )

                if isinstance(
                    raw_risk_confidence,
                    (int, float),
                ):
                    risk_confidence = float(
                        raw_risk_confidence
                    )

            request = request_cls(
                market=(
                    payload.get(
                        "market"
                    )
                    or getattr(
                        payload.get(
                            "market_snapshot"
                        ),
                        "market",
                        None,
                    )
                ),
                instrument=str(
                    payload.get(
                        "symbol",
                        payload.get(
                            "instrument",
                            "",
                        ),
                    )
                ),
                timeframe=payload.get(
                    "timeframe"
                ),
                direction=decision_direction,
                decision_direction=decision_direction,
                decision_confidence=decision_confidence,
                risk_status=(
                    str(risk_status)
                    if risk_status is not None
                    else None
                ),
                risk_decision=(
                    str(risk_decision)
                    if risk_decision is not None
                    else None
                ),
                risk_score=risk_score,
                risk_confidence=risk_confidence,
                metadata={
                    "application": self.VERSION,
                    "terminal_analysis_only": True,
                },
            )

            result = evaluate_fn(
                request
            )

            return {
                "available": True,
                "executed": True,
                "domain": "cas",
                "module": module_name,
                "function": "evaluate_cas",
                "arguments": [
                    "request"
                ],
                "result": json_safe(result),
                "error": None,
            }

        except Exception as exc:
            LOGGER.exception(
                "CAS evaluation failed"
            )

            return {
                "available": True,
                "executed": False,
                "domain": "cas",
                "module": module_name,
                "function": "evaluate_cas",
                "arguments": [
                    "request"
                ],
                "result": None,
                "error": (
                    type(exc).__name__
                    + ":"
                    + str(exc)
                ),
            }

    # ========================================================
    # TERMINAL
    # ========================================================

    def terminal(
        self,
        symbol: str,
        timeframe: str = "1m",
        metadata: dict | None = None,
    ) -> dict:

        snapshot, market_data_health = (
            self.market_data_service.get_snapshot_with_health(
                symbol
            )
        )

        observed_at = (
            snapshot.observation.observed_at
        )

        market_evidence = [
            EvidenceItem(
                evidence_id=(
                    f"market-snapshot:"
                    f"{symbol}:"
                    f"{observed_at.isoformat()}"
                ),
                evidence_type="MARKET_SNAPSHOT",
                source="binance",
                value=(
                    MarketSnapshotModel
                    .from_domain(snapshot)
                    .to_dict()
                ),
                observed_at=observed_at,
                market=snapshot.market.market,
                instrument_id=snapshot.instrument.symbol,
                timeframe=timeframe,
                quality=(
                    "VALID"
                    if snapshot.data_quality.is_complete
                    else "DEGRADED"
                ),
                description=(
                    "Canonical market snapshot "
                    "received from provider adapter."
                ),
                metadata={
                    "provider": "binance",
                    "observation_kind": (
                        "PROVIDER_OBSERVED"
                    ),
                },
            )
        ]

        payload = {
            "symbol": symbol,
            "timeframe": timeframe,
            "metadata": metadata or {},
            "market_snapshot": snapshot,
            "market_data_health": (
                market_data_health.to_dict()
            ),
            "evidence": market_evidence,
            "market": snapshot.market.market,
            "instrument": snapshot.instrument.symbol,
            "context": {},
            "specialized": {},
        }

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        evidence = self._run_evidence(
            payload
        )

        # ----------------------------------------------------
        # INTELLIGENCE
        # ----------------------------------------------------

        intelligence_payload = dict(
            payload
        )

        intelligence_payload[
            "evidence_result"
        ] = evidence.get(
            "result"
        )

        intelligence = self._run_intelligence(
            intelligence_payload
        )

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        decision_payload = dict(
            intelligence_payload
        )

        decision_payload[
            "intelligence_result"
        ] = intelligence.get(
            "result"
        )

        decision = self._run_decision(
            decision_payload
        )

        # ----------------------------------------------------
        # RISK
        # ----------------------------------------------------

        risk_payload = dict(
            decision_payload
        )

        risk_payload[
            "decision_result"
        ] = decision.get(
            "result"
        )

        risk = self._run_risk(
            risk_payload
        )

        # ----------------------------------------------------
        # CAS
        # ----------------------------------------------------

        cas_payload = dict(
            risk_payload
        )

        cas_payload[
            "risk_result"
        ] = risk.get(
            "result"
        )

        cas = self._run_cas(
            cas_payload
        )

        # ----------------------------------------------------
        # FINAL APPLICATION RESULT
        # ----------------------------------------------------

        return {
            "status": "READY",
            "symbol": symbol,
            "timeframe": timeframe,

            "market": {
                "snapshot": json_safe(
                    MarketSnapshotModel
                    .from_domain(snapshot)
                    .to_dict()
                ),
                "health": json_safe(
                    market_data_health.to_dict()
                ),
            },

            "evidence": evidence,

            "pipeline": {
                "evidence": evidence,
                "intelligence": intelligence,
                "decision": decision,
                "risk": risk,
                "cas": cas,
            },

            "execution": {
                "authorized": False,
                "invoked": False,
                "reason": (
                    "TERMINAL_ANALYSIS_ONLY"
                ),
            },

            "safety": json_safe(
                SAFETY_RULES
            ),
        }

    # ========================================================
    # DISCOVERY
    # ========================================================

    def discovery(
        self,
        symbol: str | None = None,
        market: str | None = None,
        timeframe: str = "1m",
        minimum_grade: str = "B",
    ) -> dict:

        payload = {
            "symbol": symbol,
            "market": market,
            "timeframe": timeframe,
            "minimum_grade": minimum_grade,
        }

        universe = self.call_existing(
            "opportunity",
            payload,
            (
                "discover",
                "run",
                "process",
                "build",
            ),
        )

        scanner_payload = dict(payload)

        scanner_payload[
            "universe_result"
        ] = universe.get(
            "result"
        )

        scanner = self.call_existing(
            "opportunity",
            scanner_payload,
            (
                "scan",
                "run_scan",
                "discover",
                "process",
                "run",
            ),
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "market": market,
            "timeframe": timeframe,
            "minimum_grade": minimum_grade,
            "scanner": scanner,
            "universe": universe,
            "decision_boundary": (
                "DISCOVERY_ONLY"
            ),
        }

    # ========================================================
    # BUYER
    # ========================================================

    def buyer(
        self,
        symbol: str,
        market: str,
        instrument: str,
        contract: str,
        strategy: str,
        timeframe: str = "1m",
        mode: str = "ANALYSIS",
    ) -> dict:

        payload = {
            "symbol": symbol,
            "market": market,
            "instrument": instrument,
            "contract": contract,
            "strategy": strategy,
            "timeframe": timeframe,
            "mode": mode,
        }

        strategy_result = self.call_existing(
            "intelligence",
            payload,
            (
                "analyze",
                "analyse",
                "evaluate",
                "process",
                "run",
            ),
        )

        intelligence_payload = dict(
            payload
        )

        intelligence_payload[
            "strategy_result"
        ] = strategy_result.get(
            "result"
        )

        intelligence = self.call_existing(
            "intelligence",
            intelligence_payload,
            (
                "orchestrate",
                "analyze",
                "analyse",
                "process",
                "run",
            ),
        )

        decision_payload = dict(
            intelligence_payload
        )

        decision_payload[
            "intelligence_result"
        ] = intelligence.get(
            "result"
        )

        decision = self.call_existing(
            "decision",
            decision_payload,
            (
                "orchestrate",
                "evaluate",
                "process",
                "analyze",
                "analyse",
                "run",
            ),
        )

        risk_payload = dict(
            decision_payload
        )

        risk_payload[
            "decision_result"
        ] = decision.get(
            "result"
        )

        risk = self.call_existing(
            "risk",
            risk_payload,
            (
                "evaluate",
                "process",
                "check",
                "run",
            ),
        )

        cas_payload = dict(
            risk_payload
        )

        cas_payload[
            "risk_result"
        ] = risk.get(
            "result"
        )

        cas = self.call_existing(
            "cas",
            cas_payload,
            (
                "orchestrate",
                "authorize",
                "evaluate",
                "process",
                "run",
            ),
        )

        cas_result = cas.get(
            "result"
        )

        cas_allowed = False

        if isinstance(
            cas_result,
            Mapping,
        ):
            cas_allowed = bool(
                cas_result.get(
                    "allowed",
                    cas_result.get(
                        "approved",
                        False,
                    ),
                )
            )

        execution_requested = (
            str(mode).upper()
            in (
                "AUTHORIZED_EXECUTION",
                "EXECUTION",
                "LIVE",
                "DEMO",
                "PAPER",
            )
        )

        return {
            "status": "READY",
            "symbol": symbol,
            "selection": {
                "market": market,
                "instrument": instrument,
                "contract": contract,
                "strategy": strategy,
            },
            "mode": mode,
            "pipeline": {
                "strategy": strategy_result,
                "intelligence": intelligence,
                "decision": decision,
                "risk": risk,
                "cas": cas,
            },
            "authorization": {
                "cas_allowed": cas_allowed,
                "execution_requested": (
                    execution_requested
                ),
                "execution_invoked": False,
            },
            "safety": {
                "direct_execution": False,
                "cas_bypass": False,
            },
        }

    # ========================================================
    # MEMORY
    # ========================================================

    def memory(
        self,
        symbol: str | None = None,
        query: str | None = None,
        limit: int = 50,
    ) -> dict:

        payload = {
            "symbol": symbol,
            "query": query,
            "limit": limit,
        }

        result = self.call_existing(
            "memory",
            payload,
            (
                "retrieve",
                "search",
                "query",
                "get",
                "load",
                "read",
            ),
        )

        return {
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_MEMORY_ENGINE"
            ),
            "symbol": symbol,
            "query": query,
            "limit": limit,
            "result": result,
        }

    # ========================================================
    # RESEARCH
    # ========================================================

    def research(
        self,
        query: str | None = None,
        symbol: str | None = None,
        hypothesis: str | None = None,
    ) -> dict:

        payload = {
            "query": query,
            "symbol": symbol,
            "hypothesis": hypothesis,
        }

        result = self.call_existing(
            "research",
            payload,
            (
                "research",
                "run_research",
                "run",
                "process",
                "search",
            ),
        )

        return {
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_RESEARCH_ENGINE"
            ),
            "query": query,
            "symbol": symbol,
            "hypothesis": hypothesis,
            "result": result,
            "production_boundary": (
                "RESEARCH_CANNOT_DIRECTLY_MUTATE_PRODUCTION"
            ),
        }

    # ========================================================
    # AUTOMATION STATUS
    # ========================================================

    def automation_status(self) -> dict:

        result = self.call_existing(
            "autorobomlm",
            {
                "action": "status",
            },
            (
                "status",
                "get_status",
                "state",
            ),
        )

        return {
            "status": "READY",
            "automation": result,
            "execution_requires": [
                "DECISION",
                "RISK",
                "CAS",
                "AUTHORIZED_ACTION",
            ],
        }

    # ========================================================
    # BLACKBOX CONTRACT
    # ========================================================

    def blackbox_contract(self) -> dict:

        return {
            "status": "READY",
            "lifecycle": [
                "DATA",
                "EVIDENCE",
                "CONTEXT",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
                "ACTION",
                "EXECUTION",
                "RESULT",
            ],
            "learning": [
                "OUTCOME_MEMORY",
                "PATTERN_MEMORY",
                "D15_LEARNING",
                "D16_INTELLIGENCE",
            ],
        }


# ============================================================
# SINGLE APPLICATION INSTANCE
# ============================================================

robomlm_app = RobomlmApplication()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def get_application() -> RobomlmApplication:
    """
    Return the single application facade used by API/UI.
    """
    return robomlm_app


def backend_health() -> dict:
    return robomlm_app.health()


def backend_map() -> dict:
    return robomlm_app.backend_map()


def terminal(
    symbol: str,
    timeframe: str = "1m",
    metadata: dict | None = None,
) -> dict:
    return robomlm_app.terminal(
        symbol=symbol,
        timeframe=timeframe,
        metadata=metadata,
    )


def discovery(
    symbol: str | None = None,
    market: str | None = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
) -> dict:
    return robomlm_app.discovery(
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        minimum_grade=minimum_grade,
    )


def buyer(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
    mode: str = "ANALYSIS",
) -> dict:
    return robomlm_app.buyer(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode=mode,
    )


def memory(
    symbol: str | None = None,
    query: str | None = None,
    limit: int = 50,
) -> dict:
    return robomlm_app.memory(
        symbol=symbol,
        query=query,
        limit=limit,
    )


def research(
    query: str | None = None,
    symbol: str | None = None,
    hypothesis: str | None = None,
) -> dict:
    return robomlm_app.research(
        query=query,
        symbol=symbol,
        hypothesis=hypothesis,
    )


def automation_status() -> dict:
    return robomlm_app.automation_status()


def blackbox_contract() -> dict:
    return robomlm_app.blackbox_contract()