# ============================================================
# ROBOMLM_PLUS — app/intelligence/robomlm_plus/__init__.py
# PACKAGE INITIALIZATION
# ============================================================

"""
ROBOMLM_PLUS Intelligence Package

Purpose:
    Controlled higher-order intelligence, preparation,
    monitoring, protection, reconciliation and emergency
    control layer.

Authority boundaries:
    D13  = Decision Authority
    RISK = Risk Authority
    CAS  = Authorization Authority

ROBOMLM_PLUS:
    - refines and orchestrates established intelligence
    - prepares controlled downstream states
    - monitors positions
    - evaluates protection
    - reconciles expected vs actual state
    - evaluates emergency conditions
    - controls halt state

ROBOMLM_PLUS does NOT:
    - replace D13
    - recalculate/override Risk
    - create CAS authorization
    - create broker orders
    - execute trades
    - modify positions directly
"""

from .advanced_decision import (
    AdvancedDecision,
    AdvancedDecisionEngine,
    AdvancedDecisionRequest,
    AdvancedDecisionResult,
    advanced_decision_health_check,
    run_advanced_decision,
)

from .execution_preparation import (
    ExecutionPreparation,
    ExecutionPreparationEngine,
    ExecutionPreparationRequest,
    ExecutionPreparationContract,
    prepare_execution,
    execution_preparation_health_check,
)

from .position_monitor import (
    PositionMonitor,
    PositionMonitorEngine,
    PositionMonitorRequest,
    PositionMonitorContract,
    monitor_position,
    position_monitor_health_check,
)

from .protection import (
    Protection,
    ProtectionEngine,
    ProtectionRequest,
    ProtectionContract,
    process_protection,
    protection_health_check,
)

from .reconciliation import (
    Reconciliation,
    ReconciliationEngine,
    ReconciliationRequest,
    ReconciliationContract,
    reconcile,
    reconciliation_health_check,
)

from .plus_orchestrator import (
    PlusOrchestrator,
    PlusOrchestratorEngine,
    PlusOrchestratorRequest,
    PlusOrchestratorContract,
    orchestrate_plus,
    plus_orchestration_audit,
)

from .emergency_control import (
    EmergencyControl,
    EmergencyControlEngine,
    EmergencyControlRequest,
    EmergencyControlContract,
    process_emergency_control,
    emergency_control_audit,
)

from .halt_controller import (
    HaltController,
    HaltControllerEngine,
    HaltControllerRequest,
    HaltControllerContract,
    process_halt_controller,
    halt_controller_audit,
)


# ============================================================
# PACKAGE IDENTITY
# ============================================================

__version__ = "1.0"
__package_name__ = "ROBOMLM_PLUS"


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    # Package
    "__version__",
    "__package_name__",

    # Advanced Decision
    "AdvancedDecision",
    "AdvancedDecisionEngine",
    "AdvancedDecisionRequest",
    "AdvancedDecisionResult",
    "advanced_decision_health_check",
    "run_advanced_decision",

    # Execution Preparation
    "ExecutionPreparation",
    "ExecutionPreparationEngine",
    "ExecutionPreparationRequest",
    "ExecutionPreparationContract",
    "prepare_execution",
    "execution_preparation_health_check",

    # Position Monitor
    "PositionMonitor",
    "PositionMonitorEngine",
    "PositionMonitorRequest",
    "PositionMonitorContract",
    "monitor_position",
    "position_monitor_health_check",

    # Protection
    "Protection",
    "ProtectionEngine",
    "ProtectionRequest",
    "ProtectionContract",
    "process_protection",
    "protection_health_check",

    # Reconciliation
    "Reconciliation",
    "ReconciliationEngine",
    "ReconciliationRequest",
    "ReconciliationContract",
    "reconcile",
    "reconciliation_health_check",

    # PLUS Orchestrator
    "PlusOrchestrator",
    "PlusOrchestratorEngine",
    "PlusOrchestratorRequest",
    "PlusOrchestratorContract",
    "orchestrate_plus",
    "plus_orchestration_audit",

    # Emergency Control
    "EmergencyControl",
    "EmergencyControlEngine",
    "EmergencyControlRequest",
    "EmergencyControlContract",
    "process_emergency_control",
    "emergency_control_audit",

    # Halt Controller
    "HaltController",
    "HaltControllerEngine",
    "HaltControllerRequest",
    "HaltControllerContract",
    "process_halt_controller",
    "halt_controller_audit",
]


# ============================================================
# END OF __init__.py
# ROBOMLM_PLUS PACKAGE COMPLETE
# ============================================================