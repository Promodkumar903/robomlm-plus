# ============================================================
# ROBOMLM MEMORY INTELLIGENCE LAYER
# app/intelligence/memory/__init__.py
#
# Central public export surface for the complete Memory Layer.
# No trading decision logic is implemented here.
# ============================================================

from __future__ import annotations


# ------------------------------------------------------------
# MARKET MEMORY
# ------------------------------------------------------------

from .market_memory import (
    MARKET_MEMORY_ENGINE,
    MARKET_MEMORY_VERSION,
    MarketMemoryStatus,
    MarketMemoryType,
    MarketMemoryPriority,
    MarketMemorySourceType,
    MarketMemoryContractStatus,
    MarketMemoryDataState,
    MarketMemoryConsistency,
    MarketMemoryReadiness,
    MarketMemoryActionState,
    MarketMemoryContractState,
    MarketMemoryResultStatus,
    MarketMemoryRequest,
    MarketMemoryReference,
    MarketMemorySourceReference,
    MarketMemoryContractValidation,
    MarketMemoryRequirements,
    MarketMemoryAssessment,
    MarketMemoryAction,
    MarketMemoryResult,
    MarketMemoryContract,
    MarketMemoryEngine,
    evaluate_market_memory,
    analyze_market_memory,
    review_market_memory,
    validate_market_memory_request,
    validate_market_memory_result,
    validate_market_memory_contract,
    market_memory_ready,
    market_memory_can_advance,
)


# ------------------------------------------------------------
# EVIDENCE MEMORY
# ------------------------------------------------------------

from .evidence_memory import (
    EVIDENCE_MEMORY_ENGINE,
    EVIDENCE_MEMORY_VERSION,
    EvidenceMemoryStatus,
    EvidenceMemoryType,
    EvidenceMemoryPriority,
    EvidenceMemorySourceType,
    EvidenceMemoryQuality,
    EvidenceMemoryContractStatus,
    EvidenceMemoryDataState,
    EvidenceMemoryConsistency,
    EvidenceMemoryReadiness,
    EvidenceMemoryActionState,
    EvidenceMemoryContractState,
    EvidenceMemoryResultStatus,
    EvidenceMemoryRequest,
    EvidenceMemoryReference,
    EvidenceMemorySourceReference,
    EvidenceMemoryContractValidation,
    EvidenceMemoryRequirements,
    EvidenceMemoryAssessment,
    EvidenceMemoryAction,
    EvidenceMemoryResult,
    EvidenceMemoryContract,
    EvidenceMemoryEngine,
    evaluate_evidence_memory,
    analyze_evidence_memory,
    review_evidence_memory,
    validate_evidence_memory_request,
    validate_evidence_memory_result,
    validate_evidence_memory_contract,
    evidence_memory_ready,
    evidence_memory_can_advance,
)


# ------------------------------------------------------------
# DECISION MEMORY
# ------------------------------------------------------------

from .decision_memory import (
    DECISION_MEMORY_ENGINE,
    DECISION_MEMORY_VERSION,
    DecisionMemoryStatus,
    DecisionMemoryType,
    DecisionMemoryPriority,
    DecisionMemorySourceType,
    DecisionMemoryQuality,
    DecisionMemoryContractStatus,
    DecisionMemoryDataState,
    DecisionMemoryConsistency,
    DecisionMemoryReadiness,
    DecisionMemoryActionState,
    DecisionMemoryContractState,
    DecisionMemoryResultStatus,
    DecisionMemoryRequest,
    DecisionMemoryReference,
    DecisionMemorySourceReference,
    DecisionMemoryContractValidation,
    DecisionMemoryRequirements,
    DecisionMemoryAssessment,
    DecisionMemoryAction,
    DecisionMemoryResult,
    DecisionMemoryContract,
    DecisionMemoryEngine,
    evaluate_decision_memory,
    analyze_decision_memory,
    review_decision_memory,
    validate_decision_memory_request,
    validate_decision_memory_result,
    validate_decision_memory_contract,
    decision_memory_ready,
    decision_memory_can_advance,
)


# ------------------------------------------------------------
# OUTCOME MEMORY
# ------------------------------------------------------------

from .outcome_memory import (
    OUTCOME_MEMORY_ENGINE,
    OUTCOME_MEMORY_VERSION,
    OutcomeMemoryStatus,
    OutcomeMemoryType,
    OutcomeMemoryPriority,
    OutcomeMemorySourceType,
    OutcomeMemoryQuality,
    OutcomeMemoryContractStatus,
    OutcomeMemoryDataState,
    OutcomeMemoryConsistency,
    OutcomeMemoryReadiness,
    OutcomeMemoryActionState,
    OutcomeMemoryContractState,
    OutcomeMemoryResultStatus,
    OutcomeMemoryRequest,
    OutcomeMemoryReference,
    OutcomeMemorySourceReference,
    OutcomeMemoryContractValidation,
    OutcomeMemoryRequirements,
    OutcomeMemoryAssessment,
    OutcomeMemoryAction,
    OutcomeMemoryResult,
    OutcomeMemoryContract,
    OutcomeMemoryEngine,
    evaluate_outcome_memory,
    analyze_outcome_memory,
    review_outcome_memory,
    validate_outcome_memory_request,
    validate_outcome_memory_result,
    validate_outcome_memory_contract,
    outcome_memory_ready,
    outcome_memory_can_advance,
)


# ------------------------------------------------------------
# PATTERN MEMORY
# ------------------------------------------------------------

from .pattern_memory import (
    PATTERN_MEMORY_ENGINE,
    PATTERN_MEMORY_VERSION,
    PatternMemoryStatus,
    PatternMemoryType,
    PatternMemoryPriority,
    PatternMemorySourceType,
    PatternMemoryQuality,
    PatternMemoryContractStatus,
    PatternMemoryDataState,
    PatternMemoryConsistency,
    PatternMemoryReadiness,
    PatternMemoryActionState,
    PatternMemoryContractState,
    PatternMemoryResultStatus,
    PatternMemoryRequest,
    PatternMemoryReference,
    PatternMemorySourceReference,
    PatternMemoryContractValidation,
    PatternMemoryRequirements,
    PatternMemoryAssessment,
    PatternMemoryAction,
    PatternMemoryResult,
    PatternMemoryContract,
    PatternMemoryEngine,
    evaluate_pattern_memory,
    analyze_pattern_memory,
    review_pattern_memory,
    validate_pattern_memory_request,
    validate_pattern_memory_result,
    validate_pattern_memory_contract,
    pattern_memory_ready,
    pattern_memory_can_advance,
)


# ------------------------------------------------------------
# MEMORY RETRIEVAL
# ------------------------------------------------------------

from .memory_retrieval import (
    MEMORY_RETRIEVAL_ENGINE,
    MEMORY_RETRIEVAL_VERSION,
    MemoryRetrievalStatus,
    MemoryRetrievalType,
    MemoryRetrievalPriority,
    MemoryRetrievalSourceType,
    MemoryRetrievalContractStatus,
    MemoryRetrievalDataState,
    MemoryRetrievalMatchQuality,
    MemoryRetrievalConsistency,
    MemoryRetrievalReadiness,
    MemoryRetrievalActionState,
    MemoryRetrievalContractState,
    MemoryRetrievalResultStatus,
    MemoryRetrievalRequest,
    MemoryRetrievalReference,
    MemoryRetrievalSourceReference,
    MemoryRetrievalContractValidation,
    MemoryRetrievalRequirements,
    MemoryRetrievalAssessment,
    MemoryRetrievalAction,
    MemoryRetrievalResult,
    MemoryRetrievalContract,
    MemoryRetrievalEngine,
    get_memory_retrieval_engine,
    evaluate_memory_retrieval,
    search_memory,
    retrieve_memory,
    review_memory_retrieval,
    validate_memory_retrieval_request,
    validate_memory_retrieval_result,
    validate_memory_retrieval_contract,
    memory_retrieval_ready,
    memory_retrieval_can_advance,
)


# ------------------------------------------------------------
# MEMORY SERVICE
# ------------------------------------------------------------

from .memory_service import (
    MEMORY_SERVICE_ENGINE,
    MEMORY_SERVICE_VERSION,
    MemoryServiceStatus,
    MemoryServiceOperation,
    MemoryDomain,
    MemoryServicePriority,
    MemoryServiceSourceType,
    MemoryServiceContractStatus,
    MemoryServiceDataState,
    MemoryServiceConsistency,
    MemoryServiceReadiness,
    MemoryServiceActionState,
    MemoryServiceContractState,
    MemoryServiceResultStatus,
    MemoryServiceRequest,
    MemoryServiceReference,
    MemoryServiceSourceReference,
    MemoryServiceContractValidation,
    MemoryServiceRequirements,
    MemoryServiceAssessment,
    MemoryServiceAction,
    MemoryServiceResult,
    MemoryServiceContract,
    MemoryServiceEngine,
    get_memory_service_engine,
    evaluate_memory_service,
    search_memory_service,
    retrieve_memory_service,
    store_memory_service,
    review_memory_service,
    validate_memory_service_request,
    validate_memory_service_result,
    validate_memory_service_contract,
    memory_service_ready,
    memory_service_can_advance,
)


# ============================================================
# MEMORY LAYER IDENTITY
# ============================================================

MEMORY_LAYER_NAME = "ROBOMLM_MEMORY_INTELLIGENCE_LAYER"
MEMORY_LAYER_VERSION = "1.0"

MEMORY_LAYER_COMPONENTS = (
    "MARKET_MEMORY",
    "EVIDENCE_MEMORY",
    "DECISION_MEMORY",
    "OUTCOME_MEMORY",
    "PATTERN_MEMORY",
    "MEMORY_RETRIEVAL",
    "MEMORY_SERVICE",
)


# ============================================================
# AUTHORITY BOUNDARY
# ============================================================

def memory_layer_generates_decision() -> bool:
    return False


def memory_layer_modifies_d13() -> bool:
    return False


def memory_layer_overrides_d13() -> bool:
    return False


def memory_layer_overrides_risk() -> bool:
    return False


def memory_layer_overrides_cas() -> bool:
    return False


def memory_layer_authorizes_execution() -> bool:
    return False


def memory_layer_allows_order() -> bool:
    return False


def memory_layer_allows_trade() -> bool:
    return False


def memory_layer_allows_position_change() -> bool:
    return False


def memory_layer_execution_authority() -> bool:
    return False


# ============================================================
# HEALTH / IDENTITY
# ============================================================

def memory_layer_health_check() -> dict[str, object]:
    return {
        "healthy": True,
        "layer": MEMORY_LAYER_NAME,
        "version": MEMORY_LAYER_VERSION,
        "components": list(MEMORY_LAYER_COMPONENTS),
        "component_count": len(MEMORY_LAYER_COMPONENTS),
        "decision_authority": False,
        "d13_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }


def memory_layer_info() -> dict[str, object]:
    return {
        "name": MEMORY_LAYER_NAME,
        "version": MEMORY_LAYER_VERSION,
        "components": list(MEMORY_LAYER_COMPONENTS),
        "role": (
            "Historical memory preservation, validation, retrieval, "
            "consolidation and contextual support."
        ),
        "decision_authority": False,
        "risk_authority": False,
        "cas_authority": False,
        "execution_authority": False,
    }


def memory_layer_authority_statement() -> str:
    return (
        "ROBOMLM Memory Intelligence Layer preserves, validates, "
        "retrieves, consolidates and provides historical/contextual "
        "memory. It does not generate or alter authoritative trading "
        "decisions, does not override D13, Risk or CAS, and has no "
        "execution authority. D13 remains the decision authority, "
        "Risk remains the risk authority, and CAS remains the "
        "authorization and execution-safety authority."
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [

    # Layer identity
    "MEMORY_LAYER_NAME",
    "MEMORY_LAYER_VERSION",
    "MEMORY_LAYER_COMPONENTS",

    # --------------------------------------------------------
    # Market Memory
    # --------------------------------------------------------
    "MARKET_MEMORY_ENGINE",
    "MARKET_MEMORY_VERSION",
    "MarketMemoryStatus",
    "MarketMemoryType",
    "MarketMemoryPriority",
    "MarketMemorySourceType",
    "MarketMemoryContractStatus",
    "MarketMemoryDataState",
    "MarketMemoryConsistency",
    "MarketMemoryReadiness",
    "MarketMemoryActionState",
    "MarketMemoryContractState",
    "MarketMemoryResultStatus",
    "MarketMemoryRequest",
    "MarketMemoryReference",
    "MarketMemorySourceReference",
    "MarketMemoryContractValidation",
    "MarketMemoryRequirements",
    "MarketMemoryAssessment",
    "MarketMemoryAction",
    "MarketMemoryResult",
    "MarketMemoryContract",
    "MarketMemoryEngine",
    "evaluate_market_memory",
    "analyze_market_memory",
    "review_market_memory",
    "validate_market_memory_request",
    "validate_market_memory_result",
    "validate_market_memory_contract",
    "market_memory_ready",
    "market_memory_can_advance",

    # --------------------------------------------------------
    # Evidence Memory
    # --------------------------------------------------------
    "EVIDENCE_MEMORY_ENGINE",
    "EVIDENCE_MEMORY_VERSION",
    "EvidenceMemoryStatus",
    "EvidenceMemoryType",
    "EvidenceMemoryPriority",
    "EvidenceMemorySourceType",
    "EvidenceMemoryQuality",
    "EvidenceMemoryContractStatus",
    "EvidenceMemoryDataState",
    "EvidenceMemoryConsistency",
    "EvidenceMemoryReadiness",
    "EvidenceMemoryActionState",
    "EvidenceMemoryContractState",
    "EvidenceMemoryResultStatus",
    "EvidenceMemoryRequest",
    "EvidenceMemoryReference",
    "EvidenceMemorySourceReference",
    "EvidenceMemoryContractValidation",
    "EvidenceMemoryRequirements",
    "EvidenceMemoryAssessment",
    "EvidenceMemoryAction",
    "EvidenceMemoryResult",
    "EvidenceMemoryContract",
    "EvidenceMemoryEngine",
    "get_evidence_memory_engine",
    "evaluate_evidence_memory",
    "analyze_evidence_memory",
    "review_evidence_memory",
    "validate_evidence_memory_request",
    "validate_evidence_memory_result",
    "validate_evidence_memory_contract",
    "evidence_memory_ready",
    "evidence_memory_can_advance",

    # --------------------------------------------------------
    # Decision Memory
    # --------------------------------------------------------
    "DECISION_MEMORY_ENGINE",
    "DECISION_MEMORY_VERSION",
    "DecisionMemoryStatus",
    "DecisionMemoryType",
    "DecisionMemoryPriority",
    "DecisionMemorySourceType",
    "DecisionMemoryQuality",
    "DecisionMemoryContractStatus",
    "DecisionMemoryDataState",
    "DecisionMemoryConsistency",
    "DecisionMemoryReadiness",
    "DecisionMemoryActionState",
    "DecisionMemoryContractState",
    "DecisionMemoryResultStatus",
    "DecisionMemoryRequest",
    "DecisionMemoryReference",
    "DecisionMemorySourceReference",
    "DecisionMemoryContractValidation",
    "DecisionMemoryRequirements",
    "DecisionMemoryAssessment",
    "DecisionMemoryAction",
    "DecisionMemoryResult",
    "DecisionMemoryContract",
    "DecisionMemoryEngine",
    "get_decision_memory_engine",
    "evaluate_decision_memory",
    "analyze_decision_memory",
    "review_decision_memory",
    "validate_decision_memory_request",
    "validate_decision_memory_result",
    "validate_decision_memory_contract",
    "decision_memory_ready",
    "decision_memory_can_advance",

    # --------------------------------------------------------
    # Outcome Memory
    # --------------------------------------------------------
    "OUTCOME_MEMORY_ENGINE",
    "OUTCOME_MEMORY_VERSION",
    "OutcomeMemoryStatus",
    "OutcomeMemoryType",
    "OutcomeMemoryPriority",
    "OutcomeMemorySourceType",
    "OutcomeMemoryQuality",
    "OutcomeMemoryContractStatus",
    "OutcomeMemoryDataState",
    "OutcomeMemoryConsistency",
    "OutcomeMemoryReadiness",
    "OutcomeMemoryActionState",
    "OutcomeMemoryContractState",
    "OutcomeMemoryResultStatus",
    "OutcomeMemoryRequest",
    "OutcomeMemoryReference",
    "OutcomeMemorySourceReference",
    "OutcomeMemoryContractValidation",
    "OutcomeMemoryRequirements",
    "OutcomeMemoryAssessment",
    "OutcomeMemoryAction",
    "OutcomeMemoryResult",
    "OutcomeMemoryContract",
    "OutcomeMemoryEngine",
    "get_outcome_memory_engine",
    "evaluate_outcome_memory",
    "analyze_outcome_memory",
    "review_outcome_memory",
    "validate_outcome_memory_request",
    "validate_outcome_memory_result",
    "validate_outcome_memory_contract",
    "outcome_memory_ready",
    "outcome_memory_can_advance",

    # --------------------------------------------------------
    # Pattern Memory
    # --------------------------------------------------------
    "PATTERN_MEMORY_ENGINE",
    "PATTERN_MEMORY_VERSION",
    "PatternMemoryStatus",
    "PatternMemoryType",
    "PatternMemoryPriority",
    "PatternMemorySourceType",
    "PatternMemoryQuality",
    "PatternMemoryContractStatus",
    "PatternMemoryDataState",
    "PatternMemoryConsistency",
    "PatternMemoryReadiness",
    "PatternMemoryActionState",
    "PatternMemoryContractState",
    "PatternMemoryResultStatus",
    "PatternMemoryRequest",
    "PatternMemoryReference",
    "PatternMemorySourceReference",
    "PatternMemoryContractValidation",
    "PatternMemoryRequirements",
    "PatternMemoryAssessment",
    "PatternMemoryAction",
    "PatternMemoryResult",
    "PatternMemoryContract",
    "PatternMemoryEngine",
    "get_pattern_memory_engine",
    "evaluate_pattern_memory",
    "analyze_pattern_memory",
    "review_pattern_memory",
    "validate_pattern_memory_request",
    "validate_pattern_memory_result",
    "validate_pattern_memory_contract",
    "pattern_memory_ready",
    "pattern_memory_can_advance",

    # --------------------------------------------------------
    # Memory Retrieval
    # --------------------------------------------------------
    "MEMORY_RETRIEVAL_ENGINE",
    "MEMORY_RETRIEVAL_VERSION",
    "MemoryRetrievalStatus",
    "MemoryRetrievalType",
    "MemoryRetrievalPriority",
    "MemoryRetrievalSourceType",
    "MemoryRetrievalContractStatus",
    "MemoryRetrievalDataState",
    "MemoryRetrievalMatchQuality",
    "MemoryRetrievalConsistency",
    "MemoryRetrievalReadiness",
    "MemoryRetrievalActionState",
    "MemoryRetrievalContractState",
    "MemoryRetrievalResultStatus",
    "MemoryRetrievalRequest",
    "MemoryRetrievalReference",
    "MemoryRetrievalSourceReference",
    "MemoryRetrievalContractValidation",
    "MemoryRetrievalRequirements",
    "MemoryRetrievalAssessment",
    "MemoryRetrievalAction",
    "MemoryRetrievalResult",
    "MemoryRetrievalContract",
    "MemoryRetrievalEngine",
    "get_memory_retrieval_engine",
    "evaluate_memory_retrieval",
    "search_memory",
    "retrieve_memory",
    "review_memory_retrieval",
    "validate_memory_retrieval_request",
    "validate_memory_retrieval_result",
    "validate_memory_retrieval_contract",
    "memory_retrieval_ready",
    "memory_retrieval_can_advance",

    # --------------------------------------------------------
    # Memory Service
    # --------------------------------------------------------
    "MEMORY_SERVICE_ENGINE",
    "MEMORY_SERVICE_VERSION",
    "MemoryServiceStatus",
    "MemoryServiceOperation",
    "MemoryDomain",
    "MemoryServicePriority",
    "MemoryServiceSourceType",
    "MemoryServiceContractStatus",
    "MemoryServiceDataState",
    "MemoryServiceConsistency",
    "MemoryServiceReadiness",
    "MemoryServiceActionState",
    "MemoryServiceContractState",
    "MemoryServiceResultStatus",
    "MemoryServiceRequest",
    "MemoryServiceReference",
    "MemoryServiceSourceReference",
    "MemoryServiceContractValidation",
    "MemoryServiceRequirements",
    "MemoryServiceAssessment",
    "MemoryServiceAction",
    "MemoryServiceResult",
    "MemoryServiceContract",
    "MemoryServiceEngine",
    "get_memory_service_engine",
    "evaluate_memory_service",
    "search_memory_service",
    "retrieve_memory_service",
    "store_memory_service",
    "review_memory_service",
    "validate_memory_service_request",
    "validate_memory_service_result",
    "validate_memory_service_contract",
    "memory_service_ready",
    "memory_service_can_advance",

    # --------------------------------------------------------
    # Layer Authority
    # --------------------------------------------------------
    "memory_layer_generates_decision",
    "memory_layer_modifies_d13",
    "memory_layer_overrides_d13",
    "memory_layer_overrides_risk",
    "memory_layer_overrides_cas",
    "memory_layer_authorizes_execution",
    "memory_layer_allows_order",
    "memory_layer_allows_trade",
    "memory_layer_allows_position_change",
    "memory_layer_execution_authority",

    # --------------------------------------------------------
    # Layer Health / Info
    # --------------------------------------------------------
    "memory_layer_health_check",
    "memory_layer_info",
    "memory_layer_authority_statement",
]