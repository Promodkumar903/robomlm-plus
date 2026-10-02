from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet


class ProviderStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    NOT_ENTITLED = "NOT_ENTITLED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    UNKNOWN = "UNKNOWN"


class ProviderCapability(str, Enum):
    TICKER = "ticker"
    SNAPSHOT = "snapshot"
    OHLC = "ohlc"
    CANDLES = "candles"
    TRADES = "trades"
    ORDERBOOK = "orderbook"
    QUOTES = "quotes"
    VOLUME = "volume"
    OPEN_INTEREST = "open_interest"
    OPTIONS_CHAIN = "options_chain"
    FUTURES = "futures"
    FX_SPOT = "fx_spot"
    FUNDAMENTALS = "fundamentals"


@dataclass(frozen=True, slots=True)
class ProviderCapabilityState:
    capability: ProviderCapability
    status: ProviderStatus
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderContract:
    provider_id: str
    provider_name: str

    markets: FrozenSet[str] = field(
        default_factory=frozenset
    )

    segments: FrozenSet[str] = field(
        default_factory=frozenset
    )

    instrument_types: FrozenSet[str] = field(
        default_factory=frozenset
    )

    capabilities: tuple[
        ProviderCapabilityState,
        ...,
    ] = field(default_factory=tuple)

    status: ProviderStatus = ProviderStatus.UNKNOWN

    adapter_path: str | None = None

    client_path: str | None = None

    def supports(
        self,
        capability: ProviderCapability,
    ) -> bool:
        return any(
            item.capability == capability
            and item.status == ProviderStatus.AVAILABLE
            for item in self.capabilities
        )

    def capability(
        self,
        capability: ProviderCapability,
    ) -> ProviderCapabilityState | None:
        for item in self.capabilities:
            if item.capability == capability:
                return item

        return None