# patch_deepseek_v1.py
# 1. Backup + rewrite app/strategies/base.py (adds missing fields)
# 2. Backup + rewrite app/strategies/deepseek_strategy/strategy.py (rules)
# Rule: backup PEHLE. Kuch delete nahi.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"
BASE = os.path.join(ROOT, "app", "strategies")

BASE_PY = os.path.join(BASE, "base.py")
DEEP_PY = os.path.join(BASE, "deepseek_strategy", "strategy.py")


NEW_BASE = '''"""Shared interface for X (ChatGPT) and Y (DeepSeek) strategies."""

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
'''


NEW_DEEP = '''"""Y — DeepSeek Strategy v1.

Goal
----
Improve AutoROBOMLM win rate and reduce SL hits by applying
strict multi-gate filtering on top of UnifiedSignal.

Logic
-----
1. Basic sanity (direction, grade, risk, RR)
2. Strength + Confidence double gate
3. Multi-component confluence (>= 3 of 6 agree)
4. Context alignment
5. SL sanity (not too wide)
6. Final weighted score

This strategy DOES NOT:
    - replace backend intelligence
    - bypass risk / gates / CAS
    - fabricate values
Only entry-permission + score are produced.
"""

from __future__ import annotations

from app.strategies.base import (
    BaseStrategy, StrategyID, StrategyInput, StrategyOutput,
)


class DeepSeekStrategy(BaseStrategy):
    ID = StrategyID.DEEPSEEK
    VERSION = "1.0"

    # ---------- Tunable thresholds ----------
    MIN_STRENGTH = 45.0
    STRONG_STRENGTH = 60.0
    MIN_CONFIDENCE = 55.0
    STRONG_CONFIDENCE = 70.0
    MIN_CONTEXT = 35.0
    MIN_CONFLUENCE = 3              # out of 6 components
    MIN_RR = 1.4
    MAX_SL_PCT = 3.0                # SL must be < 3% away
    ALLOWED_GRADES = {"A+", "A", "B+"}
    EXTREME_RISK = "EXTREME"

    # ---------- Helpers ----------
    def _reject(self, reason: str, notes: str = "") -> StrategyOutput:
        return StrategyOutput(
            strategy_id=self.ID,
            direction="HOLD",
            entry_permission=False,
            strategy_score=0.0,
            confidence=0.0,
            timing_quality=0.0,
            risk_quality=0.0,
            reason_codes=(reason,),
            notes=notes,
        )

    def _num(self, v, default=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    # ---------- Main ----------
    def decide(self, data: StrategyInput) -> StrategyOutput:

        # 1. Direction must be directional
        if data.direction not in ("BULLISH", "BEARISH"):
            return self._reject("NEUTRAL_DIRECTION")

        # 2. Trade quality
        if data.trade_quality not in self.ALLOWED_GRADES:
            return self._reject(f"GRADE_{data.trade_quality or 'UNKNOWN'}")

        # 3. Extreme risk
        if (data.risk_level or "").upper() == self.EXTREME_RISK:
            return self._reject("EXTREME_RISK")

        # 4. Risk-reward gate
        rr = data.risk_reward
        if rr is not None and rr < self.MIN_RR:
            return self._reject(f"RR_LOW_{rr:.2f}")

        # 5. Strength gate
        if data.strength < self.MIN_STRENGTH:
            return self._reject(f"STRENGTH_{data.strength:.1f}")

        # 6. Confidence gate
        if data.confidence < self.MIN_CONFIDENCE:
            return self._reject(f"CONFIDENCE_{data.confidence:.1f}")

        # 7. Confluence
        c = data.components or {}
        scores = [
            self._num(c.get("flow")),
            self._num(c.get("derivative")),
            self._num(c.get("volume")),
            self._num(c.get("obstacle")),
            self._num(c.get("context")),
            self._num(c.get("regime")),
        ]
        aligned = sum(1 for s in scores if s >= 45.0)
        if aligned < self.MIN_CONFLUENCE:
            return self._reject(f"CONFLUENCE_{aligned}_OF_6")

        # 8. Context minimum
        context = self._num(c.get("context"))
        if context < self.MIN_CONTEXT:
            return self._reject(f"CONTEXT_{context:.1f}")

        # 9. SL sanity
        if data.stop_loss is not None and data.entry_price > 0:
            sl_pct = abs(data.entry_price - data.stop_loss) / data.entry_price * 100.0
            if sl_pct > self.MAX_SL_PCT:
                return self._reject(f"SL_WIDE_{sl_pct:.2f}%")

        # ---------- Compute scores ----------
        avg_conf = sum(scores) / 6.0
        timing_quality = (scores[0] + scores[2]) / 2.0      # flow + volume
        risk_quality = (context + scores[5]) / 2.0          # context + regime

        strategy_score = (
            data.strength * 0.35 +
            data.confidence * 0.25 +
            avg_conf * 0.20 +
            context * 0.10 +
            scores[5] * 0.10
        )

        # ---------- Direction map ----------
        action = "BUY" if data.direction == "BULLISH" else "SELL"

        return StrategyOutput(
            strategy_id=self.ID,
            direction=action,
            entry_permission=True,
            strategy_score=round(strategy_score, 2),
            confidence=round(data.confidence, 2),
            timing_quality=round(timing_quality, 2),
            risk_quality=round(risk_quality, 2),
            reason_codes=(
                "ALL_GATES_PASSED",
                f"CONFLUENCE_{aligned}_OF_6",
                f"STRENGTH_{data.strength:.1f}",
                f"CONFIDENCE_{data.confidence:.1f}",
            ),
            notes=(
                f"{data.symbol} {action} "
                f"score={strategy_score:.1f}"
            ),
        )
'''


def backup(path):
    if not os.path.isfile(path):
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        return None
    return bak


def main():
    print("=" * 60)
    print("DeepSeek Strategy v1 patcher")
    print("=" * 60)

    # ---- base.py ----
    if os.path.isfile(BASE_PY):
        bak = backup(BASE_PY)
        if not bak:
            print("ERROR: base.py backup failed. Abort.")
            sys.exit(1)
        print(f"BACKUP OK: {os.path.basename(bak)}")
    with open(BASE_PY, "w", encoding="utf-8") as f:
        f.write(NEW_BASE)
    print("PATCHED: base.py")

    # ---- deepseek strategy ----
    os.makedirs(os.path.dirname(DEEP_PY), exist_ok=True)
    if os.path.isfile(DEEP_PY):
        bak = backup(DEEP_PY)
        if not bak:
            print("ERROR: deepseek strategy backup failed. Abort.")
            sys.exit(1)
        print(f"BACKUP OK: {os.path.basename(bak)}")
    with open(DEEP_PY, "w", encoding="utf-8") as f:
        f.write(NEW_DEEP)
    print("PATCHED: deepseek_strategy/strategy.py")

    print()
    print("Done. Kuch existing file touch nahi hui (AutoROBOMLM safe hai).")


if __name__ == "__main__":
    main()