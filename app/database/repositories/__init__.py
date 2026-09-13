"""
ROBOMLM PLUS
Database Repositories Package
"""

from app.database.repositories.decision_repository import (
    DecisionRepository,
    DecisionRepositoryError,
    DecisionNotFoundError,
    decision_repository,
    get_decision_repository,
)

from app.database.repositories.evidence_repository import (
    EvidenceRepository,
    EvidenceRepositoryError,
    EvidenceNotFoundError,
    evidence_repository,
    get_evidence_repository,
)

from app.database.repositories.trade_repository import (
    TradeRepository,
    TradeRepositoryError,
    TradeNotFoundError,
    trade_repository,
    get_trade_repository,
)

from app.database.repositories.user_repository import (
    UserRepository,
    UserRepositoryError,
    UserNotFoundError,
    DuplicateUserError,
    user_repository,
    get_user_repository,
)


__all__ = [
    # Decision
    "DecisionRepository",
    "DecisionRepositoryError",
    "DecisionNotFoundError",
    "decision_repository",
    "get_decision_repository",

    # Evidence
    "EvidenceRepository",
    "EvidenceRepositoryError",
    "EvidenceNotFoundError",
    "evidence_repository",
    "get_evidence_repository",

    # Trade
    "TradeRepository",
    "TradeRepositoryError",
    "TradeNotFoundError",
    "trade_repository",
    "get_trade_repository",

    # User
    "UserRepository",
    "UserRepositoryError",
    "UserNotFoundError",
    "DuplicateUserError",
    "user_repository",
    "get_user_repository",
]