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


class FXMarketData:
    """
    ROBOMLM Foreign-Exchange Market Data Adapter.

    Responsibility:

        External FX source
            -> raw FX quote
            -> normalization
            -> canonical MarketSnapshot

    This layer MUST NOT produce:
        - signals
        - opportunities
        - rankings
        - BUY / SELL decisions
        - verdicts
        - risk decisions
    """

    def __init__(
        self,
        source: Any,
        *,
        source_name: str = "fx",
    ) -> None:
        self._source = source
        self._source_name = source_name

    @property
    def provider_name(self) -> str:
        return self._source_name

    def get_raw_quote(
        self,
        symbol: str,
    ) -> Mapping[str, Any]:
        """
        Retrieve provider-native FX quote.

        Supported source interfaces:
            - get_quote(symbol)
            - get_ticker(symbol)
            - get(symbol)

        The returned object must be a Mapping.
        """

        if hasattr(self._source, "get_quote"):
            raw = self._source.get_quote(symbol)

        elif hasattr(self._source, "get_ticker"):
            raw = self._source.get_ticker(symbol)

        elif hasattr(self._source, "get"):
            raw = self._source.get(symbol)

        else:
            raise TypeError(
                "FX source must provide get_quote(), "
                "get_ticker(), or get()"
            )

        if not isinstance(raw, Mapping):
            raise TypeError(
                "FX provider response must be a Mapping"
            )

        return raw

    @staticmethod
    def _decimal(
        value: Any,
    ) -> Decimal | None:
        if value is None or value == "":
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

    def get_market_snapshot(
        self,
        *,
        symbol: str,
        instrument_type: str = "FX",
        country: str | None = None,
    ) -> MarketSnapshot:
        """
        Normalize one FX quote into the canonical
        MarketSnapshot contract.
        """

        raw = self.get_raw_quote(symbol)

        now = datetime.now(timezone.utc)

        price = self._decimal(
            self._first(
                raw,
                "price",
                "last",
                "lastPrice",
                "last_price",
                "mid",
                "midPrice",
            )
        )

        bid = self._decimal(
            self._first(
                raw,
                "bid",
                "bidPrice",
                "bid_price",
        )
        )

        ask = self._decimal(
            self._first(
                raw,
                "ask",
                "askPrice",
                "ask_price",
            )
        )

        if price is None:
            if bid is not None and ask is not None:
                price = (bid + ask) / Decimal("2")

        if price is None:
            raise ValueError(
                f"FX quote does not contain usable price: {symbol}"
            )

        observation = MarketObservation(
            price=price,
            bid=bid,
            ask=ask,
            open=self._decimal(
                self._first(raw, "open", "openPrice")
            ),
            high=self._decimal(
                self._first(raw, "high", "highPrice")
            ),
            low=self._decimal(
                self._first(raw, "low", "lowPrice")
            ),
            close=self._decimal(
                self._first(
                    raw,
                    "close",
                    "closePrice",
                    "previousClose",
                )
            ),
            volume=self._decimal(
                self._first(
                    raw,
                    "volume",
                    "tickVolume",
                )
            ),
        )

        quality = MarketDataQuality(
            source=self._source_name,
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
                market="FX",
                segment="SPOT",
                country=country,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
            ),
            venue=VenueIdentity(
                venue=self._source_name.upper(),
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            metadata={
                "provider": self._source_name,
                "asset_class": "FX",
                "raw_symbol": symbol.upper(),
            },
        )