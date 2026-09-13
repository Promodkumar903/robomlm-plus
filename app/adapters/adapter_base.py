from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from schemas.market.market_snapshot import MarketSnapshot


class AdapterBase(ABC):
    """Canonical market-data adapter boundary."""

    ADAPTER_TYPE = "market_data"
    CANONICAL_OUTPUT = MarketSnapshot

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the external provider/source name."""
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        """Establish or validate the provider data connection."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release provider resources held by the adapter."""
        raise NotImplementedError

    @abstractmethod
    def is_connected(self) -> bool:
        """Return provider connection state only."""
        raise NotImplementedError

    @abstractmethod
    def fetch_raw_market_data(self, symbol: str) -> Mapping[str, Any]:
        """Retrieve provider-native raw market data."""
        raise NotImplementedError

    @abstractmethod
    def get_market_snapshot(self, symbol: str, *, metadata: Mapping[str, Any] | None = None) -> MarketSnapshot:
        """Retrieve, normalize, validate, and return one MarketSnapshot."""
        raise NotImplementedError

    def ensure_raw_mapping(self, raw_data: Mapping[str, Any]) -> Mapping[str, Any]:
        """Validate the raw provider-data boundary."""
        if not isinstance(raw_data, Mapping):
            raise TypeError("Raw adapter data must implement Mapping")
        return raw_data

    def validate_canonical_output(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        """Validate that only MarketSnapshot leaves the adapter boundary."""
        if not isinstance(snapshot, self.CANONICAL_OUTPUT):
            raise TypeError("Adapter output must be a MarketSnapshot")
        return snapshot

    def adapter_identity(self) -> dict[str, str]:
        """Return structural adapter identity."""
        return {
            "adapter_type": self.ADAPTER_TYPE,
            "provider": self.provider_name,
            "canonical_output": self.CANONICAL_OUTPUT.__name__,
        }

    def canonical_output_type(self) -> type[MarketSnapshot]:
        """Return the canonical MarketSnapshot contract."""
        return self.CANONICAL_OUTPUT


__all__ = ["AdapterBase"]
