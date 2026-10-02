"""Install structure_analyzer.py — Real math from OHLCV"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")

FILE = '''"""
ROBOMLM_PLUS - Structure Analyzer

Real mathematical analysis of OHLCV candles.
No hardcoding. Every value computed from raw data.

Per timeframe returns:
    - EMA trend (20 vs 50)
    - Swing structure (HH/HL/LH/LL)
    - BOS / CHOCH detection
    - Momentum % (last N candles)
    - Volume ratio
    - ATR (Wilder)
    - Overall direction: BULLISH / BEARISH / NEUTRAL
    - Confidence: % of signals that agree
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Sequence

from app.intelligence.real.real_market_data import Candle


# ---------------------------------------------------------------------------
# RESULT CONTRACT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class StructureResult:
    symbol: str
    timeframe: str

    direction: str          # BULLISH | BEARISH | NEUTRAL
    confidence: float       # 0-100

    # Trend
    ema20: float
    ema50: float
    ema_bias: str

    # Structure
    structure_bias: str
    bos_detected: bool
    choch_detected: bool
    swing_highs: tuple
    swing_lows: tuple

    # Momentum
    momentum_pct: float
    momentum_bias: str

    # Volume
    volume_ratio: float
    volume_bias: str

    # Volatility
    atr: float
    atr_pct: float

    # Audit
    candle_count: int
    reasons: tuple
    computed_at: datetime

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "confidence": self.confidence,
            "ema20": self.ema20,
            "ema50": self.ema50,
            "ema_bias": self.ema_bias,
            "structure_bias": self.structure_bias,
            "bos_detected": self.bos_detected,
            "choch_detected": self.choch_detected,
            "momentum_pct": self.momentum_pct,
            "momentum_bias": self.momentum_bias,
            "volume_ratio": self.volume_ratio,
            "volume_bias": self.volume_bias,
            "atr": self.atr,
            "atr_pct": self.atr_pct,
            "candle_count": self.candle_count,
            "reasons": list(self.reasons),
            "computed_at": self.computed_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# TIMEFRAME NORMALIZER
# ---------------------------------------------------------------------------

_TF_ALIASES = {
    "3m": "3", "5m": "5", "15m": "15", "30m": "30",
    "1h": "60", "2h": "120", "4h": "240",
}


def normalize_tf(tf: str) -> str:
    t = str(tf).strip().lower()
    return _TF_ALIASES.get(t, t)


# ---------------------------------------------------------------------------
# MATH PRIMITIVES
# ---------------------------------------------------------------------------

def _ema(values, period: int) -> Optional[float]:
    if len(values) < period:
        return None
    k = 2.0 / (period + 1)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1 - k)
    return e


def _atr(candles, period: int = 14) -> Optional[float]:
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, len(candles)):
        h = candles[i].high
        l = candles[i].low
        pc = candles[i - 1].close
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    # Wilder smoothing
    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr


def _detect_swings(candles, lookback: int = 3):
    """
    Fractal swing detection.
    A swing high at index i if high[i] is highest among
    [i-lookback, i+lookback].
    """
    highs = []
    lows = []
    if len(candles) < lookback * 2 + 1:
        return highs, lows

    for i in range(lookback, len(candles) - lookback):
        window = candles[i - lookback : i + lookback + 1]
        h_i = candles[i].high
        l_i = candles[i].low
        if h_i == max(c.high for c in window) and h_i > 0:
            highs.append(h_i)
        if l_i == min(c.low for c in window) and l_i > 0:
            lows.append(l_i)
    return highs, lows


# ---------------------------------------------------------------------------
# STRUCTURE ANALYZER
# ---------------------------------------------------------------------------

class StructureAnalyzer:

    def analyze(
        self,
        symbol: str,
        timeframe: str,
        candles: Sequence[Candle],
    ) -> StructureResult:

        now = datetime.now(timezone.utc)
        reasons = []

        if len(candles) < 30:
            return StructureResult(
                symbol=symbol, timeframe=timeframe,
                direction="NEUTRAL", confidence=0.0,
                ema20=0.0, ema50=0.0, ema_bias="NEUTRAL",
                structure_bias="NEUTRAL", bos_detected=False,
                choch_detected=False,
                swing_highs=(), swing_lows=(),
                momentum_pct=0.0, momentum_bias="NEUTRAL",
                volume_ratio=1.0, volume_bias="NEUTRAL",
                atr=0.0, atr_pct=0.0,
                candle_count=len(candles),
                reasons=("INSUFFICIENT_CANDLES",),
                computed_at=now,
            )

        closes = [c.close for c in candles]

        # --- EMA ---
        ema20 = _ema(closes, 20)
        ema50 = _ema(closes, 50)

        if ema20 is not None and ema50 is not None:
            if ema20 > ema50:
                ema_bias = "BULLISH"
                reasons.append(f"EMA20({ema20:.2f}) > EMA50({ema50:.2f})")
            elif ema20 < ema50:
                ema_bias = "BEARISH"
                reasons.append(f"EMA20({ema20:.2f}) < EMA50({ema50:.2f})")
            else:
                ema_bias = "NEUTRAL"
        else:
            ema20 = ema20 or 0.0
            ema50 = ema50 or 0.0
            ema_bias = "NEUTRAL"

        # --- Swings ---
        swing_highs, swing_lows = _detect_swings(candles, lookback=3)

        # Structure bias from recent swings
        structure_bias = "NEUTRAL"
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            hh = swing_highs[-1] > swing_highs[-2]
            hl = swing_lows[-1] > swing_lows[-2]
            lh = swing_highs[-1] < swing_highs[-2]
            ll = swing_lows[-1] < swing_lows[-2]

            if hh and hl:
                structure_bias = "BULLISH"
                reasons.append("Higher High + Higher Low")
            elif lh and ll:
                structure_bias = "BEARISH"
                reasons.append("Lower High + Lower Low")

        # --- BOS / CHOCH ---
        bos = False
        choch = False
        last_close = closes[-1]

        if len(swing_highs) >= 1 and last_close > swing_highs[-1]:
            bos = True
            reasons.append(f"Bullish BOS above {swing_highs[-1]:.4f}")
        elif len(swing_lows) >= 1 and last_close < swing_lows[-1]:
            bos = True
            reasons.append(f"Bearish BOS below {swing_lows[-1]:.4f}")

        # CHOCH: structure reversal vs prior trend
        if bos and structure_bias != ema_bias and ema_bias != "NEUTRAL":
            choch = True
            reasons.append("CHOCH: reversal vs prior trend")

        # --- Momentum ---
        lookback = min(10, len(closes) - 1)
        prev_close = closes[-1 - lookback]
        momentum_pct = (
            (last_close - prev_close) / prev_close * 100
        ) if prev_close > 0 else 0.0

        if momentum_pct > 0.15:
            momentum_bias = "BULLISH"
        elif momentum_pct < -0.15:
            momentum_bias = "BEARISH"
        else:
            momentum_bias = "NEUTRAL"

        # --- Volume ---
        vols = [c.volume for c in candles]
        recent_vols = vols[-5:]
        baseline_vols = vols[-50:] if len(vols) >= 50 else vols
        avg_recent = sum(recent_vols) / len(recent_vols) if recent_vols else 0
        avg_base = sum(baseline_vols) / len(baseline_vols) if baseline_vols else 1
        volume_ratio = (avg_recent / avg_base) if avg_base > 0 else 1.0

        if volume_ratio > 1.3:
            volume_bias = "HIGH"
        elif volume_ratio < 0.7:
            volume_bias = "LOW"
        else:
            volume_bias = "NORMAL"

        # --- ATR ---
        atr = _atr(candles, 14) or 0.0
        atr_pct = (atr / last_close * 100) if last_close > 0 else 0.0

        # --- Combined Direction + Confidence ---
        votes = {
            "BULLISH": 0,
            "BEARISH": 0,
            "NEUTRAL": 0,
        }
        votes[ema_bias] += 1
        votes[structure_bias] += 1
        votes[momentum_bias] += 1

        # BOS adds extra weight
        if bos:
            if "Bullish BOS" in str(reasons[-1] if reasons else ""):
                votes["BULLISH"] += 1
            else:
                votes["BEARISH"] += 1

        total_votes = sum(votes.values())
        if total_votes == 0:
            direction = "NEUTRAL"
            confidence = 0.0
        else:
            direction = max(votes, key=votes.get)
            confidence = round(votes[direction] / total_votes * 100, 2)

        if direction == "NEUTRAL" or confidence < 40:
            reasons.append("Weak agreement — mixed signals")

        return StructureResult(
            symbol=symbol,
            timeframe=timeframe,
            direction=direction,
            confidence=confidence,
            ema20=round(ema20, 6),
            ema50=round(ema50, 6),
            ema_bias=ema_bias,
            structure_bias=structure_bias,
            bos_detected=bos,
            choch_detected=choch,
            swing_highs=tuple(round(x, 6) for x in swing_highs[-5:]),
            swing_lows=tuple(round(x, 6) for x in swing_lows[-5:]),
            momentum_pct=round(momentum_pct, 4),
            momentum_bias=momentum_bias,
            volume_ratio=round(volume_ratio, 4),
            volume_bias=volume_bias,
            atr=round(atr, 6),
            atr_pct=round(atr_pct, 4),
            candle_count=len(candles),
            reasons=tuple(reasons),
            computed_at=now,
        )


_engine: Optional[StructureAnalyzer] = None


def get_structure_analyzer() -> StructureAnalyzer:
    global _engine
    if _engine is None:
        _engine = StructureAnalyzer()
    return _engine


__all__ = [
    "StructureResult",
    "StructureAnalyzer",
    "get_structure_analyzer",
    "normalize_tf",
]
'''

(ROOT / "structure_analyzer.py").write_text(FILE, encoding="utf-8")
print(f"WROTE: {ROOT / 'structure_analyzer.py'}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.real_market_data import get_real_market_data; from app.intelligence.real.structure_analyzer import get_structure_analyzer; m = get_real_market_data(); c, _ = m.get_candles(\\"BTC/USDT\\", \\"15\\", 100); r = get_structure_analyzer().analyze(\\"BTC/USDT\\", \\"15m\\", c); import json; print(json.dumps(r.to_dict(), indent=2))"')