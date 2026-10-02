"""Add 60s cache to real_discovery_bridge"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "real_discovery_bridge.py"

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

# Add cache globals at top (after imports)
if "_CACHE = {}" not in content:
    # Insert after DEFAULT_WATCHLIST definition
    marker = 'DEFAULT_WATCHLIST = {'
    idx = content.find(marker)
    if idx > 0:
        # Find end of DEFAULT_WATCHLIST dict
        close_idx = content.find('}', idx)
        insert_at = close_idx + 1
        cache_block = '''

# ============================================================
# 60-second CACHE
# ============================================================
_CACHE: dict = {}
_CACHE_TTL = 60  # seconds

'''
        content = content[:insert_at] + cache_block + content[insert_at:]
        print("CACHE variables added")
else:
    print("Cache already present")

# Modify get_real_crypto_opportunities to use cache
old_start = '''def get_real_crypto_opportunities(
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

    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])'''

new_start = '''def get_real_crypto_opportunities(
    market: str = "CRYPTO",
    limit: int = 10,
    max_workers: int = 10,
) -> list[dict]:
    """
    Compute real opportunities using parallel fetch with 60s cache.

    Cache hit: returns immediately (< 0.01s)
    Cache miss: parallel fetch (~30s)
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    # ---- CACHE CHECK ----
    cache_key = f"{market.upper()}:{limit}"
    now = time.time()

    cached = _CACHE.get(cache_key)
    if cached is not None:
        expires_at, data = cached
        if now < expires_at:
            return data

    watchlist = DEFAULT_WATCHLIST.get(market.upper(), DEFAULT_WATCHLIST["CRYPTO"])'''

if "Cache hit: returns immediately" in content:
    print("Cache logic already present")
elif old_start in content:
    content = content.replace(old_start, new_start, 1)
    print("Cache check added")
else:
    print("WARNING: function start not found")

# Store cache before return
old_return = '''    # Sort by strength descending
    opportunities.sort(
        key=lambda o: o.get("strength", o.get("score", 0)),
        reverse=True,
    )

    # Attach timing metadata to each opportunity
    for opp in opportunities:
        opp["_parallel_fetch_seconds"] = round(elapsed, 2)

    return opportunities[:limit]'''

new_return = '''    # Sort by strength descending
    opportunities.sort(
        key=lambda o: o.get("strength", o.get("score", 0)),
        reverse=True,
    )

    # Attach timing metadata to each opportunity
    for opp in opportunities:
        opp["_parallel_fetch_seconds"] = round(elapsed, 2)

    result = opportunities[:limit]

    # ---- STORE CACHE ----
    _CACHE[cache_key] = (now + _CACHE_TTL, result)

    return result


def clear_cache() -> None:
    """Clear the discovery cache."""
    _CACHE.clear()


def cache_info() -> dict:
    """Return cache metadata."""
    import time
    now = time.time()
    return {
        "entries": len(_CACHE),
        "ttl_seconds": _CACHE_TTL,
        "keys": list(_CACHE.keys()),
        "details": {
            key: {
                "expires_in_seconds": round(max(0, exp - now), 1),
                "fresh": now < exp,
            }
            for key, (exp, _) in _CACHE.items()
        },
    }'''

if "clear_cache() -> None" in content:
    print("Cache store already present")
elif old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("Cache store added")
else:
    print("WARNING: return block not found")

# Update __all__
old_all = '''__all__ = [
    "signal_to_opportunity",
    "get_real_crypto_opportunities",
    "DEFAULT_WATCHLIST",
]'''

new_all = '''__all__ = [
    "signal_to_opportunity",
    "get_real_crypto_opportunities",
    "clear_cache",
    "cache_info",
    "DEFAULT_WATCHLIST",
]'''

if "clear_cache" in content and 'clear_cache",' not in content:
    content = content.replace(old_all, new_all, 1)
    print("__all__ updated")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test cache:")
print('  python -c "import time; from app.intelligence.real.real_discovery_bridge import get_real_crypto_opportunities, cache_info; t = time.time(); opps = get_real_crypto_opportunities(\\"CRYPTO\\", 10); print(f\\"1st call: {time.time()-t:.1f}s — {len(opps)} results\\"); t = time.time(); opps = get_real_crypto_opportunities(\\"CRYPTO\\", 10); print(f\\"2nd call: {time.time()-t:.3f}s — {len(opps)} results\\"); print(\\"cache:\\", cache_info())"')