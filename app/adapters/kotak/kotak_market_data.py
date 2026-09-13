from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from app.adapters.kotak.kotak_client import KotakClient

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


class KotakMarketData:
    """
    ROBOMLM Kotak Neo market-data adapter.

    Flow:

        Kotak Neo raw response
            -> provider-field normalization
            -> canonical MarketSnapshot

    This layer MUST NOT produce:
        - signals
        - opportunities
        - rankings
        - BUY / SELL
        - verdicts
        - risk decisions
    """

    def __init__(
        self,
        client: KotakClient,
        *,
        quote_endpoint: str,
    ) -> None:
        if not quote_endpoint:
            raise ValueError(
                "quote_endpoint is required"
            )

        self._client = client
        self._quote_endpoint = quote_endpoint

    @property
    def provider_name(self) -> str:
        return "Kotak Neo"

    def get_raw_quote(
        self,
        *,
        exchange_segment: str,
        instrument_token: str,
        symbol: str | None = None,
    ) -> Mapping[str, Any]:
        """
        Retrieve provider-native quote data.

        The endpoint is injected because Kotak Neo's current
        post-login API uses a dynamic base URL/API configuration.
        """

        payload: dict[str, Any] = {
            "exchangeSegment": exchange_segment,
            "instrumentToken": instrument_token,
        }

        if symbol:
            payload["symbol"] = symbol

        response = self._client.get_quotes(
            endpoint=self._quote_endpoint,
            payload=payload,
        )

        if not isinstance(response, Mapping):
            raise ValueError(
                "Invalid Kotak Neo quote response"
            )

        return response

    @staticmethod
    def _decimal(
        value: Any,
    ) -> Decimal | None:
        if value is None:
            return None

        if value == "":
            return None

        return Decimal(str(value))

    @staticmethod
    def _first(
        data: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in data:
                return data[key]

        return None

    @staticmethod
    def _extract_quote_data(
        response: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Normalize common Kotak response envelopes without
        assuming intelligence semantics.
        """

        for key in (
            "data",
            "result",
            "quote",
            "quotes",
        ):
            value = response.get(key)

            if isinstance(value, Mapping):
                return value

        return response

    def get_market_snapshot(
        self,
        *,
        symbol: str,
        exchange_segment: str,
        instrument_token: str,
        instrument_type: str = "EQUITY",
        market: str = "INDIA",
        country: str | None = "IN",
    ) -> MarketSnapshot:
        """
        Convert one Kotak Neo quote into canonical MarketSnapshot.
        """

        response = self.get_raw_quote(
            exchange_segment=exchange_segment,
            instrument_token=instrument_token,
            symbol=symbol,
        )

        raw = self._extract_quote_data(response)

        now = datetime.now(timezone.utc)

        price = self._decimal(
            self._first(
                raw,
                "ltp",
                "lastPrice",
                "last_price",
                "lastTradedPrice",
                "LTP",
            )
        )

        if price is None:
            raise ValueError(
                "Kotak Neo quote does not contain a usable LTP"
            )

        open_price = self._decimal(
            self._first(
                raw,
                "open",
                "openPrice",
            )
        )

        high = self._decimal(
            self._first(
                raw,
                "high",
                "highPrice",
            )
        )

        low = self._decimal(
            self._first(
                raw,
                "low",
                "lowPrice",
            )
        )

        close = self._decimal(
            self._first(
                raw,
                "close",
                "closePrice",
                "previousClose",
            )
        )

        volume = self._decimal(
            self._first(
                raw,
                "volume",
                "totalVolume",
            )
        )

        open_interest = self._decimal(
            self._first(
                raw,
                "openInterest",
                "open_interest",
                "oi",
            )
        )

        bid = self._decimal(
            self._first(
                raw,
                "bid",
                "bidPrice",
                "bestBid",
            )
        )

        ask = self._decimal(
            self._first(
                raw,
                "ask",
                "askPrice",
                "bestAsk",
            )
        )

        observation = MarketObservation(
            price=price,
            bid=bid,
            ask=ask,
            open=open_price,
            high=high,
            low=low,
            close=close,
            volume=volume,
            open_interest=open_interest,
        )

        quality = MarketDataQuality(
            source="kotak_neo",
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

        metadata = {
            "provider": "kotak_neo",
            "exchange_segment": exchange_segment,
            "instrument_token": instrument_token,
            "raw_symbol": symbol,
        }

        return MarketSnapshot(
            market=MarketIdentity(
                market=market,
                segment=exchange_segment,
                country=country,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
                instrument_id=instrument_token,
            ),
            venue=VenueIdentity(
                venue="KOTAK_NEO",
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            metadata=metadata,
        )