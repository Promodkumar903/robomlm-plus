# create_strategy_folders.py
# Sirf NAYE folders + NAYI files banata hai.
# Koi existing file touch nahi hoti. Koi delete nahi.

import os

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
BASE = os.path.join(ROOT, "app", "strategies")

FILES = {
    "__init__.py": '"""ROBOMLM_PLUS strategy research layer."""\n',

    "base.py": '''"""Shared interface for X (ChatGPT) and Y (DeepSeek) strategies."""

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
    direction: str              # BULLISH / BEARISH / NEUTRAL
    strength: float             # UnifiedSignal.strength
    confidence: float           # UnifiedSignal.confidence
    entry_price: float
    stop_loss: float | None
    take_profit: float | None
    components: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyOutput:
    """Strategy decision. Does NOT bypass gates."""
    strategy_id: StrategyID
    direction: str              # BUY / SELL / HOLD
    entry_permission: bool      # True = allow entering gate chain
    strategy_score: float       # 0..100
    confidence: float           # 0..100
    timing_quality: float       # 0..100
    risk_quality: float         # 0..100
    reason_codes: tuple[str, ...] = ()
    notes: str = ""


class BaseStrategy:
    """Every strategy implements decide()."""
    ID: StrategyID = StrategyID.CHATGPT

    def decide(self, data: StrategyInput) -> StrategyOutput:
        raise NotImplementedError
''',

    "chatgpt_strategy/__init__.py":
        'from .strategy import ChatGPTStrategy\n__all__ = ["ChatGPTStrategy"]\n',

    "chatgpt_strategy/strategy.py": '''"""X — ChatGPT Strategy (stub). Rules TBD."""

from __future__ import annotations
from app.strategies.base import (
    BaseStrategy, StrategyID, StrategyInput, StrategyOutput,
)


class ChatGPTStrategy(BaseStrategy):
    ID = StrategyID.CHATGPT
    VERSION = "0.1-stub"

    def decide(self, data: StrategyInput) -> StrategyOutput:
        # TODO: ChatGPT rules will be placed here.
        return StrategyOutput(
            strategy_id=self.ID,
            direction="HOLD",
            entry_permission=False,
            strategy_score=0.0,
            confidence=0.0,
            timing_quality=0.0,
            risk_quality=0.0,
            reason_codes=("STUB_NOT_IMPLEMENTED",),
            notes="ChatGPT strategy not wired yet.",
        )
''',

    "deepseek_strategy/__init__.py":
        'from .strategy import DeepSeekStrategy\n__all__ = ["DeepSeekStrategy"]\n',

    "deepseek_strategy/strategy.py": '''"""Y — DeepSeek Strategy (stub). Rules TBD."""

from __future__ import annotations
from app.strategies.base import (
    BaseStrategy, StrategyID, StrategyInput, StrategyOutput,
)


class DeepSeekStrategy(BaseStrategy):
    ID = StrategyID.DEEPSEEK
    VERSION = "0.1-stub"

    def decide(self, data: StrategyInput) -> StrategyOutput:
        # TODO: DeepSeek rules will be placed here.
        return StrategyOutput(
            strategy_id=self.ID,
            direction="HOLD",
            entry_permission=False,
            strategy_score=0.0,
            confidence=0.0,
            timing_quality=0.0,
            risk_quality=0.0,
            reason_codes=("STUB_NOT_IMPLEMENTED",),
            notes="DeepSeek strategy not wired yet.",
        )
''',
}


def main():
    print("=" * 60)
    print("Create strategy folders (NEW files only, no touch)")
    print("=" * 60)

    created = skipped = 0
    for rel, content in FILES.items():
        path = os.path.join(BASE, rel)
        if os.path.exists(path):
            print(f"  EXISTS   {rel}")
            skipped += 1
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  CREATED  {rel}")
        created += 1

    print()
    print(f"Created: {created}  Skipped: {skipped}")
    print(f"Location: {BASE}")
    print()
    print("Kuch existing file touch nahi hui.")


if __name__ == "__main__":
    main()