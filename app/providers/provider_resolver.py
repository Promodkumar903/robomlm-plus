from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.providers.provider_contract import (
    ProviderCapability,
    ProviderContract,
    ProviderStatus,
)
from app.providers.provider_registry import ProviderRegistry


class ProviderResolutionStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    NOT_ENTITLED = "NOT_ENTITLED"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ProviderResolutionRequest:
    market: str
    segment: str
    instrument_type: str
    capability: ProviderCapability = ProviderCapability.SNAPSHOT


@dataclass(frozen=True, slots=True)
class ProviderResolutionResult:
    status: ProviderResolutionStatus
    provider: ProviderContract | None
    reason: str | None = None

    @property
    def available(self) -> bool:
        return (
            self.status
            == ProviderResolutionStatus.AVAILABLE
        )


class ProviderResolver:
    """
    Resolves a market request to a registered provider.

    This layer does not fetch market data and does not
    construct MarketSnapshot objects.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
    ) -> None:
        self._registry = registry

    def resolve(
        self,
        request: ProviderResolutionRequest,
    ) -> ProviderResolutionResult:
        market = request.market.strip().upper()
        segment = request.segment.strip().upper()
        instrument_type = (
            request.instrument_type.strip().upper()
        )

        if not market or not segment or not instrument_type:
            return ProviderResolutionResult(
                status=ProviderResolutionStatus.UNKNOWN,
                provider=None,
                reason="INCOMPLETE_MARKET_IDENTITY",
            )

        candidates = [
            provider
            for provider in self._registry.all()
            if market in provider.markets
            and segment in provider.segments
            and instrument_type in provider.instrument_types
        ]

        if not candidates:
            return ProviderResolutionResult(
                status=ProviderResolutionStatus.NOT_SUPPORTED,
                provider=None,
                reason=(
                    f"NO_PROVIDER_FOR:"
                    f"{market}/{segment}/{instrument_type}"
                ),
            )

        capability_matches = [
            provider
            for provider in candidates
            if provider.capability(
                request.capability
            ) is not None
        ]

        if not capability_matches:
            return ProviderResolutionResult(
                status=ProviderResolutionStatus.NOT_SUPPORTED,
                provider=None,
                reason=(
                    f"CAPABILITY_NOT_REGISTERED:"
                    f"{request.capability.value}"
                ),
            )

        for provider in capability_matches:
            capability = provider.capability(
                request.capability
            )

            if capability is None:
                continue

            if capability.status == ProviderStatus.AVAILABLE:
                if provider.status == ProviderStatus.AVAILABLE:
                    return ProviderResolutionResult(
                        status=ProviderResolutionStatus.AVAILABLE,
                        provider=provider,
                    )

                if (
                    provider.status
                    == ProviderStatus.NOT_ENTITLED
                ):
                    return ProviderResolutionResult(
                        status=ProviderResolutionStatus.NOT_ENTITLED,
                        provider=provider,
                        reason="PROVIDER_NOT_ENTITLED",
                    )

                if (
                    provider.status
                    == ProviderStatus.TEMPORARILY_UNAVAILABLE
                ):
                    return ProviderResolutionResult(
                        status=ProviderResolutionStatus.TEMPORARILY_UNAVAILABLE,
                        provider=provider,
                        reason="PROVIDER_TEMPORARILY_UNAVAILABLE",
                    )

                if provider.status == ProviderStatus.NOT_SUPPORTED:
                    return ProviderResolutionResult(
                        status=ProviderResolutionStatus.NOT_SUPPORTED,
                        provider=provider,
                        reason="PROVIDER_NOT_SUPPORTED",
                    )

            if capability.status == ProviderStatus.NOT_ENTITLED:
                return ProviderResolutionResult(
                    status=ProviderResolutionStatus.NOT_ENTITLED,
                    provider=provider,
                    reason="CAPABILITY_NOT_ENTITLED",
                )

            if (
                capability.status
                == ProviderStatus.TEMPORARILY_UNAVAILABLE
            ):
                return ProviderResolutionResult(
                    status=ProviderResolutionStatus.TEMPORARILY_UNAVAILABLE,
                    provider=provider,
                    reason="CAPABILITY_TEMPORARILY_UNAVAILABLE",
                )

            if capability.status == ProviderStatus.NOT_SUPPORTED:
                return ProviderResolutionResult(
                    status=ProviderResolutionStatus.NOT_SUPPORTED,
                    provider=provider,
                    reason="CAPABILITY_NOT_SUPPORTED",
                )

        return ProviderResolutionResult(
            status=ProviderResolutionStatus.UNKNOWN,
            provider=None,
            reason="PROVIDER_STATUS_UNKNOWN",
        )