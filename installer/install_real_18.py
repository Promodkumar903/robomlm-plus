"""Fix grade inflation + direction skew in unified_signal"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "unified_signal.py"

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

# ---- FIX 1: Grade based on STRENGTH (absolute) not confidence alone ----
old_grade = '''        # ----------------------------------------------------
        # TRADE QUALITY GRADE
        # ----------------------------------------------------
        # Score = combined confidence + regime + RR
        quality_score = confidence
        if rr and rr >= 2.0:
            quality_score += 10
        elif rr and rr < 1.0:
            quality_score -= 15

        if stats and stats.market_regime == "TRENDING":
            quality_score += 10
        if stats and stats.market_regime == "CHAOTIC":
            quality_score -= 20

        if ctx and ctx.vol_regime == "EXTREME":
            quality_score -= 15

        # Grade
        if quality_score >= 75 and action in {"BUY", "SELL"}:
            grade = "A+"
            grade_reason = "High confidence + trend regime + good RR"
        elif quality_score >= 55 and action in {"BUY", "SELL"}:
            grade = "A"
            grade_reason = "Good confidence + acceptable RR"
        elif quality_score >= 45 and action in {"BUY", "SELL"}:
            grade = "B+"
            grade_reason = "Moderate confidence"
        elif quality_score >= 30 and action in {"BUY", "SELL"}:
            grade = "B"
            grade_reason = "Low confidence — small position only"
        else:
            grade = "HOLD"
            grade_reason = "Insufficient quality — no trade"'''

new_grade = '''        # ----------------------------------------------------
        # TRADE QUALITY GRADE
        # ----------------------------------------------------
        # Grade based on ABSOLUTE STRENGTH (not ratio-based confidence)
        # Modifiers: RR quality, regime, volatility

        base_grade_score = strength  # absolute bull/bear score (0-100)

        # RR adjustment
        if rr is not None:
            if rr >= 2.5:
                base_grade_score += 8
            elif rr >= 2.0:
                base_grade_score += 4
            elif rr >= 1.5:
                base_grade_score += 2
            elif rr < 1.0:
                base_grade_score -= 10

        # Regime adjustment
        if stats:
            if stats.market_regime == "TRENDING":
                base_grade_score += 5
            elif stats.market_regime == "CHAOTIC":
                base_grade_score -= 15
            elif stats.market_regime == "RANGING":
                base_grade_score -= 5

        # Volatility adjustment
        if ctx and ctx.vol_regime == "EXTREME":
            base_grade_score -= 10

        # Confidence gate — even high strength needs SOME confidence
        if confidence < 55:
            base_grade_score -= 15

        # Require minimum strength for each grade
        if action not in {"BUY", "SELL"}:
            grade = "HOLD"
            grade_reason = "No actionable direction"
        elif strength < 25:
            grade = "HOLD"
            grade_reason = f"Strength too low ({strength:.1f})"
        elif base_grade_score >= 75:
            grade = "A+"
            grade_reason = f"High strength ({strength:.0f}) + trend + good RR"
        elif base_grade_score >= 55:
            grade = "A"
            grade_reason = f"Good strength ({strength:.0f})"
        elif base_grade_score >= 45:
            grade = "B+"
            grade_reason = f"Moderate strength ({strength:.0f})"
        elif base_grade_score >= 30:
            grade = "B"
            grade_reason = f"Low strength ({strength:.0f}) — small position"
        else:
            grade = "HOLD"
            grade_reason = f"Insufficient strength ({strength:.0f})"'''

if "base_grade_score = strength" in content:
    print("Grade fix already applied")
elif old_grade in content:
    content = content.replace(old_grade, new_grade, 1)
    print("FIX 1: grade based on absolute strength")
else:
    print("WARNING: grade block not found")

# ---- FIX 2: Cap confidence by strength to prevent 100% on tiny signals ----
old_conf = '''        total = final_bull + final_bear

        if total < 15:
            direction = "NEUTRAL"
            strength = 0.0
            confidence = 0.0
        elif final_bull > final_bear * 1.15:
            direction = "BULLISH"
            strength = round(_clamp(final_bull), 2)
            confidence = round(final_bull / total * 100, 2)
        elif final_bear > final_bull * 1.15:
            direction = "BEARISH"
            strength = round(_clamp(final_bear), 2)
            confidence = round(final_bear / total * 100, 2)
        else:
            direction = "NEUTRAL"
            strength = round(_clamp(max(final_bull, final_bear)), 2)
            confidence = 50.0'''

new_conf = '''        total = final_bull + final_bear

        if total < 15:
            direction = "NEUTRAL"
            strength = 0.0
            confidence = 0.0
        elif final_bull > final_bear * 1.15:
            direction = "BULLISH"
            strength = round(_clamp(final_bull), 2)
            ratio_conf = (final_bull / total) * 100
            # Confidence capped by absolute strength
            # Small signals can't claim high confidence
            conf_cap = min(100.0, strength * 1.5)
            confidence = round(min(ratio_conf, conf_cap), 2)
        elif final_bear > final_bull * 1.15:
            direction = "BEARISH"
            strength = round(_clamp(final_bear), 2)
            ratio_conf = (final_bear / total) * 100
            conf_cap = min(100.0, strength * 1.5)
            confidence = round(min(ratio_conf, conf_cap), 2)
        else:
            direction = "NEUTRAL"
            strength = round(_clamp(max(final_bull, final_bear)), 2)
            confidence = 50.0'''

if "conf_cap = min(100.0, strength * 1.5)" in content:
    print("Confidence cap already applied")
elif old_conf in content:
    content = content.replace(old_conf, new_conf, 1)
    print("FIX 2: confidence capped by strength")
else:
    print("WARNING: confidence block not found")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.real_discovery_bridge import get_real_crypto_opportunities; opps = get_real_crypto_opportunities(\\"CRYPTO\\", 10); [print(f\\"{o[\\"symbol\\"]:12} {o[\\"direction\\"]:8} str={o[\\"score\\"]:6.2f} conf={o[\\"confidence\\"]:6.2f} grade={o[\\"grade\\"]:5} RR={o.get(\\"risk_reward\\")}\\") for o in opps]"')