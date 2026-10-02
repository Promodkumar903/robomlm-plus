from __future__ import annotations

import importlib
from typing import Any, Mapping

from app.markets.market_data_health import (
    MarketDataHealthResult,
    MarketDataHealthService,
)
from app.markets.market_snapshot_store import (
    MarketSnapshotStore,
)

from app.providers.provider_bootstrap import (
    build_provider_registry,
)
from app.providers.provider_contract import (
    ProviderCapability,
)
from app.providers.provider_resolver import (
    ProviderResolutionRequest,
    ProviderResolver,
)

from schemas.market.market_snapshot import MarketSnapshot


class LiveMarketDataService:
    """
    Application-facing market-data boundary.

    Provider selection:
        ProviderResolver

    Provider construction:
        ProviderContract adapter_path + client_path

    Output:
        canonical MarketSnapshot

    Health:
        MarketDataHealthResult

    This service does not calculate intelligence.

    Default compatibility behavior:
        get_snapshot(symbol)
            -> CRYPTO / SPOT / SPOT
            -> Binance

    Explicit market identity:
        get_snapshot(
            symbol,
            market=...,
            segment=...,
            instrument_type=...,
        )

    This allows Massive to serve:
        EQUITY
        INDEX
        OPTIONS
        FUTURES
        FOREX
        COMMODITY

    while Binance remains authoritative for:
        CRYPTO
    """

    def __init__(
        self,
        snapshot_store: MarketSnapshotStore | None = None,
        health_service: MarketDataHealthService | None = None,
    ) -> None:
        self._snapshot_store = (
            snapshot_store or MarketSnapshotStore()
        )

        self._health_service = (
            health_service or MarketDataHealthService()
        )

        self._provider_registry = (
            build_provider_registry()
        )

        self._provider_resolver = ProviderResolver(
            self._provider_registry
        )

        self._adapter_cache: dict[
            str,
            Any,
        ] = {}

    @property
    def snapshot_store(self) -> MarketSnapshotStore:
        return self._snapshot_store

    @property
    def health_service(self) -> MarketDataHealthService:
        return self._health_service

    @property
    def provider_registry(self):
        return self._provider_registry

    @property
    def provider_resolver(self) -> ProviderResolver:
        return self._provider_resolver

    def _load_class(
        self,
        dotted_path: str,
    ) -> type[Any]:
        module_name, class_name = (
            dotted_path.rsplit(".", 1)
        )

        module = importlib.import_module(
            module_name
        )

        adapter_class = getattr(
            module,
            class_name,
        )

        return adapter_class

    def _build_provider_adapter(
        self,
        provider_id: str,
    ) -> Any:
        provider = self._provider_registry.get(
            provider_id
        )

        if provider is None:
            raise RuntimeError(
                f"PROVIDER_NOT_REGISTERED:{provider_id}"
            )

        if not provider.adapter_path:
            raise RuntimeError(
                f"PROVIDER_ADAPTER_NOT_CONFIGURED:"
                f"{provider.provider_id}"
            )

        if not provider.client_path:
            raise RuntimeError(
                f"PROVIDER_CLIENT_NOT_CONFIGURED:"
                f"{provider.provider_id}"
            )

        cached = self._adapter_cache.get(
            provider.provider_id
        )

        if cached is not None:
            return cached

        client_class = self._load_class(
            provider.client_path
        )

        adapter_class = self._load_class(
            provider.adapter_path
        )

        client = client_class()

        adapter = adapter_class(client)

        self._adapter_cache[
            provider.provider_id
        ] = adapter

        return adapter

    def _resolve_adapter(
        self,
        *,
        market: str,
        segment: str,
        instrument_type: str,
        capability: ProviderCapability,
    ) -> Any:
        resolution = (
            self._provider_resolver.resolve(
                ProviderResolutionRequest(
                    market=market,
                    segment=segment,
                    instrument_type=instrument_type,
                    capability=capability,
                )
            )
        )

        if not resolution.available:
            raise RuntimeError(
                "MARKET_DATA_PROVIDER_UNAVAILABLE: "
                f"{resolution.status.value}: "
                f"{resolution.reason or 'unknown'}"
            )

        provider = resolution.provider

        if provider is None:
            raise RuntimeError(
                "MARKET_DATA_PROVIDER_RESOLUTION_EMPTY"
            )

        return self._build_provider_adapter(
            provider.provider_id
        )

    @staticmethod
    def _normalise_identity(
        *,
        market: str | None,
        segment: str | None,
        instrument_type: str | None,
    ) -> tuple[str, str, str]:
        resolved_market = (
            str(market or "CRYPTO")
            .strip()
            .upper()
        )

        resolved_segment = (
            str(segment or "SPOT")
            .strip()
            .upper()
        )

        resolved_instrument_type = (
            str(instrument_type or "SPOT")
            .strip()
            .upper()
        )

        return (
            resolved_market,
            resolved_segment,
            resolved_instrument_type,
        )

    @staticmethod
    def _adapter_metadata(
        *,
        market: str,
        segment: str,
        instrument_type: str,
        metadata: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "market": market,
            "segment": segment,
            "instrument_type": instrument_type,
        }

        if metadata:
            result.update(
                {
                    str(key): value
                    for key, value in metadata.items()
                }
            )

        return result

    def get_snapshot(
        self,
        symbol: str,
        *,
        market: str = "CRYPTO",
        segment: str = "SPOT",
        instrument_type: str = "SPOT",
        metadata: Mapping[str, Any] | None = None,
    ) -> MarketSnapshot:
        """
        Resolve the eligible provider and dynamically
        construct its registered adapter.

        Backward-compatible default:

            market          = CRYPTO
            segment         = SPOT
            instrument_type = SPOT

        Therefore existing Binance callers that only pass
        `symbol` continue to work.

        Explicit market requests are resolved through the
        provider registry.

        Examples:

            CRYPTO / SPOT / SPOT
                -> Binance

            EQUITY / SPOT / EQUITY
                -> Massive

            INDEX / SPOT / INDEX
                -> Massive

            OPTIONS / OPTIONS / OPTION
                -> Massive

            FUTURES / FUTURES / FUTURE
                -> Massive

            FOREX / SPOT / FOREX
                -> Massive

            COMMODITY / SPOT / COMMODITY
                -> Massive
        """

        (
            resolved_market,
            resolved_segment,
            resolved_instrument_type,
        ) = self._normalise_identity(
            market=market,
            segment=segment,
            instrument_type=instrument_type,
        )

        adapter = self._resolve_adapter(
            market=resolved_market,
            segment=resolved_segment,
            instrument_type=resolved_instrument_type,
            capability=ProviderCapability.SNAPSHOT,
        )

        adapter_metadata = self._adapter_metadata(
            market=resolved_market,
            segment=resolved_segment,
            instrument_type=resolved_instrument_type,
            metadata=metadata,
        )

        try:
            snapshot = adapter.get_market_snapshot(
                symbol,
                metadata=adapter_metadata,
            )
        except TypeError:
            # Backward compatibility for adapters whose
            # existing implementation has not yet adopted
            # the optional metadata argument.
            snapshot = adapter.get_market_snapshot(
                symbol
            )

        self._snapshot_store.put(
            snapshot
        )

        return snapshot

    def get_snapshot_with_health(
        self,
        symbol: str,
        *,
        market: str = "CRYPTO",
        segment: str = "SPOT",
        instrument_type: str = "SPOT",
        metadata: Mapping[str, Any] | None = None,
    ) -> tuple[
        MarketSnapshot,
        MarketDataHealthResult,
    ]:
        snapshot = self.get_snapshot(
            symbol,
            market=market,
            segment=segment,
            instrument_type=instrument_type,
            metadata=metadata,
        )

        health = self._health_service.evaluate(
            snapshot
        )

        return snapshot, health

    def get_latest_snapshot(
        self,
        symbol: str,
        *,
        market: str = "CRYPTO",
        venue: str = "BINANCE",
    ) -> MarketSnapshot | None:
        return self._snapshot_store.get(
            market=market.strip().upper(),
            venue=venue.strip().upper(),
            symbol=symbol,
        )

    def get_latest_snapshot_with_health(
        self,
        symbol: str,
        *,
        market: str = "CRYPTO",
        venue: str = "BINANCE",
    ) -> tuple[
        MarketSnapshot | None,
        MarketDataHealthResult | None,
    ]:
        snapshot = self.get_latest_snapshot(
            symbol,
            market=market,
            venue=venue,
        )

        if snapshot is None:
            return None, None

        health = self._health_service.evaluate(
            snapshot
        )

        return snapshot, health

    def close(self) -> None:
        for adapter in self._adapter_cache.values():
            adapter.close()

        self._adapter_cache.clear()


__all__ = ["LiveMarketDataService"]