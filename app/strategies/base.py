"""Shared interface for X (ChatGPT) and Y (DeepSeek) strategies."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class StrategyID(str, Enum):
    CHATGPT = "CHATGPT"   # X
    DEEPSEEK = "DEEPSEEK" # Y


@dataclass(frozen=True)
class StrategyInput:
    """Input given to any strategy. Backend provides this."""
    symbol: str
    timeframe: str
    direction: str                    # BULLISH / BEARISH / NEUTRAL
    action: str                       # BUY / SELL / HOLD
    strength: float                   # 0-100 (UnifiedSignal.strength)
    confidence: float                 # 0-100
    trade_quality: str                # A+ / A / B+ / B / HOLD
    risk_level: str                   # LOW / MEDIUM / HIGH / EXTREME
    entry_price: float
    stop_loss: float | None
    take_profit: float | None
    risk_reward: float | None
    expected_move_pct: float
    components: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyOutput:
    """Strategy decision. Does NOT bypass gates."""
    strategy_id: StrategyID
    direction: str                    # BUY / SELL / HOLD
    entry_permission: bool            # True = allow entering gate chain
    strategy_score: float             # 0-100
    confidence: float                 # 0-100
    timing_quality: float             # 0-100
    risk_quality: float               # 0-100
    reason_codes: tuple[str, ...] = ()
    notes: str = ""


class BaseStrategy:
    """Every strategy implements decide()."""
    ID: StrategyID = StrategyID.CHATGPT
    VERSION: str = "0.0"

    def decide(self, data: StrategyInput) -> StrategyOutput:
        raise NotImplementedError
