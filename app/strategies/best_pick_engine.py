"""Best Pick Engine — Ranking + Sizing + Duration.

Picks the BEST opportunity from universe, not the FIRST.
Includes:
  - Trade quality filter (RR 2:1+, confidence, freshness)
  - Ranking formula (grade × RR × confidence × freshness × MTF)
  - Dynamic position sizing (grade + footprint + wall break + trend)
  - Multi-TF duration prediction

New module. Nothing existing touched.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


# ============================================================
# DATA
# ============================================================

@dataclass(frozen=True)
class SignalCandidate:
    symbol: str
    direction: str              # BULLISH | BEARISH | NEUTRAL
    action: str                 # BUY | SELL | HOLD
    grade: str                  # A+ | A | B+ | B | HOLD
    confidence: float           # 0-100
    strength: float             # 0-100
    rr_actual: float            # real RR (backend ATR-based = 2.0)
    age_minutes: float          # signal age
    mtf_15m: str                # BULLISH | BEARISH | NEUTRAL
    mtf_1h: str
    mtf_4h: str
    mm_footprint: bool = False  # market maker wall detected
    wall_break: bool = False    # resistance/support broken
    volume_change_pct: float = 0.0
    oi_change_pct: float = 0.0
    volatility_ratio: float = 1.0  # current / normal
    trend_continuation: float = 0.0  # 0-1, how likely to continue


@dataclass(frozen=True)
class RankedSignal:
    candidate: SignalCandidate
    rank_score: float
    position_size_pct: float
    duration_estimate_min: int
    tp_extension_allowed: bool
    reasons: tuple = ()


# ============================================================
# THRESHOLDS
# ============================================================

MIN_RR = 2.0
MIN_CONFIDENCE = 65.0
MAX_AGE_MIN = 10.0
MAX_POSITION_PCT = 3.0
MIN_POSITION_PCT = 0.3


GRADE_WEIGHT = {
    "A+": 1.00,
    "A": 0.75,
    "B+": 0.45,
    "B": 0.20,
    "HOLD": 0.0,
}

GRADE_SIZE = {
    "A+": 2.5,
    "A": 2.0,
    "B+": 1.0,
    "B": 0.5,
    "HOLD": 0.0,
}


# ============================================================
# ENGINE
# ============================================================

class BestPickEngine:

    # ---------- FILTERS ----------

    def _passes_hard_filters(self, c: SignalCandidate) -> tuple[bool, str]:
        if c.grade == "HOLD":
            return False, "grade_hold"
        if c.rr_actual < MIN_RR:
            return False, f"rr_low_{c.rr_actual:.2f}"
        if c.confidence < MIN_CONFIDENCE:
            return False, f"conf_low_{c.confidence:.1f}"
        if c.age_minutes > MAX_AGE_MIN:
            return False, f"stale_{c.age_minutes:.1f}m"
        if c.direction not in ("BULLISH", "BEARISH"):
            return False, "direction_neutral"
        return True, "ok"

    # ---------- SCORE COMPONENTS ----------

    def _rr_mult(self, rr: float) -> float:
        if rr < 2.0:
            return 0.0
        if rr < 3.0:
            return 0.8
        if rr < 5.0:
            return 1.0
        return 1.3

    def _conf_mult(self, conf: float) -> float:
        if conf < 65.0:
            return 0.0
        if conf < 75.0:
            return 0.8
        if conf < 85.0:
            return 1.0
        return 1.2

    def _fresh_mult(self, age_min: float) -> float:
        if age_min <= 2.0:
            return 1.0
        if age_min <= 5.0:
            return 0.7
        if age_min <= 10.0:
            return 0.4
        return 0.0

    def _mtf_mult(self, c: SignalCandidate) -> tuple[float, int]:
        """How many TF align with the signal direction?"""
        aligned = 0
        for tf in (c.mtf_15m, c.mtf_1h, c.mtf_4h):
            if tf == c.direction:
                aligned += 1

        if aligned == 3:
            return 1.3, aligned
        if aligned == 2:
            return 1.0, aligned
        if aligned == 1:
            return 0.6, aligned
        return 0.0, 0

    # ---------- SCORE ----------

    def score(self, c: SignalCandidate) -> tuple[float, tuple, int]:
        ok, reason = self._passes_hard_filters(c)
        if not ok:
            return 0.0, (reason,), 0

        gw = GRADE_WEIGHT.get(c.grade, 0.0)
        rr = self._rr_mult(c.rr_actual)
        cf = self._conf_mult(c.confidence)
        fr = self._fresh_mult(c.age_minutes)
        mtf, aligned = self._mtf_mult(c)

        score = gw * rr * cf * fr * mtf

        reasons = (
            f"grade={c.grade}({gw})",
            f"rr={c.rr_actual:.2f}({rr})",
            f"conf={c.confidence:.1f}({cf})",
            f"fresh={c.age_minutes:.1f}m({fr})",
            f"mtf={aligned}/3({mtf})",
        )
        return score, reasons, aligned

    # ---------- POSITION SIZE ----------

    def size(self, c: SignalCandidate) -> tuple[float, tuple]:
        base = GRADE_SIZE.get(c.grade, 0.0)
        if base <= 0.0:
            return 0.0, ("grade_zero",)

        multipliers = []
        m = 1.0

        # confidence
        if c.confidence >= 85.0:
            m *= 1.3
            multipliers.append("conf_high_×1.3")
        elif c.confidence >= 75.0:
            m *= 1.0
        else:
            m *= 0.8
            multipliers.append("conf_med_×0.8")

        # market maker footprint
        if c.mm_footprint:
            m *= 1.2
            multipliers.append("mm_footprint_×1.2")

        # wall break
        if c.wall_break:
            m *= 1.15
            multipliers.append("wall_break_×1.15")

        # volume change
        if c.volume_change_pct >= 100.0:
            m *= 1.2
            multipliers.append("vol_2x_×1.2")
        elif c.volume_change_pct >= 50.0:
            m *= 1.1
            multipliers.append("vol_1.5x_×1.1")

        # OI change
        if abs(c.oi_change_pct) >= 5.0:
            m *= 1.1
            multipliers.append("oi_change_×1.1")

        # volatility
        if c.volatility_ratio > 2.0:
            m *= 0.7
            multipliers.append("vol_high_×0.7")
        elif c.volatility_ratio < 0.5:
            m *= 0.9
            multipliers.append("vol_low_×0.9")

        # trend continuation
        if c.trend_continuation >= 0.7:
            m *= 1.2
            multipliers.append("trend_strong_×1.2")
        elif c.trend_continuation < 0.3:
            m *= 0.7
            multipliers.append("trend_weak_×0.7")

        final = base * m

        # cap
        if final > MAX_POSITION_PCT:
            final = MAX_POSITION_PCT
        if final < MIN_POSITION_PCT:
            final = 0.0  # too small, skip

        return round(final, 3), tuple(multipliers)

    # ---------- DURATION ----------

    def duration(
        self, c: SignalCandidate
    ) -> tuple[int, bool]:
        """Estimate hold duration + whether TP extension is allowed."""
        _, aligned = self._mtf_mult(c)

        # Base duration by alignment
        if aligned == 3:
            base_min = 240          # 4 hours
            extension = True
        elif aligned == 2:
            base_min = 120          # 2 hours
            extension = True
        elif aligned == 1:
            base_min = 45           # 45 min
            extension = False
        else:
            base_min = 15
            extension = False

        # Adjust by grade
        if c.grade == "A+":
            base_min = int(base_min * 1.3)
        elif c.grade == "A":
            base_min = int(base_min * 1.1)
        elif c.grade == "B":
            base_min = int(base_min * 0.7)

        # Adjust by trend continuation
        if c.trend_continuation >= 0.7:
            base_min = int(base_min * 1.2)
            extension = True
        elif c.trend_continuation < 0.3:
            base_min = int(base_min * 0.6)
            extension = False

        # Adjust by volatility
        if c.volatility_ratio > 2.0:
            base_min = int(base_min * 0.6)

        return max(15, base_min), extension

    # ---------- MAIN ----------

    def rank(
        self, candidates: Iterable[SignalCandidate]
    ) -> list[RankedSignal]:
        ranked = []
        for c in candidates:
            score, reasons, _ = self.score(c)
            if score <= 0.0:
                continue
            size, size_reasons = self.size(c)
            if size <= 0.0:
                continue
            dur, ext = self.duration(c)
            ranked.append(
                RankedSignal(
                    candidate=c,
                    rank_score=round(score, 4),
                    position_size_pct=size,
                    duration_estimate_min=dur,
                    tp_extension_allowed=ext,
                    reasons=tuple(reasons) + tuple(size_reasons),
                )
            )

        ranked.sort(key=lambda r: r.rank_score, reverse=True)
        return ranked

    def best(
        self, candidates: Iterable[SignalCandidate]
    ) -> RankedSignal | None:
        ranked = self.rank(candidates)
        return ranked[0] if ranked else None