"""
ROBOMLM_PLUS Terminal Package
=============================

Terminal presentation/application layer.

Architecture:

    Market Data
        ↓
    Evidence / Intelligence
        ↓
    Market Context
        ↓
    Decision / D13
        ↓
    Risk
        ↓
    CAS
        ↓
    Terminal Components
        ↓
    Terminal Service
        ↓
    Terminal UI

Authority Boundary
------------------
The terminal package is a presentation and application-orchestration
surface.

It consumes upstream authoritative outputs but does not replace them.

Terminal MUST NOT:
    - generate market data
    - generate evidence
    - generate intelligence
    - generate market context intelligence
    - generate decisions
    - mutate D13
    - generate or override risk
    - generate or override CAS
    - execute orders
    - mutate positions
    - mutate upstream intelligence state
"""

from __future__ import annotations


# ============================================================================
# PACKAGE METADATA
# ============================================================================

TERMINAL_PACKAGE_NAME = "ROBOMLM_PLUS_TERMINAL"
TERMINAL_PACKAGE_VERSION = "1.0"
TERMINAL_PACKAGE_LAYER = "PRESENTATION_APPLICATION"
TERMINAL_PACKAGE_STATUS = "ACTIVE"


# ============================================================================
# PACKAGE ARCHITECTURE
# ============================================================================

TERMINAL_COMPONENTS = (
    "market_context",
    "evidence_strip",
    "intelligence_panel",
    "decision_outlook",
    "risk_panel",
    "cas_status",
    "terminal_service",
)

TERMINAL_COMPONENT_MODULES = {
    "market_context": "app.terminal.market_context",
    "evidence_strip": "app.terminal.evidence_strip",
    "intelligence_panel": "app.terminal.intelligence_panel",
    "decision_outlook": "app.terminal.decision_outlook",
    "risk_panel": "app.terminal.risk_panel",
    "cas_status": "app.terminal.cas_status",
    "terminal_service": "app.terminal.terminal_service",
}


# ============================================================================
# TERMINAL FLOW
# ============================================================================

TERMINAL_FLOW = (
    "market_context",
    "evidence_strip",
    "intelligence_panel",
    "decision_outlook",
    "risk_panel",
    "cas_status",
    "terminal_service",
)

TERMINAL_FLOW_DESCRIPTION = (
    "Market Context → Evidence Strip → Intelligence Panel → "
    "Decision Outlook → Risk Panel → CAS Status → Terminal Service"
)


# ============================================================================
# AUTHORITY BOUNDARY
# ============================================================================

TERMINAL_PACKAGE_AUTHORITY = {
    # Allowed
    "presentation_authority": True,
    "terminal_orchestration_authority": True,
    "terminal_aggregation_authority": True,
    "terminal_resolution_authority": True,

    # Forbidden
    "market_data_authority": False,
    "evidence_generation_authority": False,
    "intelligence_generation_authority": False,
    "market_context_generation_authority": False,
    "decision_generation_authority": False,
    "d13_authority": False,
    "d13_mutation": False,
    "risk_generation_authority": False,
    "risk_override": False,
    "cas_generation_authority": False,
    "cas_override": False,
    "execution_authority": False,
    "order_authority": False,
    "position_authority": False,
    "upstream_mutation_authority": False,
}


# ============================================================================
# SAFETY INVARIANTS
# ============================================================================

TERMINAL_SAFETY_INVARIANTS = {
    "preserve_d13_authority": True,
    "preserve_risk_authority": True,
    "preserve_cas_authority": True,
    "no_intelligence_generation": True,
    "no_decision_generation": True,
    "no_d13_mutation": True,
    "no_risk_override": True,
    "no_cas_override": True,
    "no_execution": True,
    "no_order_creation": True,
    "no_position_mutation": True,
    "no_upstream_mutation": True,
}


# ============================================================================
# PUBLIC MODULE IMPORTS
# ============================================================================

from .market_context import (
    TERMINAL_MARKET_CONTEXT_ENGINE,
    TERMINAL_MARKET_CONTEXT_VERSION,
    TerminalMarketContextStatus,
    TerminalMarketContextMode,
    TerminalMarketContextPriority,
    TerminalMarketContextContractStatus,
    TerminalMarketContextDataState,
    TerminalMarketContextConsistency,
    TerminalMarketContextReadiness,
    TerminalMarketContextDecision,
    TerminalMarketContextResolutionStatus,
    TerminalMarketContextRequest,
    TerminalMarketContextReference,
    TerminalMarketContextContractValidation,
    TerminalMarketContextRequirements,
    TerminalMarketContextAssessment,
    TerminalMarketContextResolutionRules,
    TerminalMarketContextPresentation,
    TerminalMarketContextResult,
    TerminalMarketContextSourceMap,
    TerminalMarketContextRegistryEntry,
    TerminalMarketContextRegistrySnapshot,
    TerminalMarketContextServiceResult,
    get_terminal_market_context_service,
    resolve_terminal_market_context,
    get_terminal_market_context_reference,
    terminal_market_context_snapshot,
    terminal_market_context_count,
    terminal_market_context_health,
    terminal_market_context_integrity,
    terminal_market_context_operational_check,
    terminal_market_context_service_info,
)


from .evidence_strip import (
    EVIDENCE_STRIP_ENGINE,
    EVIDENCE_STRIP_VERSION,
    EvidenceStripStatus,
    EvidenceStripMode,
    EvidenceStripPriority,
    EvidenceStripSeverity,
    EvidenceStripSourceType,
    EvidenceStripContractStatus,
    EvidenceStripDataState,
    EvidenceStripConsistency,
    EvidenceStripReadiness,
    EvidenceStripDecision,
    EvidenceStripResolutionStatus,
    EvidenceStripRequest,
    EvidenceStripItem,
    EvidenceStripReference,
    EvidenceStripContractValidation,
    EvidenceStripRequirements,
    EvidenceStripAssessment,
    EvidenceStripResolutionRules,
    EvidenceStripPresentation,
    EvidenceStripResult,
    EvidenceStripSourceMap,
    EvidenceStripRegistryEntry,
    EvidenceStripRegistrySnapshot,
    EvidenceStripServiceResult,
    get_evidence_strip_service,
    resolve_terminal_evidence_strip,
    get_terminal_evidence_strip_reference,
    terminal_evidence_strip_snapshot,
    terminal_evidence_strip_count,
    terminal_evidence_strip_health,
    terminal_evidence_strip_integrity,
    terminal_evidence_strip_operational_check,
    terminal_evidence_strip_service_info,
)


from .intelligence_panel import (
    INTELLIGENCE_PANEL_ENGINE,
    INTELLIGENCE_PANEL_VERSION,
    IntelligencePanelStatus,
    IntelligencePanelMode,
    IntelligencePanelPriority,
    IntelligencePanelSeverity,
    IntelligencePanelSourceType,
    IntelligencePanelContractStatus,
    IntelligencePanelCategory,
    IntelligencePanelDataState,
    IntelligencePanelConsistency,
    IntelligencePanelReadiness,
    IntelligencePanelDecision,
    IntelligencePanelResolutionStatus,
    IntelligencePanelRequest,
    IntelligencePanelItem,
    IntelligencePanelReference,
    IntelligencePanelContractValidation,
    IntelligencePanelRequirements,
    IntelligencePanelAssessment,
    IntelligencePanelResolutionRules,
    IntelligencePanelPresentation,
    IntelligencePanelResult,
    IntelligencePanelSourceMap,
    IntelligencePanelRegistryEntry,
    IntelligencePanelRegistrySnapshot,
    IntelligencePanelServiceResult,
    get_intelligence_panel_service,
    resolve_terminal_intelligence_panel,
    get_terminal_intelligence_panel_reference,
    terminal_intelligence_panel_snapshot,
    terminal_intelligence_panel_count,
    terminal_intelligence_panel_health,
    terminal_intelligence_panel_integrity,
    terminal_intelligence_panel_operational_check,
    terminal_intelligence_panel_service_info,
)


from .decision_outlook import (
    DECISION_OUTLOOK_ENGINE,
    DECISION_OUTLOOK_VERSION,
    DecisionOutlookStatus,
    DecisionOutlookMode,
    DecisionOutlookPriority,
    DecisionOutlookSeverity,
    DecisionOutlookSourceType,
    DecisionOutlookContractStatus,
    DecisionOutlookDirection,
    DecisionOutlookAction,
    DecisionOutlookCategory,
    DecisionOutlookDataState,
    DecisionOutlookConsistency,
    DecisionOutlookReadiness,
    DecisionOutlookDecision,
    DecisionOutlookResolutionStatus,
    DecisionOutlookRequest,
    DecisionOutlookItem,
    DecisionOutlookReference,
    DecisionOutlookContractValidation,
    DecisionOutlookRequirements,
    DecisionOutlookAssessment,
    DecisionOutlookResolutionRules,
    DecisionOutlookPresentation,
    DecisionOutlookResult,
    DecisionOutlookSourceMap,
    DecisionOutlookRegistryEntry,
    DecisionOutlookRegistrySnapshot,
    DecisionOutlookServiceResult,
    get_decision_outlook_service,
    resolve_terminal_decision_outlook,
    get_terminal_decision_outlook_reference,
    terminal_decision_outlook_snapshot,
    terminal_decision_outlook_count,
    terminal_decision_outlook_health,
    terminal_decision_outlook_integrity,
    terminal_decision_outlook_operational_check,
    terminal_decision_outlook_service_info,
)


from .risk_panel import (
    RISK_PANEL_ENGINE,
    RISK_PANEL_VERSION,
    RiskPanelStatus,
    RiskPanelMode,
    RiskPanelPriority,
    RiskPanelSeverity,
    RiskPanelSourceType,
    RiskPanelContractStatus,
    RiskPanelCategory,
    RiskPanelRiskLevel,
    RiskPanelDataState,
    RiskPanelConsistency,
    RiskPanelReadiness,
    RiskPanelDecision,
    RiskPanelResolutionStatus,
    RiskPanelRequest,
    RiskPanelItem,
    RiskPanelReference,
    RiskPanelContractValidation,
    RiskPanelRequirements,
    RiskPanelAssessment,
    RiskPanelResolutionRules,
    RiskPanelPresentation,
    RiskPanelResult,
    RiskPanelSourceMap,
    RiskPanelRegistryEntry,
    RiskPanelRegistrySnapshot,
    RiskPanelServiceResult,
    get_risk_panel_service,
    resolve_terminal_risk_panel,
    get_terminal_risk_panel_reference,
    terminal_risk_panel_snapshot,
    terminal_risk_panel_count,
    terminal_risk_panel_health,
    terminal_risk_panel_integrity,
    terminal_risk_panel_operational_check,
    terminal_risk_panel_service_info,
)


from .cas_status import (
    CAS_STATUS_ENGINE,
    CAS_STATUS_VERSION,
    CASStatus,
    CASMode,
    CASPriority,
    CASSeverity,
    CASSourceType,
    CASContractStatus,
    CASCategory,
    CASGateState,
    CASDecision,
    CASDataState,
    CASConsistency,
    CASReadiness,
    CASResolutionStatus,
    CASStatusRequest,
    CASGateItem,
    CASStatusReference,
    CASContractValidation,
    CASStatusRequirements,
    CASStatusAssessment,
    CASResolutionRules,
    CASStatusPresentation,
    CASStatusResult,
    CASStatusSourceMap,
    CASStatusRegistryEntry,
    CASStatusRegistrySnapshot,
    CASStatusServiceResult,
    get_cas_status_service,
    resolve_terminal_cas_status,
    get_terminal_cas_status_reference,
    terminal_cas_status_snapshot,
    terminal_cas_status_count,
    terminal_cas_status_health,
    terminal_cas_status_integrity,
    terminal_cas_status_operational_check,
    terminal_cas_status_service_info,
)


from .terminal_service import (
    TERMINAL_SERVICE_ENGINE,
    TERMINAL_SERVICE_VERSION,
    TerminalServiceStatus,
    TerminalServiceMode,
    TerminalServicePriority,
    TerminalServiceSeverity,
    TerminalServiceContractStatus,
    TerminalServiceDataState,
    TerminalServiceConsistency,
    TerminalServiceReadiness,
    TerminalServiceDecision,
    TerminalServiceResolutionStatus,
    TerminalServiceRequest,
    TerminalComponentReference,
    TerminalServiceContractValidation,
    TerminalComponentSnapshot,
    TerminalServiceRequirements,
    TerminalServiceAssessment,
    TerminalServiceResolutionRules,
    TerminalServicePresentation,
    TerminalServiceResult,
    TerminalServiceSourceMap,
    TerminalServiceRegistryEntry,
    TerminalServiceRegistrySnapshot,
    TerminalServiceExecutionResult,
    get_terminal_service,
    resolve_terminal,
    get_terminal_reference,
    terminal_service_snapshot,
    terminal_service_count,
    terminal_service_health,
    terminal_service_integrity,
    terminal_service_operational_check,
    terminal_service_info,
)


# ============================================================================
# PACKAGE HEALTH
# ============================================================================

def terminal_package_info() -> dict:
    """
    Return immutable-style package metadata for diagnostics and introspection.
    """
    return {
        "package": TERMINAL_PACKAGE_NAME,
        "version": TERMINAL_PACKAGE_VERSION,
        "layer": TERMINAL_PACKAGE_LAYER,
        "status": TERMINAL_PACKAGE_STATUS,
        "components": list(TERMINAL_COMPONENTS),
        "flow": list(TERMINAL_FLOW),
        "authority": dict(TERMINAL_PACKAGE_AUTHORITY),
        "safety_invariants": dict(TERMINAL_SAFETY_INVARIANTS),
    }


def terminal_package_operational_check() -> dict:
    """
    Lightweight package-level operational check.

    This check verifies package identity and exported component availability.
    It does not generate intelligence, make decisions, modify D13, calculate
    risk, evaluate CAS, or execute anything.
    """
    required_modules = set(TERMINAL_COMPONENTS)
    registered_modules = set(TERMINAL_COMPONENT_MODULES)

    missing_modules = sorted(required_modules - registered_modules)

    authority_violations = [
        key
        for key, value in TERMINAL_PACKAGE_AUTHORITY.items()
        if key.endswith("_authority")
        and key not in {
            "presentation_authority",
            "terminal_orchestration_authority",
            "terminal_aggregation_authority",
            "terminal_resolution_authority",
        }
        and value is True
    ]

    return {
        "operational": not missing_modules and not authority_violations,
        "package": TERMINAL_PACKAGE_NAME,
        "version": TERMINAL_PACKAGE_VERSION,
        "missing_modules": missing_modules,
        "authority_violations": authority_violations,
        "component_count": len(TERMINAL_COMPONENTS),
        "flow_valid": TERMINAL_FLOW == TERMINAL_COMPONENTS,
    }


# ============================================================================
# PUBLIC EXPORTS
# ============================================================================

__all__ = [
    # Package metadata
    "TERMINAL_PACKAGE_NAME",
    "TERMINAL_PACKAGE_VERSION",
    "TERMINAL_PACKAGE_LAYER",
    "TERMINAL_PACKAGE_STATUS",

    # Architecture
    "TERMINAL_COMPONENTS",
    "TERMINAL_COMPONENT_MODULES",
    "TERMINAL_FLOW",
    "TERMINAL_FLOW_DESCRIPTION",
    "TERMINAL_PACKAGE_AUTHORITY",
    "TERMINAL_SAFETY_INVARIANTS",

    # Package diagnostics
    "terminal_package_info",
    "terminal_package_operational_check",

    # Market Context
    "TERMINAL_MARKET_CONTEXT_ENGINE",
    "TERMINAL_MARKET_CONTEXT_VERSION",
    "TerminalMarketContextStatus",
    "TerminalMarketContextMode",
    "TerminalMarketContextPriority",
    "TerminalMarketContextContractStatus",
    "TerminalMarketContextDataState",
    "TerminalMarketContextConsistency",
    "TerminalMarketContextReadiness",
    "TerminalMarketContextDecision",
    "TerminalMarketContextResolutionStatus",
    "TerminalMarketContextRequest",
    "TerminalMarketContextReference",
    "TerminalMarketContextContractValidation",
    "TerminalMarketContextRequirements",
    "TerminalMarketContextAssessment",
    "TerminalMarketContextResolutionRules",
    "TerminalMarketContextPresentation",
    "TerminalMarketContextResult",
    "TerminalMarketContextSourceMap",
    "TerminalMarketContextRegistryEntry",
    "TerminalMarketContextRegistrySnapshot",
    "TerminalMarketContextServiceResult",
    "get_terminal_market_context_service",
    "resolve_terminal_market_context",
    "get_terminal_market_context_reference",
    "terminal_market_context_snapshot",
    "terminal_market_context_count",
    "terminal_market_context_health",
    "terminal_market_context_integrity",
    "terminal_market_context_operational_check",
    "terminal_market_context_service_info",

    # Evidence Strip
    "EVIDENCE_STRIP_ENGINE",
    "EVIDENCE_STRIP_VERSION",
    "EvidenceStripStatus",
    "EvidenceStripMode",
    "EvidenceStripPriority",
    "EvidenceStripSeverity",
    "EvidenceStripSourceType",
    "EvidenceStripContractStatus",
    "EvidenceStripDataState",
    "EvidenceStripConsistency",
    "EvidenceStripReadiness",
    "EvidenceStripDecision",
    "EvidenceStripResolutionStatus",
    "EvidenceStripRequest",
    "EvidenceStripItem",
    "EvidenceStripReference",
    "EvidenceStripContractValidation",
    "EvidenceStripRequirements",
    "EvidenceStripAssessment",
    "EvidenceStripResolutionRules",
    "EvidenceStripPresentation",
    "EvidenceStripResult",
    "EvidenceStripSourceMap",
    "EvidenceStripRegistryEntry",
    "EvidenceStripRegistrySnapshot",
    "EvidenceStripServiceResult",
    "get_evidence_strip_service",
    "resolve_terminal_evidence_strip",
    "get_terminal_evidence_strip_reference",
    "terminal_evidence_strip_snapshot",
    "terminal_evidence_strip_count",
    "terminal_evidence_strip_health",
    "terminal_evidence_strip_integrity",
    "terminal_evidence_strip_operational_check",
    "terminal_evidence_strip_service_info",

    # Intelligence Panel
    "INTELLIGENCE_PANEL_ENGINE",
    "INTELLIGENCE_PANEL_VERSION",
    "IntelligencePanelStatus",
    "IntelligencePanelMode",
    "IntelligencePanelPriority",
    "IntelligencePanelSeverity",
    "IntelligencePanelSourceType",
    "IntelligencePanelContractStatus",
    "IntelligencePanelCategory",
    "IntelligencePanelDataState",
    "IntelligencePanelConsistency",
    "IntelligencePanelReadiness",
    "IntelligencePanelDecision",
    "IntelligencePanelResolutionStatus",
    "IntelligencePanelRequest",
    "IntelligencePanelItem",
    "IntelligencePanelReference",
    "IntelligencePanelContractValidation",
    "IntelligencePanelRequirements",
    "IntelligencePanelAssessment",
    "IntelligencePanelResolutionRules",
    "IntelligencePanelPresentation",
    "IntelligencePanelResult",
    "IntelligencePanelSourceMap",
    "IntelligencePanelRegistryEntry",
    "IntelligencePanelRegistrySnapshot",
    "IntelligencePanelServiceResult",
    "get_intelligence_panel_service",
    "resolve_terminal_intelligence_panel",
    "get_terminal_intelligence_panel_reference",
    "terminal_intelligence_panel_snapshot",
    "terminal_intelligence_panel_count",
    "terminal_intelligence_panel_health",
    "terminal_intelligence_panel_integrity",
    "terminal_intelligence_panel_operational_check",
    "terminal_intelligence_panel_service_info",

    # Decision Outlook
    "DECISION_OUTLOOK_ENGINE",
    "DECISION_OUTLOOK_VERSION",
    "DecisionOutlookStatus",
    "DecisionOutlookMode",
    "DecisionOutlookPriority",
    "DecisionOutlookSeverity",
    "DecisionOutlookSourceType",
    "DecisionOutlookContractStatus",
    "DecisionOutlookDirection",
    "DecisionOutlookAction",
    "DecisionOutlookCategory",
    "DecisionOutlookDataState",
    "DecisionOutlookConsistency",
    "DecisionOutlookReadiness",
    "DecisionOutlookDecision",
    "DecisionOutlookResolutionStatus",
    "DecisionOutlookRequest",
    "DecisionOutlookItem",
    "DecisionOutlookReference",
    "DecisionOutlookContractValidation",
    "DecisionOutlookRequirements",
    "DecisionOutlookAssessment",
    "DecisionOutlookResolutionRules",
    "DecisionOutlookPresentation",
    "DecisionOutlookResult",
    "DecisionOutlookSourceMap",
    "DecisionOutlookRegistryEntry",
    "DecisionOutlookRegistrySnapshot",
    "DecisionOutlookServiceResult",
    "get_decision_outlook_service",
    "resolve_terminal_decision_outlook",
    "get_terminal_decision_outlook_reference",
    "terminal_decision_outlook_snapshot",
    "terminal_decision_outlook_count",
    "terminal_decision_outlook_health",
    "terminal_decision_outlook_integrity",
    "terminal_decision_outlook_operational_check",
    "terminal_decision_outlook_service_info",

    # Risk Panel
    "RISK_PANEL_ENGINE",
    "RISK_PANEL_VERSION",
    "RiskPanelStatus",
    "RiskPanelMode",
    "RiskPanelPriority",
    "RiskPanelSeverity",
    "RiskPanelSourceType",
    "RiskPanelContractStatus",
    "RiskPanelCategory",
    "RiskPanelRiskLevel",
    "RiskPanelDataState",
    "RiskPanelConsistency",
    "RiskPanelReadiness",
    "RiskPanelDecision",
    "RiskPanelResolutionStatus",
    "RiskPanelRequest",
    "RiskPanelItem",
    "RiskPanelReference",
    "RiskPanelContractValidation",
    "RiskPanelRequirements",
    "RiskPanelAssessment",
    "RiskPanelResolutionRules",
    "RiskPanelPresentation",
    "RiskPanelResult",
    "RiskPanelSourceMap",
    "RiskPanelRegistryEntry",
    "RiskPanelRegistrySnapshot",
    "RiskPanelServiceResult",
    "get_risk_panel_service",
    "resolve_terminal_risk_panel",
    "get_terminal_risk_panel_reference",
    "terminal_risk_panel_snapshot",
    "terminal_risk_panel_count",
    "terminal_risk_panel_health",
    "terminal_risk_panel_integrity",
    "terminal_risk_panel_operational_check",
    "terminal_risk_panel_service_info",

    # CAS Status
    "CAS_STATUS_ENGINE",
    "CAS_STATUS_VERSION",
    "CASStatus",
    "CASMode",
    "CASPriority",
    "CASSeverity",
    "CASSourceType",
    "CASContractStatus",
    "CASCategory",
    "CASGateState",
    "CASDecision",
    "CASDataState",
    "CASConsistency",
    "CASReadiness",
    "CASResolutionStatus",
    "CASStatusRequest",
    "CASGateItem",
    "CASStatusReference",
    "CASContractValidation",
    "CASStatusRequirements",
    "CASStatusAssessment",
    "CASResolutionRules",
    "CASStatusPresentation",
    "CASStatusResult",
    "CASStatusSourceMap",
    "CASStatusRegistryEntry",
    "CASStatusRegistrySnapshot",
    "CASStatusServiceResult",
    "get_cas_status_service",
    "resolve_terminal_cas_status",
    "get_terminal_cas_status_reference",
    "terminal_cas_status_snapshot",
    "terminal_cas_status_count",
    "terminal_cas_status_health",
    "terminal_cas_status_integrity",
    "terminal_cas_status_operational_check",
    "terminal_cas_status_service_info",

    # Terminal Service
    "TERMINAL_SERVICE_ENGINE",
    "TERMINAL_SERVICE_VERSION",
    "TerminalServiceStatus",
    "TerminalServiceMode",
    "TerminalServicePriority",
    "TerminalServiceSeverity",
    "TerminalServiceContractStatus",
    "TerminalServiceDataState",
    "TerminalServiceConsistency",
    "TerminalServiceReadiness",
    "TerminalServiceDecision",
    "TerminalServiceResolutionStatus",
    "TerminalServiceRequest",
    "TerminalComponentReference",
    "TerminalServiceContractValidation",
    "TerminalComponentSnapshot",
    "TerminalServiceRequirements",
    "TerminalServiceAssessment",
    "TerminalServiceResolutionRules",
    "TerminalServicePresentation",
    "TerminalServiceResult",
    "TerminalServiceSourceMap",
    "TerminalServiceRegistryEntry",
    "TerminalServiceRegistrySnapshot",
    "TerminalServiceExecutionResult",
    "get_terminal_service",
    "resolve_terminal",
    "get_terminal_reference",
    "terminal_service_snapshot",
    "terminal_service_count",
    "terminal_service_health",
    "terminal_service_integrity",
    "terminal_service_operational_check",
    "terminal_service_info",
]