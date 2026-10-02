from __future__ import annotations

from app.providers.provider_definitions import (
    BINANCE_PROVIDER,
    MASSIVE_PROVIDER,
)
from app.providers.provider_registry import ProviderRegistry


def build_provider_registry() -> ProviderRegistry:
    registry = ProviderRegistry()

    registry.register(BINANCE_PROVIDER)
    registry.register(MASSIVE_PROVIDER)

    return registry


__all__ = ["build_provider_registry"]