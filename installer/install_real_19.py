"""Wire real_discovery_bridge into universe_seed (Option B)"""
from pathlib import Path
import shutil
from datetime import datetime

# Target 1 — universe_seed.py in opportunity folder
OPP = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\opportunity\universe_seed.py")

if not OPP.exists():
    print(f"ERROR: {OPP} not found")
    raise SystemExit(1)

content = OPP.read_text(encoding="utf-8")
backup = OPP.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(OPP, backup)
print(f"BACKUP: {backup}")

# Check if already wired
if "real_discovery_bridge" in content:
    print("Already wired.")
    raise SystemExit(0)

# Patch get_universe_seed function
old = '''def get_universe_seed(
    market: Optional[str] = None,
    venue: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return a copy of the seed universe for the given market.

    - market=None or "" or "ALL" -> returns combined seeds.
    - Unknown market -> CRYPTO seed as default.
    - Returns a fresh list of dicts (safe to mutate).
    """
    if market is None or str(market).strip() == "":
        normalized = "CRYPTO"
    else:
        normalized = str(market).strip().upper()

    if normalized == "ALL":
        combined: List[Dict[str, Any]] = []
        for items in _SEED_BY_MARKET.values():
            combined.extend(dict(item) for item in items)
        return combined

    items = _SEED_BY_MARKET.get(normalized, CRYPTO_SEED)

    # Return fresh copies so callers can mutate safely.
    result: List[Dict[str, Any]] = []
    for item in items:
        copy_item = dict(item)
        symbol = copy_item.get("symbol", "")

        # Merge static reference prices for non-crypto markets when
        # real provider data is not available.
        if "price" not in copy_item:
            static = _STATIC_REFERENCE_PRICES.get(symbol)
            if static:
                copy_item["price"] = static["price"]
                copy_item["change_pct"] = static["change_pct"]

        result.append(copy_item)

    return result'''

new = '''def get_universe_seed(
    market: Optional[str] = None,
    venue: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Real universe — computed from live market data via unified_signal.

    Falls back to static seed if real bridge unavailable or fails.
    """
    if market is None or str(market).strip() == "":
        normalized = "CRYPTO"
    else:
        normalized = str(market).strip().upper()

    # Try real bridge first
    if normalized in {"CRYPTO", "EQUITY", "INDEX", "FOREX"}:
        try:
            from app.intelligence.real.real_discovery_bridge import (
                get_real_crypto_opportunities,
            )
            real = get_real_crypto_opportunities(normalized, limit=15)
            if real:
                return real
        except Exception as _e:
            # Fall through to static seed
            pass

    # Fallback — static seed
    if normalized == "ALL":
        combined: List[Dict[str, Any]] = []
        for items in _SEED_BY_MARKET.values():
            combined.extend(dict(item) for item in items)
        return combined

    items = _SEED_BY_MARKET.get(normalized, CRYPTO_SEED)

    result: List[Dict[str, Any]] = []
    for item in items:
        copy_item = dict(item)
        symbol = copy_item.get("symbol", "")

        if "price" not in copy_item:
            static = _STATIC_REFERENCE_PRICES.get(symbol)
            if static:
                copy_item["price"] = static["price"]
                copy_item["change_pct"] = static["change_pct"]

        result.append(copy_item)

    return result'''

if old in content:
    content = content.replace(old, new, 1)
    OPP.write_text(content, encoding="utf-8")
    print(f"WIRED: {OPP}")
else:
    print(f"WARNING: get_universe_seed marker not found — check manually")
    raise SystemExit(1)

print()
print("Discovery ab real unified_signal se data lega.")
print()
print("Test:")
print('  curl "http://127.0.0.1:8000/api/discovery?market=CRYPTO" | python -c "import sys, json; d = json.load(sys.stdin); top = d.get(\\"top10\\", []); [print(f\\"{t[\\"symbol\\"]:12} {t.get(\\"direction\\",\\"\\"):8} score={t.get(\\"score\\",0):6.2f}\\") for t in top[:5]]"')