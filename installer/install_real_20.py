"""Parallel fetch for real_discovery_bridge"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "real_discovery_bridge.py"

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

old_fn = '''def get_real_crypto_opportunities(
    market: str = "CRYPTO",
    limit: int = 10,
) -> list[dict]:
    """
    Compute real opportunities for the given market using unified_signal.
    """
    engine = get_unified_signal_engine()
    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])

    opportunities = []
    for symbol in watchlist:
        try:
            signal = engine.compute(symbol)
            opp = signal_to_opportunity(signal)
            opportunities.append(opp)
        except Exception as e:
            # Don't fabricate — skip on error
            continue

    # Sort by strength descending
    opportunities.sort(key=lambda o: o.get("strength", o.get("score", 0)), reverse=True)
    return opportunities[:limit]'''

new_fn = '''def _compute_one(symbol: str) -> Optional[dict]:
    """Compute one symbol's opportunity — thread-safe wrapper."""
    try:
        engine = get_unified_signal_engine()
        signal = engine.compute(symbol)
        return signal_to_opportunity(signal)
    except Exception:
        return None


def get_real_crypto_opportunities(
    market: str = "CRYPTO",
    limit: int = 10,
    max_workers: int = 10,
) -> list[dict]:
    """
    Compute real opportunities using parallel fetch.

    Each symbol is fetched in parallel using ThreadPoolExecutor.
    This reduces total time from ~150 sequential calls to ~10 parallel calls.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])

    opportunities: list[dict] = []
    started = time.time()

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_compute_one, symbol): symbol
                for symbol in watchlist
            }
            for future in as_completed(futures, timeout=90):
                try:
                    result = future.result(timeout=60)
                    if result is not None:
                        opportunities.append(result)
                except Exception:
                    continue
    except Exception:
        # Timeout or executor failure — return whatever we got
        pass

    elapsed = time.time() - started

    # Sort by strength descending
    opportunities.sort(
        key=lambda o: o.get("strength", o.get("score", 0)),
        reverse=True,
    )

    # Attach timing metadata to each opportunity
    for opp in opportunities:
        opp["_parallel_fetch_seconds"] = round(elapsed, 2)

    return opportunities[:limit]'''

if "ThreadPoolExecutor" in content:
    print("Parallel fetch already applied")
elif old_fn in content:
    content = content.replace(old_fn, new_fn, 1)
    # Ensure Optional import
    if "from typing import Optional" not in content:
        content = content.replace(
            "from typing import",
            "from typing import Optional,",
            1,
        )
    TARGET.write_text(content, encoding="utf-8")
    print("PARALLEL FETCH: added")
else:
    print("WARNING: get_real_crypto_opportunities not found")
    raise SystemExit(1)

print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "import time; from app.intelligence.real.real_discovery_bridge import get_real_crypto_opportunities; t = time.time(); opps = get_real_crypto_opportunities(\\"CRYPTO\\", 10); print(f\\"fetched {len(opps)} in {time.time()-t:.1f}s\\"); [print(f\\"{o[\\"symbol\\"]:12} {o[\\"direction\\"]:8} score={o[\\"score\\"]:6.2f}\\") for o in opps]"')