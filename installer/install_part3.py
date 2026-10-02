"""AutoROBOMLM installer part 3 - capital_allocator + sl_tp_calculator"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
ROOT.mkdir(parents=True, exist_ok=True)

FILES = {}

FILES["capital_allocator.py"] = '''"""
ROBOMLM_PLUS - AutoROBOMLM Capital Allocator

Purpose:
    Compute position size for a proposed trade.

Method:
    Risk-based sizing:
        risk_amount      = capital * risk_per_trade_pct / 100
        stop_distance    = abs(entry_price - stop_loss)
        raw_quantity     = risk_amount / stop_distance
        position_value   = raw_quantity * entry_price
        max_value        = capital * max_position_pct / 100
        final_quantity   = min(raw_quantity, max_value / entry_price)

Design:
    - No fabricated values.
    - Missing inputs -> INSUFFICIENT.
    - Invalid inputs -> INVALID.
    - No execution authority.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional


ALLOCATOR_NAME = "AutoROBOMLM_CapitalAllocator"
ALLOCATOR_VERSION = "1.0"


class AllocatorStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


@dataclass(frozen=True)
class AllocationRequest:
    capital: Optional[float]
    entry_price: Optional[float]
    stop_loss: Optional[float]
    risk_per_trade_pct: float = 1.0
    max_position_pct: float = 10.0
    min_quantity: Optional[float] = None
    quantity_step: Optional[float] = None
    metadata: Mapping = field(default_factory=dict)


@dataclass(frozen=True)
class AllocationResult:
    status: AllocatorStatus
    quantity: Optional[float]
    position_value: Optional[float]
    risk_amount: Optional[float]
    stop_distance: Optional[float]
    stop_distance_pct: Optional[float]
    capped_by_max_position: bool = False
    reasons: tuple = ()
    errors: tuple = ()
    engine: str = ALLOCATOR_NAME
    version: str = ALLOCATOR_VERSION

    def as_dict(self):
        return {
            "status": self.status.value,
            "quantity": self.quantity,
            "position_value": self.position_value,
            "risk_amount": self.risk_amount,
            "stop_distance": self.stop_distance,
            "stop_distance_pct": self.stop_distance_pct,
            "capped_by_max_position": self.capped_by_max_position,
            "reasons": list(self.reasons),
            "errors": list(self.errors),
            "engine": self.engine,
            "version": self.version,
        }


class CapitalAllocator:
    def __init__(self):
        pass

    def allocate(self, req: AllocationRequest) -> AllocationResult:
        # Validate presence
        if req.capital is None:
            return self._insufficient("capital is required.")
        if req.entry_price is None:
            return self._insufficient("entry_price is required.")
        if req.stop_loss is None:
            return self._insufficient("stop_loss is required.")

        # Validate numeric
        for name, value in (
            ("capital", req.capital),
            ("entry_price", req.entry_price),
            ("stop_loss", req.stop_loss),
        ):
            err = self._validate_number(value, name)
            if err:
                return self._invalid(err)

        err = self._validate_number(
            req.risk_per_trade_pct, "risk_per_trade_pct"
        )
        if err:
            return self._invalid(err)
        err = self._validate_number(
            req.max_position_pct, "max_position_pct"
        )
        if err:
            return self._invalid(err)

        capital = float(req.capital)
        entry = float(req.entry_price)
        sl = float(req.stop_loss)
        risk_pct = float(req.risk_per_trade_pct)
        max_pct = float(req.max_position_pct)

        if capital <= 0.0:
            return self._invalid("capital must be > 0.")
        if entry <= 0.0:
            return self._invalid("entry_price must be > 0.")
        if sl <= 0.0:
            return self._invalid("stop_loss must be > 0.")
        if not (0.0 < risk_pct <= 100.0):
            return self._invalid("risk_per_trade_pct must be (0, 100].")
        if not (0.0 < max_pct <= 100.0):
            return self._invalid("max_position_pct must be (0, 100].")
        if risk_pct > max_pct:
            return self._invalid(
                "risk_per_trade_pct cannot exceed max_position_pct."
            )

        stop_distance = abs(entry - sl)
        if stop_distance <= 0.0:
            return self._invalid(
                "stop_loss must differ from entry_price."
            )

        risk_amount = capital * risk_pct / 100.0
        raw_quantity = risk_amount / stop_distance
        raw_value = raw_quantity * entry

        max_value = capital * max_pct / 100.0
        capped = False
        final_quantity = raw_quantity
        final_value = raw_value

        if raw_value > max_value:
            capped = True
            final_quantity = max_value / entry
            final_value = final_quantity * entry

        # Apply min_quantity if provided
        if req.min_quantity is not None:
            min_q = float(req.min_quantity)
            if final_quantity < min_q:
                return AllocationResult(
                    status=AllocatorStatus.INSUFFICIENT,
                    quantity=None,
                    position_value=None,
                    risk_amount=risk_amount,
                    stop_distance=stop_distance,
                    stop_distance_pct=stop_distance / entry * 100.0,
                    reasons=(
                        f"Computed quantity {final_quantity:.8f} is below "
                        f"min_quantity {min_q}.",
                    ),
                )

        # Apply quantity_step if provided
        if req.quantity_step is not None:
            step = float(req.quantity_step)
            if step <= 0.0:
                return self._invalid("quantity_step must be > 0.")
            final_quantity = (final_quantity // step) * step
            final_value = final_quantity * entry

        if final_quantity <= 0.0:
            return self._invalid(
                "Final quantity after constraints is <= 0."
            )

        stop_distance_pct = (stop_distance / entry) * 100.0

        reasons = []
        reasons.append(
            f"Risk {risk_pct}% of capital = {risk_amount:.4f}."
        )
        reasons.append(
            f"Stop distance = {stop_distance:.8f} "
            f"({stop_distance_pct:.4f}%)."
        )
        if capped:
            reasons.append(
                f"Position capped by max_position_pct "
                f"({max_pct}% of capital)."
            )

        return AllocationResult(
            status=AllocatorStatus.VALID,
            quantity=final_quantity,
            position_value=final_value,
            risk_amount=risk_amount,
            stop_distance=stop_distance,
            stop_distance_pct=stop_distance_pct,
            capped_by_max_position=capped,
            reasons=tuple(reasons),
        )

    @staticmethod
    def _validate_number(value, name):
        if isinstance(value, bool):
            return f"{name} cannot be boolean."
        if not isinstance(value, (int, float)):
            return f"{name} must be numeric."
        if not isfinite(float(value)):
            return f"{name} must be finite."
        return None

    @staticmethod
    def _invalid(error):
        return AllocationResult(
            status=AllocatorStatus.INVALID,
            quantity=None, position_value=None,
            risk_amount=None, stop_distance=None,
            stop_distance_pct=None,
            errors=(error,),
        )

    @staticmethod
    def _insufficient(reason):
        return AllocationResult(
            status=AllocatorStatus.INSUFFICIENT,
            quantity=None, position_value=None,
            risk_amount=None, stop_distance=None,
            stop_distance_pct=None,
            reasons=(reason,),
        )


def allocate_capital(
    *,
    capital,
    entry_price,
    stop_loss,
    risk_per_trade_pct=1.0,
    max_position_pct=10.0,
    min_quantity=None,
    quantity_step=None,
) -> AllocationResult:
    return CapitalAllocator().allocate(
        AllocationRequest(
            capital=capital,
            entry_price=entry_price,
            stop_loss=stop_loss,
            risk_per_trade_pct=risk_per_trade_pct,
            max_position_pct=max_position_pct,
            min_quantity=min_quantity,
            quantity_step=quantity_step,
        )
    )


__all__ = [
    "ALLOCATOR_NAME", "ALLOCATOR_VERSION",
    "AllocatorStatus",
    "AllocationRequest", "AllocationResult",
    "CapitalAllocator", "allocate_capital",
]
'''

FILES["sl_tp_calculator.py"] = '''"""
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
'''

for filename, content in FILES.items():
    path = ROOT / filename
    path.write_text(content, encoding="utf-8")
    print(f"WROTE: {path}")

print()
print(f"DONE. Files in {ROOT}:")
for p in sorted(ROOT.glob("*.py")):
    print(f"  {p.name} ({p.stat().st_size} bytes)")