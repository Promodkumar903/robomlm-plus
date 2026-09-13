from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from schemas.market.market_snapshot import (
    ContractIdentity,
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    VenueIdentity,
)


class CommodityMarketData:
    """
    ROBOMLM Commodity Market Data Adapter.

    Responsibility:

        External commodity source
            -> raw quote
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
        source_name: str = "commodity",
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
        Retrieve provider-native commodity quote.
        """

        if hasattr(self._source, "get_quote"):
            raw = self._source.get_quote(symbol)

        elif hasattr(self._source, "get_ticker"):
            raw = self._source.get_ticker(symbol)

        elif hasattr(self._source, "get"):
            raw = self._source.get(symbol)

        else:
            raise TypeError(
                "Commodity source must provide get_quote(), "
                "get_ticker(), or get()"
            )

        if not isinstance(raw, Mapping):
            raise TypeError(
                "Commodity provider response must be a Mapping"
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
        exchange_segment: str = "COMMODITY",
        instrument_type: str = "COMMODITY",
        country: str | None = None,
        instrument_id: str | None = None,
        contract_id: str | None = None,
        contract_type: str | None = None,
        expiry: datetime | None = None,
        strike: Decimal | None = None,
        option_type: str | None = None,
    ) -> MarketSnapshot:
        """
        Normalize one commodity quote into the canonical
        MarketSnapshot contract.

        Contract information is preserved when supplied.
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
                "ltp",
            )
        )

        if price is None:
            raise ValueError(
                f"Commodity quote does not contain usable "
                f"price: {symbol}"
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

        observation = MarketObservation(
            price=price,
            bid=bid,
            ask=ask,
            open=self._decimal(
                self._first(
                    raw,
                    "open",
                    "openPrice",
                )
            ),
            high=self._decimal(
                self._first(
                    raw,
                    "high",
                    "highPrice",
                )
            ),
            low=self._decimal(
                self._first(
                    raw,
                    "low",
                    "lowPrice",
                )
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
                    "totalVolume",
                )
            ),
            turnover=self._decimal(
                self._first(
                    raw,
                    "turnover",
                    "totalTurnover",
                )
            ),
            open_interest=self._decimal(
                self._first(
                    raw,
                    "openInterest",
                    "open_interest",
                    "oi",
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

        contract = None

        if any(
            value is not None
            for value in (
                contract_id,
                contract_type,
                expiry,
                strike,
                option_type,
            )
        ):
            contract = ContractIdentity(
                contract_id=contract_id,
                contract_type=contract_type,
                expiry=expiry,
                strike=strike,
                option_type=option_type,
            )

        return MarketSnapshot(
            market=MarketIdentity(
                market=market_name(country),
                segment=exchange_segment,
                country=country,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
                instrument_id=instrument_id,
            ),
            venue=VenueIdentity(
                venue=self._source_name.upper(),
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            contract=contract,
            metadata={
                "provider": self._source_name,
                "asset_class": "COMMODITY",
                "exchange_segment": exchange_segment,
                "raw_symbol": symbol.upper(),
            },
        )


def market_name(
    country: str | None,
) -> str:
    """
    Keep market identity deterministic without introducing
    trading intelligence.
    """
    if country:
        return country.upper()

    return "COMMODITY"