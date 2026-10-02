"""Master portfolio strategy.

V1:
- Collects market-specific strategy candidates.
- Applies deterministic grade ordering.
- Does not execute trades.
- Does not bypass risk/allocation/execution gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class PortfolioCandidate:
    symbol: str
    market: str
    direction: str
    grade: str
    strategy_score: float
    confidence: float
    entry_permission: bool
    risk_reward: Optional[float] = None


@dataclass(frozen=True)
class PortfolioDecision:
    selected: bool
    symbol: Optional[str]
    market: Optional[str]
    direction: Optional[str]
    grade: str
    strategy_score: float
    reason: str


class MasterPortfolioStrategy:
    """Final V1 portfolio-level candidate selector."""

    VERSION = "1.0"

    GRADE_ORDER = {
        "A+": 4,
        "A": 3,
        "B+": 2,
        "B": 1,
        "HOLD": 0,
    }

    def select(
        self,
        candidates: Iterable[PortfolioCandidate],
    ) -> PortfolioDecision:
        valid = [
            candidate
            for candidate in candidates
            if candidate.entry_permission
            and candidate.grade in self.GRADE_ORDER
            and candidate.grade != "HOLD"
        ]

        if not valid:
            return PortfolioDecision(
                selected=False,
                symbol=None,
                market=None,
                direction=None,
                grade="HOLD",
                strategy_score=0.0,
                reason="NO_VALID_STRATEGY_CANDIDATE",
            )

        ranked = sorted(
            valid,
            key=lambda candidate: (
                self.GRADE_ORDER[candidate.grade],
                float(candidate.strategy_score),
                float(candidate.confidence),
            ),
            reverse=True,
        )

        selected = ranked[0]

        return PortfolioDecision(
            selected=True,
            symbol=selected.symbol,
            market=selected.market,
            direction=selected.direction,
            grade=selected.grade,
            strategy_score=selected.strategy_score,
            reason="MASTER_PORTFOLIO_CANDIDATE_SELECTED",
        )