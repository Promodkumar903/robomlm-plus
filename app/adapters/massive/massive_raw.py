from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(slots=True)
class MassiveRawMarketData:
    """
    Lossless Massive provider-data boundary.

    This class deliberately does NOT normalize provider data into
    MarketSnapshot and does NOT calculate intelligence.

    It preserves:
        - spot/equity data
        - index data
        - futures data
        - options data
        - option chains
        - calls / puts
        - strikes / expiries
        - trades
        - quotes / NBBO
        - OHLC / aggregates
        - volume
        - turnover where supplied
        - open interest
        - Greeks
        - implied volatility
        - percentage/value changes
        - contract/reference metadata
        - provider timestamps
        - exchange identifiers
        - trade conditions
        - raw provider fields

    Unsupported provider capabilities such as full Level-2 DOM,
    iceberg-order identification, and actual execution-order flow
    are NOT fabricated.
    """

    payload: dict[str, Any]

    market: str | None = None
    asset_class: str | None = None
    symbol: str | None = None
    provider_symbol: str | None = None
    venue: str | None = None
    data_type: str | None = None

    endpoint: str | None = None
    request_id: str | None = None
    status: str | None = None
    next_url: str | None = None

    capabilities: dict[str, bool] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.payload = dict(self.payload)

        self.market = self._first_string(
            self.payload,
            "market",
            "market_type",
        )

        self.asset_class = self._first_string(
            self.payload,
            "asset_class",
            "assetClass",
        )

        self.symbol = self._first_string(
            self.payload,
            "ticker",
            "symbol",
            "options_ticker",
            "contract_ticker",
        )

        self.provider_symbol = self.symbol

        self.venue = self._first_string(
            self.payload,
            "exchange",
            "venue",
            "primary_exchange",
        )

        self.data_type = self._first_string(
            self.payload,
            "data_type",
            "type",
        )

        self.request_id = self._first_string(
            self.payload,
            "request_id",
        )

        self.status = self._first_string(
            self.payload,
            "status",
        )

        self.next_url = self._first_string(
            self.payload,
            "next_url",
        )

        self.capabilities = self._detect_capabilities(
            self.payload
        )

    @staticmethod
    def _first_string(
        payload: Mapping[str, Any],
        *keys: str,
    ) -> str | None:
        for key in keys:
            value = payload.get(key)

            if value is None:
                continue

            text = str(value).strip()

            if text:
                return text

        return None

    @staticmethod
    def _detect_capabilities(
        payload: Mapping[str, Any],
    ) -> dict[str, bool]:
        """
        Detect what the provider response actually contains.

        This is presence detection only.
        It does not calculate missing market information.
        """

        def present(*keys: str) -> bool:
            return any(
                key in payload
                and payload.get(key) is not None
                for key in keys
            )

        return {
            # Price / OHLC
            "ltp": present(
                "price",
                "last",
                "lastPrice",
                "last_trade",
                "lastTrade",
                "lastTradePrice",
            ),
            "open": present(
                "open",
                "o",
            ),
            "high": present(
                "high",
                "h",
            ),
            "low": present(
                "low",
                "l",
            ),
            "close": present(
                "close",
                "c",
            ),

            # Change
            "change": present(
                "change",
                "todaysChange",
                "price_change",
                "change_value",
            ),
            "change_percent": present(
                "change_percent",
                "todaysChangePerc",
                "percent_change",
                "change_percent",
            ),

            # Volume / turnover
            "volume": present(
                "volume",
                "v",
                "size",
            ),
            "turnover": present(
                "turnover",
                "quoteVolume",
                "value",
            ),

            # Quote / NBBO
            "bid": present(
                "bid",
                "bid_price",
                "bidPrice",
            ),
            "ask": present(
                "ask",
                "ask_price",
                "askPrice",
            ),
            "bid_size": present(
                "bid_size",
                "bidSize",
                "bidsize",
            ),
            "ask_size": present(
                "ask_size",
                "askSize",
                "asksize",
            ),

            # Trade information
            "trades": present(
                "trades",
                "lastTrade",
                "last_trade",
                "results",
            ),
            "trade_price": present(
                "price",
                "trade_price",
                "lastPrice",
            ),
            "trade_size": present(
                "size",
                "trade_size",
                "lastTradeSize",
            ),
            "trade_conditions": present(
                "conditions",
                "trade_conditions",
            ),
            "trade_exchange": present(
                "exchange",
                "trade_exchange",
            ),

            # Options
            "option_type": present(
                "contract_type",
                "option_type",
                "type",
            ),
            "strike": present(
                "strike_price",
                "strike",
            ),
            "expiration": present(
                "expiration_date",
                "expiration",
            ),
            "underlying": present(
                "underlying_ticker",
                "underlying",
            ),

            # Options analytics
            "open_interest": present(
                "open_interest",
                "openInterest",
            ),
            "implied_volatility": present(
                "implied_volatility",
                "impliedVolatility",
                "iv",
            ),
            "delta": present(
                "delta",
            ),
            "gamma": present(
                "gamma",
            ),
            "theta": present(
                "theta",
            ),
            "vega": present(
                "vega",
            ),
            "rho": present(
                "rho",
            ),

            # Contract/reference information
            "contract": present(
                "contract",
                "contract_id",
                "contract_type",
                "product_code",
            ),
            "contract_size": present(
                "contract_size",
                "shares_per_contract",
            ),
            "tick_size": present(
                "tick_size",
            ),

            # Futures/session
            "settlement": present(
                "settlement_price",
                "settlement",
            ),
            "session": present(
                "session",
                "session_end_date",
            ),

            # Timestamp
            "timestamp": present(
                "timestamp",
                "t",
                "updated",
                "updated_at",
            ),

            # Provider pagination / metadata
            "request_id": present(
                "request_id",
            ),
            "next_url": present(
                "next_url",
            ),
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Return the complete provider payload without removing fields.
        """

        return dict(self.payload)

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Read any provider-native field without normalization.
        """

        return self.payload.get(
            key,
            default,
        )

    def contains(self, key: str) -> bool:
        return key in self.payload

    def raw_results(self) -> list[Any]:
        """
        Return provider result array when present.

        Massive commonly uses:
            results: [...]
        """

        results = self.payload.get("results")

        if isinstance(results, list):
            return list(results)

        return []

    def has_capability(
        self,
        capability: str,
    ) -> bool:
        return bool(
            self.capabilities.get(
                capability,
                False,
            )
        )


@dataclass(slots=True)
class MassiveRawResponse:
    """
    Container for an entire Massive REST response.

    Keeps the response envelope and all provider-native records.
    """

    payload: dict[str, Any]

    endpoint: str | None = None

    def __post_init__(self) -> None:
        self.payload = dict(self.payload)

    @property
    def status(self) -> str | None:
        value = self.payload.get("status")

        if value is None:
            return None

        return str(value)

    @property
    def count(self) -> int | None:
        value = self.payload.get("count")

        if value is None:
            return None

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @property
    def request_id(self) -> str | None:
        value = self.payload.get(
            "request_id"
        )

        if value is None:
            return None

        return str(value)

    @property
    def next_url(self) -> str | None:
        value = self.payload.get(
            "next_url"
        )

        if value is None:
            return None

        return str(value)

    @property
    def results(self) -> list[Any]:
        value = self.payload.get(
            "results"
        )

        if isinstance(value, list):
            return list(value)

        return []

    def raw(self) -> dict[str, Any]:
        return dict(self.payload)

    def records(
        self,
    ) -> list[MassiveRawMarketData]:
        return [
            MassiveRawMarketData(
                item
            )
            for item in self.results
            if isinstance(
                item,
                Mapping,
            )
        ]


# Explicit provider capability map.
#
# True means Massive documentation exposes this category.
# False means this adapter must not pretend that the provider
# supplies it.
MASSIVE_DATA_CAPABILITIES: dict[str, bool] = {
    "spot_equity": True,
    "index": True,
    "futures": True,
    "options": True,
    "options_chain": True,
    "calls": True,
    "puts": True,
    "ohlc": True,
    "ltp": True,
    "trades": True,
    "quotes": True,
    "nbbo": True,
    "volume": True,
    "open_interest": True,
    "implied_volatility": True,
    "delta": True,
    "gamma": True,
    "theta": True,
    "vega": True,
    "rho": True,
    "percentage_change": True,
    "contract_metadata": True,
    "trade_conditions": True,
    "exchange": True,
    "full_level_2_dom": False,
    "order_book": False,
    "iceberg_order_detection": False,
    "execution_order_flow": False,
    "broker_order_status": False,
}


def capability_available(
    capability: str,
) -> bool:
    return bool(
        MASSIVE_DATA_CAPABILITIES.get(
            capability,
            False,
        )
    )


__all__ = [
    "MassiveRawMarketData",
    "MassiveRawResponse",
    "MASSIVE_DATA_CAPABILITIES",
    "capability_available",
]