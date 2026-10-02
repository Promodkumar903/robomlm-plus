"""Add BYBIT_PROVIDER contract to provider_definitions (safe patch)"""
from pathlib import Path
import shutil
from datetime import datetime

TARGET = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\providers\provider_definitions.py")

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found")
    raise SystemExit(1)

content = TARGET.read_text(encoding="utf-8")

if "BYBIT_PROVIDER" in content:
    print("BYBIT_PROVIDER already present — nothing to do")
    raise SystemExit(0)

backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

# ---------- 1. Insert BYBIT_PROVIDER before __all__ ----------
marker = "\n__all__ = ["
if marker not in content:
    print("WARNING: __all__ marker not found — abort")
    raise SystemExit(1)

bybit_block = '''

BYBIT_PROVIDER = ProviderContract(
    provider_id="BYBIT",
    provider_name="Bybit",

    markets=frozenset({
        "CRYPTO",
    }),

    segments=frozenset({
        "SPOT",
    }),

    instrument_types=frozenset({
        "SPOT",
    }),

    capabilities=(
        ProviderCapabilityState(
            capability=ProviderCapability.TICKER,
            status=ProviderStatus.AVAILABLE,
        ),
        ProviderCapabilityState(
            capability=ProviderCapability.SNAPSHOT,
            status=ProviderStatus.AVAILABLE,
        ),
    ),

    status=ProviderStatus.AVAILABLE,

    adapter_path=(
        "app.adapters.bybit.bybit_market_data."
        "BybitMarketData"
    ),

    client_path=(
        "app.adapters.bybit.bybit_client."
        "BybitClient"
    ),
)

'''

content = content.replace(marker, bybit_block + marker, 1)
print("BYBIT_PROVIDER inserted")

# ---------- 2. Update __all__ ----------
old_all = '''__all__ = [
    "BINANCE_PROVIDER",
    "MASSIVE_PROVIDER",
]'''

new_all = '''__all__ = [
    "BINANCE_PROVIDER",
    "MASSIVE_PROVIDER",
    "BYBIT_PROVIDER",
]'''

if old_all in content:
    content = content.replace(old_all, new_all, 1)
    print("__all__ updated")
else:
    # fallback — add BYBIT_PROVIDER inside __all__
    if '"BYBIT_PROVIDER"' not in content:
        content = content.replace(
            '"MASSIVE_PROVIDER",',
            '"MASSIVE_PROVIDER",\n    "BYBIT_PROVIDER",',
            1,
        )
        print("__all__ updated (fallback)")

TARGET.write_text(content, encoding="utf-8")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.providers.provider_definitions import BYBIT_PROVIDER; print(\'provider_id:\', BYBIT_PROVIDER.provider_id); print(\'markets:\', BYBIT_PROVIDER.markets); print(\'capabilities:\', [(c.capability.value, c.status.value) for c in BYBIT_PROVIDER.capabilities])"')