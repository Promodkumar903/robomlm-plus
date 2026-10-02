from __future__ import annotations

from app.providers.provider_contract import (
    ProviderContract,
    ProviderCapability,
    ProviderStatus,
)


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[
            str,
            ProviderContract,
        ] = {}

    def register(
        self,
        provider: ProviderContract,
    ) -> None:
        provider_id = provider.provider_id.strip().upper()

        if not provider_id:
            raise ValueError(
                "provider_id must not be empty"
            )

        self._providers[provider_id] = provider

    def get(
        self,
        provider_id: str,
    ) -> ProviderContract | None:
        return self._providers.get(
            provider_id.strip().upper()
        )

    def all(self) -> tuple[ProviderContract, ...]:
        return tuple(self._providers.values())

    def supports(
        self,
        provider_id: str,
        capability: ProviderCapability,
    ) -> bool:
        provider = self.get(provider_id)

        if provider is None:
            return False

        return provider.supports(capability)