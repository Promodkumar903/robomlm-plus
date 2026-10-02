"""Wire unified_signal into AutoROBOMLM signal_adapter (Option C)"""
from pathlib import Path
import shutil
from datetime import datetime

TARGET = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\signal_adapter.py")

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

if "_make_unified_provider" in content:
    print("Already wired.")
    raise SystemExit(0)

# ---------------------------------------------------------------
# 1. Insert unified_signal -> AutoROBOMLM dict converter
# ---------------------------------------------------------------
insert_marker = "def make_live_signal_provider()"

converter = '''# ---------------------------------------------------------------------
# unified_signal -> AutoROBOMLM dict
# ---------------------------------------------------------------------

def _unified_to_autoro_dict(sig) -> dict:
    """
    Convert a UnifiedSignal into the dict shape AutoRobomlmLoop expects.

    Fields provided:
        direction     : LONG | SHORT | NEUTRAL
        action        : BUY  | SELL  | HOLD
        decision_score: 0-100 (strength)
        confidence    : 0-100
        grade         : A+ | A | B+ | B | HOLD
        strength      : 0-100
        entry, sl, tp, rr, expected_move_pct, size_pct
        risk_level, warnings
        source        : REAL_UNIFIED_SIGNAL
    """
    direction = "NEUTRAL"
    if sig.direction == "BULLISH":
        direction = "LONG"
    elif sig.direction == "BEARISH":
        direction = "SHORT"

    return {
        "symbol": sig.symbol,
        "timestamp": sig.timestamp,
        "direction": direction,
        "action": sig.action,
        "decision_score": float(sig.strength),
        "confidence": float(sig.confidence),
        "strength": float(sig.strength),
        "grade": sig.trade_quality,
        "entry": sig.entry_price,
        "entry_price": sig.entry_price,
        "stop_loss": sig.stop_loss,
        "take_profit": sig.take_profit,
        "risk_reward": sig.risk_reward,
        "expected_move_pct": sig.expected_move_pct,
        "suggested_size_pct": sig.suggested_size_pct,
        "risk_level": sig.risk_level,
        "warnings": list(sig.warnings),
        "source": "REAL_UNIFIED_SIGNAL",
        # keep audit for logs
        "audit": sig.audit,
    }


def _make_unified_provider():
    """
    Return a callable that uses unified_signal for a symbol.
    Returns None on failure so caller can fall back.
    """
    try:
        from app.intelligence.real.unified_signal import (
            get_unified_signal_engine,
        )
    except Exception:
        return None

    engine = get_unified_signal_engine()

    def provider(symbol: str):
        try:
            sig = engine.compute(symbol)
            return _unified_to_autoro_dict(sig)
        except Exception:
            return None

    return provider


'''

# Insert converter before make_live_signal_provider
if insert_marker in content:
    content = content.replace(insert_marker, converter + insert_marker, 1)
    print("Converter + unified provider inserted")
else:
    print("WARNING: make_live_signal_provider marker not found")
    raise SystemExit(1)

# ---------------------------------------------------------------
# 2. Patch make_live_signal_provider to try unified first
# ---------------------------------------------------------------
old_fn = '''def make_live_signal_provider() -> Callable[[str], Optional[dict]]:
    """
    Return a callable suitable for AutoRobomlmLoop.signal_provider.

    Raises RuntimeError immediately if live_signal cannot be imported.
    """
    getter = _import_live_signal_getter()

    if getter is None:
        raise RuntimeError(
            "Could not import live_signal.get_signal. "
            "Check that app.intelligence.live_signal exists."
        )

    def provider(symbol: str) -> Optional[dict]:
        try:
            raw = getter(symbol)
        except Exception:
            return None
        return normalize_signal(raw)

    return provider'''

new_fn = '''def make_live_signal_provider() -> Callable[[str], Optional[dict]]:
    """
    Return a callable suitable for AutoRobomlmLoop.signal_provider.

    Priority:
        1. unified_signal  (REAL — all 8 engines)
        2. live_signal     (legacy fallback)

    Raises RuntimeError only if BOTH are unavailable.
    """
    # --- Try unified first ---
    unified = _make_unified_provider()

    # --- Legacy fallback getter ---
    getter = _import_live_signal_getter()

    if unified is None and getter is None:
        raise RuntimeError(
            "Neither unified_signal nor live_signal is available. "
            "Check app.intelligence.real.unified_signal and "
            "app.intelligence.live_signal."
        )

    def provider(symbol: str) -> Optional[dict]:
        # 1) unified
        if unified is not None:
            try:
                result = unified(symbol)
                if result is not None:
                    # Optionally normalize for downstream
                    return normalize_signal(result)
            except Exception:
                pass
        # 2) legacy
        if getter is not None:
            try:
                raw = getter(symbol)
                return normalize_signal(raw)
            except Exception:
                return None
        return None

    return provider'''

if "Priority:" in content and "unified_signal  (REAL" in content:
    print("make_live_signal_provider already patched")
elif old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    print("make_live_signal_provider patched: unified first, legacy fallback")
else:
    print("WARNING: make_live_signal_provider block not found — checking partial")
    # Try partial match
    if "def make_live_signal_provider" in content:
        print("Function exists but pattern mismatch. Manual review needed.")
        raise SystemExit(1)

# Update version
content = content.replace(
    'ADAPTER_VERSION = "1.0"',
    'ADAPTER_VERSION = "2.0-unified"',
    1,
)

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test 1 — provider returns unified dict:")
print('  python -c "from app.autorobomlm.signal_adapter import make_live_signal_provider; p = make_live_signal_provider(); s = p(\\"BTC/USDT\\"); import json; print(json.dumps({k:v for k,v in s.items() if k != \\"audit\\"}, indent=2, default=str))"')