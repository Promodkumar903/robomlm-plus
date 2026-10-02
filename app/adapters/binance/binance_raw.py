from __future__ import annotations

from typing import Any, Mapping


class BinanceRawMarketData:
    """
    Provider-native Binance market response.

    This layer preserves Binance fields exactly as received.
    It does not normalize into MarketSnapshot and does not
    calculate health or intelligence.
    """

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self.payload = dict(payload)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)