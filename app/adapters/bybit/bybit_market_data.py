from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from schemas.market.market_snapshot import (
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    VenueIdentity,
)

from app.adapters.bybit.bybit_client import BybitClient


class BybitMarketData:
    """
    ROBOMLM Bybit Market Data Adapter.

    Responsibility:
        Bybit Raw Data
            -> Normalization
            -> Canonical MarketSnapshot

    No intelligence.
    No signals.
    No opportunity generation.
    No decisions.
    """

    def __init__(
        self,
        client: BybitClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Bybit"

    def get_raw_ticker(
        self,
        symbol: str,
    ) -> Mapping[str, Any]:

        response = self._client.get(
            "/v5/market/tickers",
            {
                "category": "spot",
                "symbol": symbol.upper(),
            },
        )

        result = response.get("result", {})
        ticker_list = result.get("list", [])

        if not ticker_list:
            raise ValueError(
                f"No Bybit ticker data for {symbol}"
            )

        return ticker_list[0]

    def get_market_snapshot(
        self,
        symbol: str,
    ) -> MarketSnapshot:

        raw = self.get_raw_ticker(symbol)

        now = datetime.now(timezone.utc)

        price = Decimal(str(raw["lastPrice"]))

        high = Decimal(str(raw["highPrice24h"]))
        low = Decimal(str(raw["lowPrice24h"]))

        volume = Decimal(str(raw["volume24h"]))

        observation = MarketObservation(
            price=price,
            high=high,
            low=low,
            volume=volume,
        )

        quality = MarketDataQuality(
            source="bybit",
            source_timestamp=now,
            received_timestamp=now,
            latency_ms=0.0,
            is_complete=True,
        )

        state = MarketState(
            session=MarketSessionState.OPEN,
            halted=False,
            tradable=True,
        )

        return MarketSnapshot(
            market=MarketIdentity(
                market="CRYPTO",
                segment="SPOT",
                country=None,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type="CRYPTO",
            ),
            venue=VenueIdentity(
                venue="BYBIT",
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            metadata={
                "provider": "bybit",
                "raw_symbol": symbol.upper(),
            },
        )