from __future__ import annotations

from app.providers.provider_contract import (
    ProviderCapability,
    ProviderCapabilityState,
    ProviderContract,
    ProviderStatus,
)


BINANCE_PROVIDER = ProviderContract(
    provider_id="BINANCE",
    provider_name="Binance",

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
        "app.adapters.binance.binance_market_data."
        "BinanceMarketData"
    ),

    client_path=(
        "app.adapters.binance.binance_client."
        "BinanceClient"
    ),
)


MASSIVE_PROVIDER = ProviderContract(
    provider_id="MASSIVE",
    provider_name="Massive",

    markets=frozenset({
        "EQUITY",
        "INDEX",
        "OPTIONS",
        "FUTURES",
        "FOREX",
        "COMMODITY",
    }),

    segments=frozenset({
        "SPOT",
        "OPTIONS",
        "FUTURES",
    }),

    instrument_types=frozenset({
        "EQUITY",
        "INDEX",
        "OPTIONS",
        "OPTION",
        "FUTURES",
        "FUTURE",
        "FOREX",
        "COMMODITY",
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
        "app.adapters.massive.massive_market_data."
        "MassiveMarketData"
    ),

    client_path=(
        "app.adapters.massive.massive_client."
        "MassiveClient"
    ),
)


__all__ = [
    "BINANCE_PROVIDER",
    "MASSIVE_PROVIDER",
]