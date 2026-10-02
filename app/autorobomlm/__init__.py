"""
ROBOMLM_PLUS - AutoROBOMLM package.

Safety pipeline between D13 decision and execution.

Layers:
    config              - user configuration + grade bands
    grade_evaluator     - signal -> grade band
    objective_gate      - AIC-009
    resource_gate       - AIC-007
    constraint_gate     - AIC-008
    capital_allocator   - position sizing
    sl_tp_calculator    - SL/TP calculation
    paper_broker        - execution simulator
    auto_loop           - main scheduler
    autorobomlm_api     - thin API layer
"""

from app.autorobomlm.config import (
    AutoRobomlmConfig,
    GradeBand,
    GradeBands,
    WatchlistSource,
    ExecutionMode,
    DEFAULT_GRADE_BANDS,
)

from app.autorobomlm.grade_evaluator import (
    GradeEvaluator,
    GradeInput,
    GradeResult,
    GradeSource,
    GradeStatus,
    evaluate_grade,
)

from app.autorobomlm.objective_gate import (
    ObjectiveGate,
    ObjectiveDefinition,
    ObjectiveGateResult,
    ObjectiveGateStatus,
    ObjectiveType,
    evaluate_objective,
)

from app.autorobomlm.resource_gate import (
    ResourceGate,
    ResourceCheck,
    ResourceGateResult,
    ResourceGateStatus,
    ResourceKind,
    evaluate_resources,
)

from app.autorobomlm.constraint_gate import (
    ConstraintGate,
    ConstraintCheck,
    ConstraintDisposition,
    ConstraintGateResult,
    ConstraintGateStatus,
    ConstraintKind,
    evaluate_constraints,
)

from app.autorobomlm.capital_allocator import (
    CapitalAllocator,
    AllocationRequest,
    AllocationResult,
    AllocatorStatus,
    allocate_capital,
)

from app.autorobomlm.sl_tp_calculator import (
    SLTPCalculator,
    SLTPRequest,
    SLTPResult,
    SLTPStatus,
    TradeDirection as SLTPTradeDirection,
    calculate_sl_tp,
)

from app.autorobomlm.paper_broker import (
    PaperBroker,
    Position,
    PositionStatus,
    BrokerStatus,
    FillResult,
    TradeDirection as BrokerTradeDirection,
)

from app.autorobomlm.auto_loop import (
    AutoRobomlmLoop,
    LoopState,
    TickSummary,
)

from app.autorobomlm.autorobomlm_api import (
    AutoRobomlmAPI,
)

__all__ = [
    # config
    "AutoRobomlmConfig",
    "GradeBand", "GradeBands",
    "WatchlistSource", "ExecutionMode",
    "DEFAULT_GRADE_BANDS",

    # grade
    "GradeEvaluator", "GradeInput",
    "GradeResult", "GradeSource", "GradeStatus",
    "evaluate_grade",

    # objective
    "ObjectiveGate", "ObjectiveDefinition",
    "ObjectiveGateResult", "ObjectiveGateStatus",
    "ObjectiveType", "evaluate_objective",

    # resource
    "ResourceGate", "ResourceCheck",
    "ResourceGateResult", "ResourceGateStatus",
    "ResourceKind", "evaluate_resources",

    # constraint
    "ConstraintGate", "ConstraintCheck",
    "ConstraintDisposition", "ConstraintGateResult",
    "ConstraintGateStatus", "ConstraintKind",
    "evaluate_constraints",

    # allocator
    "CapitalAllocator", "AllocationRequest",
    "AllocationResult", "AllocatorStatus",
    "allocate_capital",

    # sl/tp
    "SLTPCalculator", "SLTPRequest", "SLTPResult",
    "SLTPStatus", "SLTPTradeDirection",
    "calculate_sl_tp",

    # broker
    "PaperBroker", "Position", "PositionStatus",
    "BrokerStatus", "FillResult",
    "BrokerTradeDirection",

    # loop
    "AutoRobomlmLoop", "LoopState", "TickSummary",

    # api
    "AutoRobomlmAPI",
]