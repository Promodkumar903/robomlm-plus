"""X — ChatGPT Strategy v1.

## Purpose

Conservative confirmation strategy intended to reduce low-quality entries.

This strategy:
- does NOT replace UnifiedSignal
- does NOT bypass AutoROBOMLM gates
- does NOT fabricate market data
- only decides whether a candidate may proceed

Focus:
- directional clarity
- quality grade
- confidence-strength alignment
- component agreement
- risk sanity
"""

from __future__ import annotations

from app.strategies.base import (
BaseStrategy,
StrategyID,
StrategyInput,
StrategyOutput,
)
from app.strategies.spot_strategy import SpotStrategy
from app.strategies.futures_strategy import FuturesStrategy
from app.strategies.crypto_strategy import CryptoStrategy
from app.strategies.forex_strategy import ForexStrategy
from app.strategies.commodity_strategy import CommodityStrategy
from app.strategies.indices_strategy import IndicesStrategy
from app.strategies.options_strategy import OptionsStrategy
from app.strategies.option_future import OptionFutureStrategy

class ChatGPTStrategy(BaseStrategy):
    ID = StrategyID.CHATGPT
    VERSION = "1.0"

    # --------------------------------------------------
    # Thresholds
    # --------------------------------------------------

    MIN_STRENGTH = 40.0
    MIN_CONFIDENCE = 58.0

    MIN_RR = 1.60
    MAX_SL_PCT = 2.50

    MIN_COMPONENT_SCORE = 40.0
    MIN_CONFLUENCE = 4

    MIN_CONTEXT = 30.0
    MIN_REGIME = 25.0

    ALLOWED_GRADES = {"A+", "A", "B+"}

    EXTREME_RISK = "EXTREME"
    HIGH_RISK = "HIGH"

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _reject(
        self,
        reason: str,
        notes: str = "",
    ) -> StrategyOutput:
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

    def _num(self, value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    # --------------------------------------------------
    # Main decision
    # --------------------------------------------------

    def decide(self, data: StrategyInput) -> StrategyOutput:
        # OLD=CHATGPT: execute all 8 existing market strategies.
        market_strategies = (
            ('SPOT', SpotStrategy()),
            ('FUTURES', FuturesStrategy()),
            ('CRYPTO', CryptoStrategy()),
            ('FOREX', ForexStrategy()),
            ('COMMODITY', CommodityStrategy()),
            ('INDICES', IndicesStrategy()),
            ('OPTIONS', OptionsStrategy()),
            ('OPTION_FUTURE', OptionFutureStrategy()),
        )

        candidates = []
        failures = []

        for market_id, strategy in market_strategies:
            try:
                out = strategy.decide(data)
            except Exception as exc:
                failures.append(f'{market_id}:EXCEPTION:{type(exc).__name__}')
                continue

            if out.entry_permission:
                candidates.append((market_id, out))
            else:
                code = out.reason_codes[0] if out.reason_codes else 'REJECTED'
                failures.append(f'{market_id}:{code}')

        if not candidates:
            return self._reject(
                'NO_MARKET_STRATEGY_PASSED',
                '8-strategy pool produced no valid trade candidate. ' + ' | '.join(failures),
            )

        selected_market, selected = max(
            candidates,
            key=lambda item: float(item[1].strategy_score),
        )

        return StrategyOutput(
            strategy_id=StrategyID.CHATGPT,
            direction=selected.direction,
            entry_permission=True,
            strategy_score=selected.strategy_score,
            confidence=selected.confidence,
            timing_quality=selected.timing_quality,
            risk_quality=selected.risk_quality,
            reason_codes=(
                'CHATGPT_8_STRATEGY_POOL',
                f'SELECTED_{selected_market}',
                *selected.reason_codes,
            ),
            notes=(
                f'8-strategy pool selected {selected_market}; '
                f'score={selected.strategy_score:.2f}; '
                f'candidates={len(candidates)}/8'
            ),
        )
    def _legacy_decide(self, data: StrategyInput) -> StrategyOutput:

        # 1. Direction gate
        if data.direction not in ("BULLISH", "BEARISH"):
            return self._reject(
                "NEUTRAL_DIRECTION",
                "No directional edge."
            )

        # 2. Grade gate
        grade = (data.trade_quality or "").strip().upper()
        if grade not in self.ALLOWED_GRADES:
            return self._reject(
                f"GRADE_{grade or 'UNKNOWN'}"
            )

        # 3. Risk gate
        risk = (data.risk_level or "").strip().upper()

        if risk == self.EXTREME_RISK:
            return self._reject("EXTREME_RISK")

        # High risk requires stronger evidence
        min_strength = self.MIN_STRENGTH
        min_confidence = self.MIN_CONFIDENCE

        if risk == self.HIGH_RISK:
            min_strength += 10.0
            min_confidence += 5.0

        # 4. Strength gate
        if data.strength < min_strength:
            return self._reject(
                f"STRENGTH_{data.strength:.1f}"
            )

        # 5. Confidence gate
        if data.confidence < min_confidence:
            return self._reject(
                f"CONFIDENCE_{data.confidence:.1f}"
            )

        # 6. Risk reward gate
        rr = data.risk_reward

        if rr is not None and rr < self.MIN_RR:
            return self._reject(
                f"RR_LOW_{rr:.2f}"
            )

        # 7. Component analysis
        c = data.components or {}

        flow = self._num(c.get("flow"))
        derivative = self._num(c.get("derivative"))
        volume = self._num(c.get("volume"))
        obstacle = self._num(c.get("obstacle"))
        context = self._num(c.get("context"))
        regime = self._num(c.get("regime"))

        scores = [
            flow,
            derivative,
            volume,
            obstacle,
            context,
            regime,
        ]

        aligned = sum(
            1
            for score in scores
            if score >= self.MIN_COMPONENT_SCORE
        )

        if aligned < self.MIN_CONFLUENCE:
            return self._reject(
                f"CONFLUENCE_{aligned}_OF_6"
            )

        # 8. Context gate
        if context < self.MIN_CONTEXT:
            return self._reject(
                f"CONTEXT_{context:.1f}"
            )

        # 9. Regime gate
        if regime < self.MIN_REGIME:
            return self._reject(
                f"REGIME_{regime:.1f}"
            )

        # 10. SL sanity gate
        if (
            data.stop_loss is not None
            and data.entry_price > 0
        ):
            sl_pct = (
                abs(data.entry_price - data.stop_loss)
                / data.entry_price
                * 100.0
            )

            if sl_pct > self.MAX_SL_PCT:
                return self._reject(
                    f"SL_WIDE_{sl_pct:.2f}%"
                )

        # --------------------------------------------------
        # Score model
        # --------------------------------------------------

        component_avg = sum(scores) / 6.0

        timing_quality = (
            flow * 0.40 +
            volume * 0.30 +
            obstacle * 0.30
        )

        risk_quality = (
            context * 0.50 +
            regime * 0.50
        )

        strategy_score = (
            data.strength * 0.30 +
            data.confidence * 0.30 +
            component_avg * 0.20 +
            timing_quality * 0.10 +
            risk_quality * 0.10
        )

        action = (
            "BUY"
            if data.direction == "BULLISH"
            else "SELL"
        )

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
                f"GRADE_{grade}",
                f"CONFLUENCE_{aligned}_OF_6",
                f"STRENGTH_{data.strength:.1f}",
                f"CONFIDENCE_{data.confidence:.1f}",
            ),
            notes=(
                f"{data.symbol} "
                f"{action} "
                f"score={strategy_score:.1f}"
            ),
        )
