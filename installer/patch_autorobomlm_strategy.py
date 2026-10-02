# patch_autorobomlm_strategy.py
# Adds DeepSeek strategy hook to AutoROBOMLM.
# Default = "OLD" (no behavior change).
# Backup PEHLE har file ka. Kuch delete nahi.

import os, sys, shutil
from datetime import datetime

ROOT = r"C:\Users\Administrator\ROBOMLM_PLUS"

CONFIG_PY = os.path.join(ROOT, "app", "autorobomlm", "config.py")
LOOP_PY = os.path.join(ROOT, "app", "autorobomlm", "auto_loop.py")
API_PY = os.path.join(ROOT, "app", "api", "v1", "autorobomlm_api.py")


def backup(path):
    if not os.path.isfile(path):
        print(f"ERROR: not found: {path}")
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path + f".bak_{ts}"
    shutil.copy2(path, bak)
    if not os.path.isfile(bak):
        print("ERROR: backup not verified")
        return None
    print(f"BACKUP OK: {os.path.basename(bak)}")
    return bak


# ============================================================
# 1. config.py — add strategy_id field
# ============================================================

def patch_config():
    with open(CONFIG_PY, "r", encoding="utf-8") as f:
        src = f.read()

    if "strategy_id" in src:
        print("config.py: ALREADY PATCHED")
        return True

    # Anchor 1: field
    a1 = "    min_grade: GradeBand = GradeBand.A\n"
    r1 = ("    min_grade: GradeBand = GradeBand.A\n"
          "\n"
          "    # NEW: strategy selector. OLD = existing behavior. DEEPSEEK = strategy layer.\n"
          "    strategy_id: str = \"OLD\"\n")
    if a1 not in src:
        print("config.py: anchor1 not found")
        return False
    src = src.replace(a1, r1, 1)

    # Anchor 2: as_dict
    a2 = '            "min_grade": self.min_grade.value,\n'
    r2 = ('            "min_grade": self.min_grade.value,\n'
          '            "strategy_id": self.strategy_id,\n')
    if a2 in src:
        src = src.replace(a2, r2, 1)
    else:
        print("config.py: as_dict anchor missing (non-fatal)")

    # Anchor 3: from_dict
    a3 = '            min_grade=GradeBand(\n                data.get("min_grade", GradeBand.A.value)\n            ),\n'
    r3 = (a3 + '            strategy_id=str(data.get("strategy_id", "OLD")),\n')
    if a3 in src:
        src = src.replace(a3, r3, 1)
    else:
        print("config.py: from_dict anchor missing (non-fatal)")

    bak = backup(CONFIG_PY)
    if not bak:
        return False
    with open(CONFIG_PY, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: config.py")
    return True


# ============================================================
# 2. auto_loop.py — add _apply_strategy + call
# ============================================================

NEW_METHOD = '''
    def _apply_strategy(self, signal: dict, symbol: str) -> tuple:
        """Strategy gate. Returns (allowed: bool, reason: str).

        Default strategy_id = "OLD" -> always allow (existing behavior).
        "DEEPSEEK" -> uses app.strategies.deepseek_strategy.DeepSeekStrategy.
        """
        sid = str(getattr(self.config, "strategy_id", "OLD") or "OLD").upper()

        if sid == "OLD":
            return True, "strategy_OLD_allow"

        if sid != "DEEPSEEK":
            return True, f"strategy_unknown_allow:{sid}"

        try:
            from app.strategies.base import StrategyInput
            from app.strategies.deepseek_strategy import DeepSeekStrategy
        except Exception as exc:
            return True, f"strategy_import_failed:{exc!r}"

        def _f(v, d=0.0):
            try:
                return float(v)
            except (TypeError, ValueError):
                return d

        direction_raw = str(signal.get("direction", "NEUTRAL")).upper()
        if direction_raw == "LONG":
            direction = "BULLISH"
        elif direction_raw == "SHORT":
            direction = "BEARISH"
        else:
            direction = "NEUTRAL"

        comps = signal.get("components") or {}
        sl_raw = signal.get("stop_loss")
        tp_raw = signal.get("take_profit")
        rr_raw = signal.get("risk_reward")

        inp = StrategyInput(
            symbol=symbol,
            timeframe=str(signal.get("timeframe", "1m")),
            direction=direction,
            action=str(signal.get("action", "HOLD")).upper(),
            strength=_f(signal.get("strength", signal.get("decision_score"))),
            confidence=_f(signal.get("confidence")),
            trade_quality=str(signal.get("trade_quality") or signal.get("grade") or "HOLD"),
            risk_level=str(signal.get("risk_level") or "LOW"),
            entry_price=_f(signal.get("entry_price")),
            stop_loss=_f(sl_raw) if sl_raw is not None else None,
            take_profit=_f(tp_raw) if tp_raw is not None else None,
            risk_reward=_f(rr_raw) if rr_raw is not None else None,
            expected_move_pct=_f(signal.get("expected_move_pct")),
            components={
                "flow": _f(comps.get("flow")),
                "derivative": _f(comps.get("derivative")),
                "volume": _f(comps.get("volume")),
                "obstacle": _f(comps.get("obstacle")),
                "context": _f(comps.get("context")),
                "regime": _f(comps.get("regime")),
            },
            warnings=tuple(signal.get("warnings") or ()),
            metadata={},
        )

        try:
            out = DeepSeekStrategy().decide(inp)
        except Exception as exc:
            return True, f"strategy_exception_allow:{exc!r}"

        if not out.entry_permission:
            reasons = ",".join(out.reason_codes) if out.reason_codes else "unknown"
            return False, f"strategy_reject:{reasons}"

        return True, f"strategy_pass:{out.strategy_score}"
'''

ANCHOR_METHOD = "    def _evaluate_symbol(\n"

ANCHOR_CALL = "        # Price\n        price = self._price_for(symbol)\n"
REPLACE_CALL = (
    "        # Strategy gate (NEW; default OLD = pass-through)\n"
    "        strategy_ok, strategy_reason = self._apply_strategy(signal, symbol)\n"
    "        if not strategy_ok:\n"
    "            summary.skipped_gates += 1\n"
    "            summary.events.append(f\"{symbol}: {strategy_reason}\")\n"
    "            return\n"
    "\n"
    "        # Price\n"
    "        price = self._price_for(symbol)\n"
)


def patch_loop():
    with open(LOOP_PY, "r", encoding="utf-8") as f:
        src = f.read()

    if "_apply_strategy" in src:
        print("auto_loop.py: ALREADY PATCHED")
        return True

    if ANCHOR_METHOD not in src:
        print("auto_loop.py: _evaluate_symbol anchor not found")
        return False
    if ANCHOR_CALL not in src:
        print("auto_loop.py: # Price anchor not found")
        return False

    # Insert method before _evaluate_symbol
    src = src.replace(ANCHOR_METHOD, NEW_METHOD + "\n" + ANCHOR_METHOD, 1)

    # Insert call before # Price
    src = src.replace(ANCHOR_CALL, REPLACE_CALL, 1)

    bak = backup(LOOP_PY)
    if not bak:
        return False
    with open(LOOP_PY, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: auto_loop.py")
    return True


# ============================================================
# 3. autorobomlm_api.py — add /strategy endpoint
# ============================================================

NEW_ENDPOINT = '''

@router.post("/strategy")
def set_strategy(payload: dict = Body(...)) -> dict:
    """Set active strategy: OLD | DEEPSEEK."""
    _ensure_state()
    sid = str(payload.get("strategy_id", "OLD")).upper()
    if sid not in ("OLD", "DEEPSEEK"):
        return {"ok": False, "error": f"invalid strategy_id: {sid}"}
    try:
        _state["config"].strategy_id = sid
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "strategy_id": sid}

'''


def patch_api():
    with open(API_PY, "r", encoding="utf-8") as f:
        src = f.read()

    if '@router.post("/strategy")' in src:
        print("autorobomlm_api.py: ALREADY PATCHED")
        return True

    idx = src.find("def manual_trade(")
    if idx < 0:
        print("autorobomlm_api.py: manual_trade not found")
        return False

    dec_idx = src.rfind("@router", 0, idx)
    if dec_idx < 0:
        print("autorobomlm_api.py: decorator before manual_trade not found")
        return False

    src = src[:dec_idx] + NEW_ENDPOINT.lstrip("\n") + "\n" + src[dec_idx:]

    bak = backup(API_PY)
    if not bak:
        return False
    with open(API_PY, "w", encoding="utf-8") as f:
        f.write(src)
    print("PATCHED: autorobomlm_api.py")
    return True


# ============================================================

def main():
    print("=" * 60)
    print("Patch AutoROBOMLM with DeepSeek strategy hook")
    print("=" * 60)

    ok1 = patch_config()
    ok2 = patch_loop()
    ok3 = patch_api()

    print()
    if ok1 and ok2 and ok3:
        print("ALL PATCHES APPLIED.")
        print()
        print("Server restart karo (uvicorn Ctrl+C, phir dobara).")
        print("Phir test:")
        print('  curl -X POST http://127.0.0.1:8000/api/autorobomlm/strategy -H "Content-Type: application/json" -d "{\\"strategy_id\\":\\"DEEPSEEK\\"}"')
        print('  curl -X POST http://127.0.0.1:8000/api/autorobomlm/strategy -H "Content-Type: application/json" -d "{\\"strategy_id\\":\\"OLD\\"}"')
    else:
        print("Some patches failed. Check output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()