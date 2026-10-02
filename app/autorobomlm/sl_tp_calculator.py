"""
ROBOMLM_PLUS - AutoROBOMLM SL/TP Calculator

Purpose:
    Compute stop-loss and take-profit levels.

Method:
    ATR-based:
        SL = entry -/+ (sl_atr_multiplier * ATR)
        TP = entry +/- (tp_atr_multiplier * ATR)
    Fallback (ATR unavailable):
        SL = entry -/+ (sl_fallback_pct% of entry)
        TP = entry +/- (tp_fallback_pct% of entry)

Design:
    - No fabricated ATR.
    - Missing inputs -> INSUFFICIENT.
    - Invalid inputs -> INVALID.
    - Direction-aware (BUY vs SELL).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional


SLTP_NAME = "AutoROBOMLM_SLTPCalculator"
SLTP_VERSION = "1.0"


class SLTPStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class TradeDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class SLTPRequest:
    direction: TradeDirection
    entry_price: Optional[float]
    atr: Optional[float] = None
    sl_atr_multiplier: float = 1.5
    tp_atr_multiplier: float = 3.0
    sl_fallback_pct: float = 1.5
    tp_fallback_pct: float = 3.0
    metadata: Mapping = field(default_factory=dict)


@dataclass(frozen=True)
class SLTPResult:
    status: SLTPStatus
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward_ratio: Optional[float]
    used_atr: bool
    reasons: tuple = ()
    errors: tuple = ()
    engine: str = SLTP_NAME
    version: str = SLTP_VERSION

    def as_dict(self):
        return {
            "status": self.status.value,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_reward_ratio": self.risk_reward_ratio,
            "used_atr": self.used_atr,
            "reasons": list(self.reasons),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
        }


class SLTPCalculator:
    def calculate(self, req: SLTPRequest) -> SLTPResult:
        if not isinstance(req.direction, TradeDirection):
            return self._invalid("direction must be a TradeDirection.")

        if req.entry_price is None:
            return self._insufficient("entry_price is required.")

        err = self._validate_positive(req.entry_price, "entry_price")
        if err:
            return self._invalid(err)

        for name, value in (
            ("sl_atr_multiplier", req.sl_atr_multiplier),
            ("tp_atr_multiplier", req.tp_atr_multiplier),
            ("sl_fallback_pct", req.sl_fallback_pct),
            ("tp_fallback_pct", req.tp_fallback_pct),
        ):
            err = self._validate_positive(value, name)
            if err:
                return self._invalid(err)

        entry = float(req.entry_price)
        sl_mult = float(req.sl_atr_multiplier)
        tp_mult = float(req.tp_atr_multiplier)

        used_atr = False
        reasons = []

        # ATR path
        if req.atr is not None:
            err = self._validate_positive(req.atr, "atr")
            if err:
                return self._invalid(err)
            atr = float(req.atr)
            sl_distance = sl_mult * atr
            tp_distance = tp_mult * atr
            used_atr = True
            reasons.append(
                f"ATR-based SL/TP: ATR={atr:.8f}, "
                f"SL={sl_mult}x, TP={tp_mult}x."
            )
        else:
            # Fallback
            sl_distance = entry * float(req.sl_fallback_pct) / 100.0
            tp_distance = entry * float(req.tp_fallback_pct) / 100.0
            reasons.append(
                f"Fallback SL/TP: SL={req.sl_fallback_pct}%, "
                f"TP={req.tp_fallback_pct}% of entry."
            )

        if sl_distance <= 0.0 or tp_distance <= 0.0:
            return self._invalid(
                "Computed SL/TP distance must be > 0."
            )

        if req.direction == TradeDirection.BUY:
            stop_loss = entry - sl_distance
            take_profit = entry + tp_distance
        else:
            stop_loss = entry + sl_distance
            take_profit = entry - tp_distance

        if stop_loss <= 0.0 or take_profit <= 0.0:
            return self._invalid(
                "Computed SL/TP levels must be positive."
            )

        rr = tp_distance / sl_distance if sl_distance > 0 else None

        return SLTPResult(
            status=SLTPStatus.VALID,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=rr,
            used_atr=used_atr,
            reasons=tuple(reasons),
        )

    @staticmethod
    def _validate_positive(value, name):
        if isinstance(value, bool):
            return f"{name} cannot be boolean."
        if not isinstance(value, (int, float)):
            return f"{name} must be numeric."
        if not isfinite(float(value)):
            return f"{name} must be finite."
        if float(value) <= 0.0:
            return f"{name} must be > 0."
        return None

    @staticmethod
    def _invalid(error):
        return SLTPResult(
            status=SLTPStatus.INVALID,
            stop_loss=None, take_profit=None,
            risk_reward_ratio=None, used_atr=False,
            errors=(error,),
        )

    @staticmethod
    def _insufficient(reason):
        return SLTPResult(
            status=SLTPStatus.INSUFFICIENT,
            stop_loss=None, take_profit=None,
            risk_reward_ratio=None, used_atr=False,
            reasons=(reason,),
        )


def calculate_sl_tp(
    *,
    direction,
    entry_price,
    atr=None,
    sl_atr_multiplier=1.5,
    tp_atr_multiplier=3.0,
    sl_fallback_pct=1.5,
    tp_fallback_pct=3.0,
) -> SLTPResult:
    return SLTPCalculator().calculate(
        SLTPRequest(
            direction=direction,
            entry_price=entry_price,
            atr=atr,
            sl_atr_multiplier=sl_atr_multiplier,
            tp_atr_multiplier=tp_atr_multiplier,
            sl_fallback_pct=sl_fallback_pct,
            tp_fallback_pct=tp_fallback_pct,
        )
    )


__all__ = [
    "SLTP_NAME", "SLTP_VERSION",
    "SLTPStatus", "TradeDirection",
    "SLTPRequest", "SLTPResult",
    "SLTPCalculator", "calculate_sl_tp",
]
