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

from app.adapters.binance.binance_client import BinanceClient


class BinanceMarketData:
    """
    Binance market-data adapter.

    Responsibility:
        Binance raw ticker
            -> normalization
            -> MarketSnapshot

    No intelligence.
    No signals.
    No opportunities.
    """

    def __init__(
        self,
        client: BinanceClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Binance"

    def get_raw_ticker(
        self,
        symbol: str,
    ) -> Mapping[str, Any]:
        return self._client.get(
            "/api/v3/ticker/24hr",
            {"symbol": symbol.upper()},
        )

    def get_market_snapshot(
        self,
        symbol: str,
    ) -> MarketSnapshot:

        raw = self.get_raw_ticker(symbol)

        now = datetime.now(timezone.utc)

        price = Decimal(str(raw["lastPrice"]))
        high = Decimal(str(raw["highPrice"]))
        low = Decimal(str(raw["lowPrice"]))
        volume = Decimal(str(raw["volume"]))

        observation = MarketObservation(
            price=price,
            high=high,
            low=low,
            volume=volume,
        )

        quality = MarketDataQuality(
            source="binance",
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
                venue="BINANCE",
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            metadata={
                "provider": "binance",
                "raw_symbol": raw.get("symbol"),
            },
        )