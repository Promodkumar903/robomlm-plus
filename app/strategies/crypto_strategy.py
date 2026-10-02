"""
ROBOMLM_PLUS - Crypto Market Strategy

File:
    C:\\Users\\Administrator\\ROBOMLM_PLUS\\app\\strategies\\crypto_strategy.py

Purpose:
    Market-specific crypto strategy layer.

Architecture:
    Existing Intelligence
        -> Trend / Structure / Regime
        -> Flow / Volume / Derivative evidence
        -> Crypto setup classification
        -> 0-100 strategy score
        -> Grade
        -> Mandatory A+ gates
        -> StrategyOutput

Important:
    This strategy interprets existing backend intelligence.

    It does NOT:
        - create market data
        - replace intelligence engines
        - invent OI
        - invent OI delta
        - invent delta
        - invent footprint imbalance
        - invent funding
        - invent liquidation data
        - calculate a replacement EQE/PFS/LQS/MTS formula
        - generate SL/TP
        - execute trades
        - bypass downstream risk gates
        - modify AutoROBOMLM wiring
"""

from __future__ import annotations

from typing import Any, Mapping

from app.strategies.base import (
    BaseStrategy,
    StrategyID,
    StrategyInput,
    StrategyOutput,
)


class CryptoStrategy(BaseStrategy):
    """
    Crypto-specific strategy interpreter.

    The strategy layer consumes StrategyInput produced by the existing
    backend and returns StrategyOutput for downstream AutoROBOMLM gates.
    """

    # NOTE:
    # StrategyID currently contains only CHATGPT and DEEPSEEK.
    # CRYPTO is therefore represented as a runtime-compatible string here.
    # The base enum should NOT be changed until AutoROBOMLM wiring proves
    # that an enum extension is required.
    ID = "CRYPTO"

    VERSION = "1.0"

    # ------------------------------------------------------------------
    # Basic gates
    # ------------------------------------------------------------------

    MIN_DIRECTIONAL_STRENGTH = 40.0
    MIN_CONFIDENCE = 55.0

    # ------------------------------------------------------------------
    # Existing StrategyInput component contract
    # ------------------------------------------------------------------

    REQUIRED_COMPONENTS = (
        "flow",
        "derivative",
        "volume",
        "obstacle",
        "context",
        "regime",
    )

    # ------------------------------------------------------------------
    # Locked score bands
    # ------------------------------------------------------------------

    B_MIN = 30.0
    B_PLUS_MIN = 45.0
    A_MIN = 55.0
    A_PLUS_MIN = 75.0

    # ------------------------------------------------------------------
    # Locked A+ mandatory gates
    # ------------------------------------------------------------------

    A_PLUS_EVIDENCE_MIN = 85.0
    A_PLUS_RR_MIN = 3.0
    A_PLUS_EQE_MIN = 85.0
    A_PLUS_PFS_MIN = 80.0
    A_PLUS_LQS_MIN = 75.0
    A_PLUS_MTS_MIN = 80.0

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _float(
        value: Any,
        default: float | None = None,
    ) -> float | None:
        """Safely convert a value to float."""
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _upper(
        value: Any,
        default: str = "",
    ) -> str:
        """Normalize a value to uppercase text."""
        if value is None:
            return default

        return str(value).strip().upper()

    @staticmethod
    def _mapping(value: Any) -> Mapping[str, Any]:
        """Return a mapping or an empty mapping."""
        if isinstance(value, Mapping):
            return value

        return {}

    @classmethod
    def _component(
        cls,
        components: Mapping[str, Any],
        name: str,
    ) -> float | None:
        """Read one existing component without inventing a value."""
        return cls._float(components.get(name))

    @classmethod
    def _component_values(
        cls,
        components: Mapping[str, Any],
    ) -> list[float]:
        """Return only actually available numeric components."""

        values: list[float] = []

        for name in cls.REQUIRED_COMPONENTS:
            value = cls._component(components, name)

            if value is None:
                continue

            values.append(
                max(
                    0.0,
                    min(100.0, value),
                )
            )

        return values

    @staticmethod
    def _grade(score: float) -> str:
        """
        Locked score-band mapping.

        <30       -> NO_TRADE
        30-44.99  -> B
        45-54.99  -> B+
        55-74.99  -> A
        75-100    -> A+
        """

        score = max(0.0, min(100.0, score))

        if score < 30.0:
            return "NO_TRADE"

        if score < 45.0:
            return "B"

        if score < 55.0:
            return "B+"

        if score < 75.0:
            return "A"

        return "A+"

    @staticmethod
    def _direction_to_action(direction: str) -> str:
        if direction == "BULLISH":
            return "BUY"

        if direction == "BEARISH":
            return "SELL"

        return "HOLD"

    @staticmethod
    def _bool_value(value: Any) -> bool | None:
        """
        Parse an explicitly supplied boolean-like value.

        Unknown/missing values return None.

        No inference is performed.
        """

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            if value == 1:
                return True

            if value == 0:
                return False

            return None

        if isinstance(value, str):
            normalized = value.strip().upper()

            if normalized in {
                "TRUE",
                "YES",
                "Y",
                "1",
                "EXPANDING",
                "POSITIVE",
                "BUY",
                "BUY_IMBALANCE",
            }:
                return True

            if normalized in {
                "FALSE",
                "NO",
                "N",
                "0",
                "CONTRACTING",
                "NEGATIVE",
                "SELL",
                "SELL_IMBALANCE",
            }:
                return False

        return None

    # ------------------------------------------------------------------
    # Backend value access
    # ------------------------------------------------------------------

    @classmethod
    def _market_value(
        cls,
        data: StrategyInput,
        key: str,
    ) -> Any:
        """
        Read a value already supplied by upstream intelligence.

        Search order:
            metadata
            components

        No calculated fallback is used.
        """

        metadata = cls._mapping(data.metadata)

        if key in metadata:
            return metadata.get(key)

        components = cls._mapping(data.components)

        if key in components:
            return components.get(key)

        return None

    # ------------------------------------------------------------------
    # A+ mandatory gates
    # ------------------------------------------------------------------

    @classmethod
    def _evaluate_a_plus_gates(
        cls,
        data: StrategyInput,
    ) -> tuple[bool, tuple[str, ...]]:
        """
        Evaluate the locked A+ mandatory gates.

        Missing information is NOT interpreted as passing.

        This is intentionally conservative because the upstream
        AutoROBOMLM mapper currently does not prove all crypto-specific
        fields are present.
        """

        reasons: list[str] = []

        evidence = cls._float(
            cls._market_value(data, "evidence")
        )

        rr = cls._float(data.risk_reward)

        eqe = cls._float(
            cls._market_value(data, "eqe")
        )

        pfs = cls._float(
            cls._market_value(data, "pfs")
        )

        lqs = cls._float(
            cls._market_value(data, "lqs")
        )

        mts = cls._float(
            cls._market_value(data, "mts")
        )

        oi_expansion = cls._bool_value(
            cls._market_value(data, "oi_expansion")
        )

        positive_delta = cls._bool_value(
            cls._market_value(data, "positive_delta")
        )

        footprint_buy_imbalance = cls._bool_value(
            cls._market_value(
                data,
                "footprint_buy_imbalance",
            )
        )

        # --------------------------------------------------------------
        # Evidence
        # --------------------------------------------------------------

        if evidence is None:
            reasons.append(
                "A_PLUS_EVIDENCE_UNAVAILABLE"
            )
        elif evidence < cls.A_PLUS_EVIDENCE_MIN:
            reasons.append(
                "A_PLUS_EVIDENCE_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # Risk / Reward
        # --------------------------------------------------------------

        if rr is None:
            reasons.append(
                "A_PLUS_RR_UNAVAILABLE"
            )
        elif rr < cls.A_PLUS_RR_MIN:
            reasons.append(
                "A_PLUS_RR_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # EQE
        # --------------------------------------------------------------

        if eqe is None:
            reasons.append(
                "A_PLUS_EQE_UNAVAILABLE"
            )
        elif eqe < cls.A_PLUS_EQE_MIN:
            reasons.append(
                "A_PLUS_EQE_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # PFS
        # --------------------------------------------------------------

        if pfs is None:
            reasons.append(
                "A_PLUS_PFS_UNAVAILABLE"
            )
        elif pfs < cls.A_PLUS_PFS_MIN:
            reasons.append(
                "A_PLUS_PFS_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # LQS
        # --------------------------------------------------------------

        if lqs is None:
            reasons.append(
                "A_PLUS_LQS_UNAVAILABLE"
            )
        elif lqs < cls.A_PLUS_LQS_MIN:
            reasons.append(
                "A_PLUS_LQS_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # MTS
        # --------------------------------------------------------------

        if mts is None:
            reasons.append(
                "A_PLUS_MTS_UNAVAILABLE"
            )
        elif mts < cls.A_PLUS_MTS_MIN:
            reasons.append(
                "A_PLUS_MTS_GATE_FAILED"
            )

        # --------------------------------------------------------------
        # OI expansion
        # --------------------------------------------------------------

        if oi_expansion is not True:
            if oi_expansion is None:
                reasons.append(
                    "A_PLUS_OI_EXPANSION_UNAVAILABLE"
                )
            else:
                reasons.append(
                    "A_PLUS_OI_EXPANSION_GATE_FAILED"
                )

        # --------------------------------------------------------------
        # Positive delta
        # --------------------------------------------------------------

        if positive_delta is not True:
            if positive_delta is None:
                reasons.append(
                    "A_PLUS_DELTA_UNAVAILABLE"
                )
            else:
                reasons.append(
                    "A_PLUS_DELTA_GATE_FAILED"
                )

        # --------------------------------------------------------------
        # Footprint buy imbalance
        # --------------------------------------------------------------

        if footprint_buy_imbalance is not True:
            if footprint_buy_imbalance is None:
                reasons.append(
                    "A_PLUS_FOOTPRINT_UNAVAILABLE"
                )
            else:
                reasons.append(
                    "A_PLUS_FOOTPRINT_GATE_FAILED"
                )

        return (
            len(reasons) == 0,
            tuple(reasons),
        )

    # ------------------------------------------------------------------
    # Crypto setup classification
    # ------------------------------------------------------------------

    @classmethod
    def _classify_setup(
        cls,
        data: StrategyInput,
    ) -> str:
        """
        Interpret existing intelligence into a crypto setup.

        This does NOT calculate a new indicator.
        """

        direction = cls._upper(
            data.direction,
            "NEUTRAL",
        )

        components = cls._mapping(data.components)

        flow = cls._component(
            components,
            "flow",
        )

        derivative = cls._component(
            components,
            "derivative",
        )

        volume = cls._component(
            components,
            "volume",
        )

        obstacle = cls._component(
            components,
            "obstacle",
        )

        context = cls._component(
            components,
            "context",
        )

        regime = cls._component(
            components,
            "regime",
        )

        flow_v = flow if flow is not None else 0.0
        derivative_v = (
            derivative
            if derivative is not None
            else 0.0
        )
        volume_v = (
            volume
            if volume is not None
            else 0.0
        )
        obstacle_v = (
            obstacle
            if obstacle is not None
            else 0.0
        )
        context_v = (
            context
            if context is not None
            else 0.0
        )
        regime_v = (
            regime
            if regime is not None
            else 0.0
        )

        # --------------------------------------------------------------
        # Trend continuation
        # --------------------------------------------------------------

        if (
            direction in {"BULLISH", "BEARISH"}
            and flow_v >= 70.0
            and volume_v >= 65.0
            and context_v >= 60.0
            and regime_v >= 60.0
        ):
            return "CRYPTO_TREND_CONTINUATION"

        # --------------------------------------------------------------
        # Breakout
        # --------------------------------------------------------------

        if (
            direction in {"BULLISH", "BEARISH"}
            and volume_v >= 70.0
            and obstacle_v >= 60.0
            and flow_v >= 55.0
        ):
            return "CRYPTO_BREAKOUT"

        # --------------------------------------------------------------
        # Squeeze
        # --------------------------------------------------------------

        if (
            direction in {"BULLISH", "BEARISH"}
            and derivative_v >= 70.0
            and flow_v >= 55.0
            and volume_v >= 55.0
        ):
            return "CRYPTO_SQUEEZE"

        # --------------------------------------------------------------
        # Reversal
        # --------------------------------------------------------------

        if (
            direction in {"BULLISH", "BEARISH"}
            and obstacle_v >= 65.0
            and context_v >= 55.0
            and flow_v >= 50.0
        ):
            return "CRYPTO_REVERSAL"

        # --------------------------------------------------------------
        # Distribution
        # --------------------------------------------------------------

        if (
            direction == "BEARISH"
            and obstacle_v >= 60.0
            and flow_v < 50.0
            and context_v >= 50.0
        ):
            return "CRYPTO_DISTRIBUTION"

        return "CRYPTO_UNCLASSIFIED"

    # ------------------------------------------------------------------
    # Strategy score
    # ------------------------------------------------------------------

    @classmethod
    def _calculate_score(
        cls,
        data: StrategyInput,
    ) -> tuple[float, float, float]:
        """
        Calculate:

            strategy_score
            timing_quality
            risk_quality

        from existing StrategyInput values only.
        """

        components = cls._mapping(
            data.components
        )

        flow = cls._component(
            components,
            "flow",
        )

        derivative = cls._component(
            components,
            "derivative",
        )

        volume = cls._component(
            components,
            "volume",
        )

        obstacle = cls._component(
            components,
            "obstacle",
        )

        context = cls._component(
            components,
            "context",
        )

        regime = cls._component(
            components,
            "regime",
        )

        values = cls._component_values(
            components
        )

        if values:
            component_average = (
                sum(values) / len(values)
            )
        else:
            component_average = 0.0

        strength = max(
            0.0,
            min(
                100.0,
                cls._float(
                    data.strength,
                    0.0,
                ) or 0.0,
            ),
        )

        confidence = max(
            0.0,
            min(
                100.0,
                cls._float(
                    data.confidence,
                    0.0,
                ) or 0.0,
            ),
        )

        flow_v = (
            flow if flow is not None else 0.0
        )

        derivative_v = (
            derivative
            if derivative is not None
            else 0.0
        )

        volume_v = (
            volume
            if volume is not None
            else 0.0
        )

        obstacle_v = (
            obstacle
            if obstacle is not None
            else 0.0
        )

        context_v = (
            context
            if context is not None
            else 0.0
        )

        regime_v = (
            regime
            if regime is not None
            else 0.0
        )

        # --------------------------------------------------------------
        # Timing quality
        # --------------------------------------------------------------

        timing_quality = (
            flow_v * 0.40
            + volume_v * 0.35
            + obstacle_v * 0.25
        )

        # --------------------------------------------------------------
        # Risk quality
        # --------------------------------------------------------------

        risk_quality = (
            context_v * 0.40
            + regime_v * 0.40
            + derivative_v * 0.20
        )

        # --------------------------------------------------------------
        # Core strategy score
        # --------------------------------------------------------------

        strategy_score = (
            strength * 0.25
            + confidence * 0.25
            + component_average * 0.20
            + timing_quality * 0.15
            + risk_quality * 0.15
        )

        return (
            max(
                0.0,
                min(100.0, strategy_score),
            ),
            max(
                0.0,
                min(100.0, timing_quality),
            ),
            max(
                0.0,
                min(100.0, risk_quality),
            ),
        )

    # ------------------------------------------------------------------
    # Rejection helper
    # ------------------------------------------------------------------

    def _reject(
        self,
        direction: str,
        reason: str,
        strategy_score: float = 0.0,
        confidence: float = 0.0,
        timing_quality: float = 0.0,
        risk_quality: float = 0.0,
        notes: str = "",
    ) -> StrategyOutput:
        """Create a rejected StrategyOutput."""

        return StrategyOutput(
            strategy_id=self.ID,
            direction=direction,
            entry_permission=False,
            strategy_score=max(
                0.0,
                min(100.0, strategy_score),
            ),
            confidence=max(
                0.0,
                min(100.0, confidence),
            ),
            timing_quality=max(
                0.0,
                min(100.0, timing_quality),
            ),
            risk_quality=max(
                0.0,
                min(100.0, risk_quality),
            ),
            reason_codes=(reason,),
            notes=notes,
        )

    # ------------------------------------------------------------------
    # Main decision
    # ------------------------------------------------------------------

    def decide(
        self,
        data: StrategyInput,
    ) -> StrategyOutput:
        """
        Evaluate one crypto signal.

        Returns StrategyOutput only.

        No order or position is created here.
        """

        direction = self._upper(
            data.direction,
            "NEUTRAL",
        )

        action = self._upper(
            data.action,
            "HOLD",
        )

        strength = max(
            0.0,
            min(
                100.0,
                self._float(
                    data.strength,
                    0.0,
                ) or 0.0,
            ),
        )

        confidence = max(
            0.0,
            min(
                100.0,
                self._float(
                    data.confidence,
                    0.0,
                ) or 0.0,
            ),
        )

        # ==============================================================
        # 1. Direction validation
        # ==============================================================

        if direction not in {
            "BULLISH",
            "BEARISH",
        }:
            return self._reject(
                direction=direction,
                reason="CRYPTO_NON_DIRECTIONAL",
                confidence=confidence,
                notes=(
                    "Crypto strategy requires a "
                    "directional market state."
                ),
            )

        expected_action = (
            self._direction_to_action(
                direction
            )
        )

        if action not in {
            "BUY",
            "SELL",
            "HOLD",
        }:
            return self._reject(
                direction=direction,
                reason="CRYPTO_INVALID_ACTION",
                confidence=confidence,
            )

        # HOLD is not converted into a grade.
        if action == "HOLD":
            return self._reject(
                direction=direction,
                reason="CRYPTO_HOLD",
                confidence=confidence,
                notes=(
                    "HOLD is not converted into "
                    "a trade grade."
                ),
            )

        if action != expected_action:
            return self._reject(
                direction=direction,
                reason="CRYPTO_DIRECTION_ACTION_CONFLICT",
                confidence=confidence,
            )

        # ==============================================================
        # 2. Strength gate
        # ==============================================================

        if strength < self.MIN_DIRECTIONAL_STRENGTH:
            return self._reject(
                direction=direction,
                reason="CRYPTO_STRENGTH_GATE_FAILED",
                confidence=confidence,
                notes=f"strength={strength:.2f}",
            )

        # ==============================================================
        # 3. Confidence gate
        # ==============================================================

        if confidence < self.MIN_CONFIDENCE:
            return self._reject(
                direction=direction,
                reason="CRYPTO_CONFIDENCE_GATE_FAILED",
                confidence=confidence,
                notes=f"confidence={confidence:.2f}",
            )

        # ==============================================================
        # 4. Strategy score
        # ==============================================================

        (
            strategy_score,
            timing_quality,
            risk_quality,
        ) = self._calculate_score(data)

        # ==============================================================
        # 5. Crypto setup
        # ==============================================================

        setup = self._classify_setup(data)

        # ==============================================================
        # 6. Score grade
        # ==============================================================

        grade = self._grade(strategy_score)

        # ==============================================================
        # 7. Hard NO_TRADE
        # ==============================================================

        if strategy_score < self.B_MIN:
            return self._reject(
                direction=direction,
                reason="CRYPTO_SCORE_BELOW_B",
                strategy_score=strategy_score,
                confidence=confidence,
                timing_quality=timing_quality,
                risk_quality=risk_quality,
                notes=(
                    f"setup={setup}; "
                    f"grade=NO_TRADE"
                ),
            )

        # ==============================================================
        # 8. A+ mandatory gates
        # ==============================================================

        a_plus_pass, a_plus_reasons = (
            self._evaluate_a_plus_gates(data)
        )

        # ==============================================================
        # 9. A+ demotion
        # ==============================================================

        if (
            grade == "A+"
            and not a_plus_pass
        ):
            # A+ is invalid without ALL mandatory gates.
            #
            # The trade is demoted according to its score band.
            if strategy_score >= self.A_MIN:
                grade = "A"

            elif strategy_score >= self.B_PLUS_MIN:
                grade = "B+"

            else:
                grade = "B"

        # ==============================================================
        # 10. Reason codes
        # ==============================================================

        reason_codes: list[str] = [
            f"CRYPTO_SETUP:{setup}",
            f"CRYPTO_GRADE:{grade}",
        ]

        if (
            strategy_score >= self.A_PLUS_MIN
        ):
            if a_plus_pass:
                reason_codes.append(
                    "CRYPTO_A_PLUS_GATES_PASSED"
                )
            else:
                reason_codes.extend(
                    a_plus_reasons
                )

        if grade == "B":
            reason_codes.append(
                "CRYPTO_SCORE_BAND_B"
            )

        elif grade == "B+":
            reason_codes.append(
                "CRYPTO_SCORE_BAND_B_PLUS"
            )

        elif grade == "A":
            reason_codes.append(
                "CRYPTO_SCORE_BAND_A"
            )

        elif grade == "A+":
            reason_codes.append(
                "CRYPTO_SCORE_BAND_A_PLUS"
            )

        # ==============================================================
        # 11. Notes
        # ==============================================================

        notes = (
            f"setup={setup}; "
            f"grade={grade}; "
            f"score={strategy_score:.2f}; "
            f"timing={timing_quality:.2f}; "
            f"risk_quality={risk_quality:.2f}"
        )

        # ==============================================================
        # 12. Strategy permission
        # ==============================================================

        # True here means only that the CryptoStrategy accepts the
        # signal. Downstream AutoROBOMLM/risk/execution gates remain
        # authoritative.
        entry_permission = True

        return StrategyOutput(
            strategy_id=self.ID,
            direction=direction,
            entry_permission=entry_permission,
            strategy_score=round(
                strategy_score,
                4,
            ),
            confidence=round(
                confidence,
                4,
            ),
            timing_quality=round(
                timing_quality,
                4,
            ),
            risk_quality=round(
                risk_quality,
                4,
            ),
            reason_codes=tuple(
                reason_codes
            ),
            notes=notes,
        )


__all__ = ["CryptoStrategy"]