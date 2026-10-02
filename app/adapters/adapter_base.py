from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from schemas.market.market_data_packet import MarketDataPacket
from schemas.market.market_snapshot import MarketSnapshot


class AdapterBase(ABC):
    """Canonical base contract for market-data provider adapters."""

    ADAPTER_TYPE = "market_data"
    CANONICAL_OUTPUT = MarketSnapshot
    RAW_OUTPUT = MarketDataPacket

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_raw_market_data(self, symbol: str) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_raw_market_packet(self, symbol: str, *, metadata: Mapping[str, Any] | None = None, **kwargs: Any) -> MarketDataPacket:
        raise NotImplementedError

    @abstractmethod
    def get_market_snapshot(self, symbol: str, *, metadata: Mapping[str, Any] | None = None) -> MarketSnapshot:
        raise NotImplementedError

    @staticmethod
    def ensure_raw_mapping(value: Any) -> Mapping[str, Any]:
        if not isinstance(value, Mapping):
            raise TypeError("Provider market-data response must be a mapping")
        return value

    def validate_raw_packet(self, packet: MarketDataPacket) -> MarketDataPacket:
        if not isinstance(packet, self.RAW_OUTPUT):
            raise TypeError(
                f"Adapter {self.provider_name} returned {type(packet).__name__}; "
                f"expected {self.RAW_OUTPUT.__name__}"
            )

        provider = str(packet.metadata.get("provider", "")).strip()
        if provider and provider.lower() != self.provider_name.lower():
            raise ValueError(
                f"Packet provider mismatch: expected {self.provider_name!r}, "
                f"received {provider!r}"
            )

        return packet

    def validate_canonical_output(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        if not isinstance(snapshot, self.CANONICAL_OUTPUT):
            raise TypeError(
                f"Adapter {self.provider_name} returned {type(snapshot).__name__}; "
                f"expected {self.CANONICAL_OUTPUT.__name__}"
            )
        return snapshot

    def adapter_identity(self) -> dict[str, Any]:
        return {
            "adapter_type": self.ADAPTER_TYPE,
            "provider": self.provider_name,
            "raw_output": self.RAW_OUTPUT.__name__,
            "canonical_output": self.CANONICAL_OUTPUT.__name__,
        }

    @classmethod
    def raw_output_type(cls) -> type[MarketDataPacket]:
        return cls.RAW_OUTPUT

    @classmethod
    def canonical_output_type(cls) -> type[MarketSnapshot]:
        return cls.CANONICAL_OUTPUT


__all__ = ["AdapterBase"]
