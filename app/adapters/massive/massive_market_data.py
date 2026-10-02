from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from app.adapters.massive.massive_client import MassiveClient
from app.adapters.massive.massive_raw import (
    MassiveRawMarketData,
    MassiveRawResponse,
)

from schemas.market.market_snapshot import (
    ContractIdentity,
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    MarketTiming,
    ObservationKind,
    VenueIdentity,
)


class MassiveMarketData:
    """
    Massive market-data adapter.

    Provider:
        Massive

    Raw boundary:
        MassiveRawMarketData
        MassiveRawResponse

    Canonical boundary:
        MarketSnapshot

    Supported domains:
        - EQUITY
        - INDEX
        - OPTIONS
        - FUTURES
        - FOREX

    This adapter preserves provider-native responses and does not
    fabricate unavailable market microstructure.

    Full Level-2 DOM, iceberg-order identification and broker
    execution-order flow are NOT invented here.
    """

    def __init__(
        self,
        client: MassiveClient,
    ) -> None:
        self._client = client
        self._last_raw: MassiveRawMarketData | None = None
        self._last_response: MassiveRawResponse | None = None

    # ------------------------------------------------------------------
    # IDENTITY / LIFECYCLE
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return self._client.provider_name

    @property
    def last_raw(self) -> MassiveRawMarketData | None:
        return self._last_raw

    @property
    def last_response(self) -> MassiveRawResponse | None:
        return self._last_response

    def connect(self) -> None:
        self._client.connect()

    def close(self) -> None:
        self._client.close()

    def is_connected(self) -> bool:
        return self._client.is_connected()

    # ------------------------------------------------------------------
    # STOCK / EQUITY
    # ------------------------------------------------------------------

    def get_equity_snapshot(
        self,
        symbol: str,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v2/snapshot/locale/us/markets/stocks/"
            f"tickers/{symbol.upper()}",
        )

        return self._remember_response(
            payload,
            "/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}",
        )

    def get_equity_full_market_snapshot(
        self,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/v2/snapshot/locale/us/markets/stocks/tickers"
        )

        return self._remember_response(
            payload,
            "/v2/snapshot/locale/us/markets/stocks/tickers",
        )

    def get_equity_aggregates(
        self,
        symbol: str,
        *,
        multiplier: int,
        timespan: str,
        date_from: str,
        date_to: str,
        adjusted: bool = True,
        sort: str = "asc",
        limit: int = 5000,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            (
                f"/v2/aggs/ticker/{symbol.upper()}/"
                f"range/{multiplier}/{timespan}/"
                f"{date_from}/{date_to}"
            ),
            params={
                "adjusted": str(adjusted).lower(),
                "sort": sort,
                "limit": limit,
            },
        )

        return self._remember_response(
            payload,
            "/v2/aggs/ticker/{ticker}/range/"
            "{multiplier}/{timespan}/{from}/{to}",
        )

    def get_equity_trades(
        self,
        symbol: str,
        *,
        timestamp: str | None = None,
        timestamp_gte: str | None = None,
        timestamp_gt: str | None = None,
        timestamp_lte: str | None = None,
        timestamp_lt: str | None = None,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v3/trades/{symbol.upper()}",
            params=self._optional_params(
                {
                    "timestamp": timestamp,
                    "timestamp.gte": timestamp_gte,
                    "timestamp.gt": timestamp_gt,
                    "timestamp.lte": timestamp_lte,
                    "timestamp.lt": timestamp_lt,
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/v3/trades/{ticker}",
        )

    def get_equity_quotes(
        self,
        symbol: str,
        *,
        timestamp: str | None = None,
        timestamp_gte: str | None = None,
        timestamp_gt: str | None = None,
        timestamp_lte: str | None = None,
        timestamp_lt: str | None = None,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v3/quotes/{symbol.upper()}",
            params=self._optional_params(
                {
                    "timestamp": timestamp,
                    "timestamp.gte": timestamp_gte,
                    "timestamp.gt": timestamp_gt,
                    "timestamp.lte": timestamp_lte,
                    "timestamp.lt": timestamp_lt,
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/v3/quotes/{ticker}",
        )

    # ------------------------------------------------------------------
    # OPTIONS
    # ------------------------------------------------------------------

    def get_option_snapshot(
        self,
        underlying: str,
        option_contract: str,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            (
                f"/v3/snapshot/options/"
                f"{underlying.upper()}/"
                f"{option_contract.upper()}"
            )
        )

        return self._remember_response(
            payload,
            "/v3/snapshot/options/"
            "{underlyingAsset}/{optionContract}",
        )

    def get_option_chain(
        self,
        underlying: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v3/snapshot/options/{underlying.upper()}",
            params=params,
        )

        return self._remember_response(
            payload,
            "/v3/snapshot/options/{underlyingAsset}",
        )

    def get_option_contract(
        self,
        option_contract: str,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            (
                "/v3/reference/options/contracts/"
                f"{option_contract.upper()}"
            )
        )

        return self._remember_response(
            payload,
            "/v3/reference/options/contracts/{options_ticker}",
        )

    def get_option_contracts(
        self,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/v3/reference/options/contracts",
            params=params,
        )

        return self._remember_response(
            payload,
            "/v3/reference/options/contracts",
        )

    def get_option_trades(
        self,
        option_contract: str,
        *,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v3/trades/{option_contract.upper()}",
            params=self._optional_params(
                {
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/v3/trades/{optionsTicker}",
        )

    def get_option_quotes(
        self,
        option_contract: str,
        *,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/v3/quotes/{option_contract.upper()}",
            params=self._optional_params(
                {
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/v3/quotes/{optionsTicker}",
        )

    # ------------------------------------------------------------------
    # FUTURES
    # ------------------------------------------------------------------

    def get_futures_snapshot(
        self,
        *,
        ticker: str | None = None,
        product_code: str | None = None,
        limit: int = 100,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/futures/v1/snapshot",
            params=self._optional_params(
                {
                    "ticker": ticker,
                    "product_code": product_code,
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/futures/v1/snapshot",
        )

    def get_futures_aggregates(
        self,
        ticker: str,
        *,
        resolution: str,
        window_start: str,
        window_end: str,
        limit: int = 5000,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/futures/v1/aggs/{ticker.upper()}",
            params={
                "resolution": resolution,
                "window_start": window_start,
                "window_end": window_end,
                "limit": limit,
            },
        )

        return self._remember_response(
            payload,
            "/futures/v1/aggs/{ticker}",
        )

    def get_futures_trades(
        self,
        ticker: str,
        *,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/futures/v1/trades/{ticker.upper()}",
            params=self._optional_params(
                {
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/futures/v1/trades/{ticker}",
        )

    def get_futures_quotes(
        self,
        ticker: str,
        *,
        limit: int = 5000,
        sort: str | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            f"/futures/v1/quotes/{ticker.upper()}",
            params=self._optional_params(
                {
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/futures/v1/quotes/{ticker}",
        )

    def get_futures_products(
        self,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/futures/v1/products",
            params=params,
        )

        return self._remember_response(
            payload,
            "/futures/v1/products",
        )

    def get_futures_contracts(
        self,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/futures/v1/contracts",
            params=params,
        )

        return self._remember_response(
            payload,
            "/futures/v1/contracts",
        )

    def get_futures_market_status(
        self,
        *,
        product_code: str | None = None,
        limit: int = 100,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/futures/v1/market-status",
            params=self._optional_params(
                {
                    "product_code": product_code,
                    "limit": limit,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/futures/v1/market-status",
        )

    def get_futures_schedules(
        self,
        *,
        product_code: str | None = None,
        session_end_date: str | None = None,
        limit: int = 100,
        sort: str = "product_code.asc",
    ) -> MassiveRawResponse:
        payload = self._client.get(
            "/futures/v1/schedules",
            params=self._optional_params(
                {
                    "product_code": product_code,
                    "session_end_date": session_end_date,
                    "limit": limit,
                    "sort": sort,
                }
            ),
        )

        return self._remember_response(
            payload,
            "/futures/v1/schedules",
        )

    # ------------------------------------------------------------------
    # FOREX
    # ------------------------------------------------------------------

    def get_forex_snapshot(
        self,
        ticker: str,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            (
                "/v2/snapshot/locale/global/"
                f"markets/forex/tickers/{ticker.upper()}"
            )
        )

        return self._remember_response(
            payload,
            "/v2/snapshot/locale/global/"
            "markets/forex/tickers/{ticker}",
        )

    # ------------------------------------------------------------------
    # GENERIC RAW ACCESS
    # ------------------------------------------------------------------

    def get_raw(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> MassiveRawResponse:
        payload = self._client.get(
            path,
            params=params,
        )

        return self._remember_response(
            payload,
            path,
        )

    # ------------------------------------------------------------------
    # CANONICAL ENTRYPOINT
    # ------------------------------------------------------------------

    def get_market_snapshot(
        self,
        symbol: str,
        *,
        metadata: Mapping[str, Any] | None = None,
    ) -> MarketSnapshot:
        """
        Resolve the requested Massive market domain.

        metadata:
            market
            segment
            instrument_type
            underlying
            option_contract
            product_code
        """

        meta = dict(metadata or {})

        market = str(
            meta.get("market", "EQUITY")
        ).strip().upper()

        instrument_type = str(
            meta.get(
                "instrument_type",
                "EQUITY",
            )
        ).strip().upper()

        if market in {"CRYPTO", "BINANCE"}:
            raise ValueError(
                "MASSIVE_CRYPTO_NOT_SELECTED:"
                "Use Binance adapter for crypto."
            )

        if instrument_type in {
            "OPTION",
            "OPTIONS",
        }:
            underlying = str(
                meta.get("underlying", "")
            ).strip()

            if not underlying:
                raise ValueError(
                    "MASSIVE_OPTION_UNDERLYING_REQUIRED"
                )

            option_contract = str(
                meta.get(
                    "option_contract",
                    symbol,
                )
            ).strip()

            response = self.get_option_snapshot(
                underlying,
                option_contract,
            )

            return self._snapshot_from_option(
                response,
                option_contract,
            )

        if instrument_type in {
            "FUTURE",
            "FUTURES",
        }:
            response = self.get_futures_snapshot(
                ticker=symbol,
                product_code=meta.get(
                    "product_code"
                ),
                limit=1,
            )

            return self._snapshot_from_futures(
                response,
                symbol,
            )

        if instrument_type in {
            "FOREX",
            "FX",
        } or market == "FOREX":
            response = self.get_forex_snapshot(
                symbol
            )

            return self._snapshot_from_forex(
                response,
                symbol,
            )

        response = self.get_equity_snapshot(
            symbol
        )

        return self._snapshot_from_equity(
            response,
            symbol,
        )

    # ------------------------------------------------------------------
    # RAW RESPONSE STORAGE
    # ------------------------------------------------------------------

    def _remember_response(
        self,
        payload: Mapping[str, Any],
        endpoint: str,
    ) -> MassiveRawResponse:
        response = MassiveRawResponse(
            dict(payload),
            endpoint=endpoint,
        )

        self._last_response = response

        return response

    # ------------------------------------------------------------------
    # EQUITY SNAPSHOT -> CANONICAL
    # ------------------------------------------------------------------

    def _snapshot_from_equity(
        self,
        response: MassiveRawResponse,
        symbol: str,
    ) -> MarketSnapshot:
        payload = self._single_record(response)

        day = self._mapping(
            payload.get("day")
        )

        trade = self._mapping(
            payload.get("lastTrade")
            or payload.get("last_trade")
        )

        quote = self._mapping(
            payload.get("lastQuote")
            or payload.get("last_quote")
        )

        price = self._decimal_from(
            trade,
            "p",
            "price",
        )

        if price is None:
            price = self._decimal_from(
                payload,
                "price",
                "lastPrice",
            )

        observed_at = self._timestamp(
            self._first_value(
                trade,
                "t",
                "timestamp",
            )
            or self._first_value(
                quote,
                "t",
                "timestamp",
            )
            or self._first_value(
                day,
                "last_updated",
                "timestamp",
            )
        )

        received_at = datetime.now(
            timezone.utc
        )

        open_value = self._decimal_from(
            day,
            "o",
            "open",
        )
        high_value = self._decimal_from(
            day,
            "h",
            "high",
        )
        low_value = self._decimal_from(
            day,
            "l",
            "low",
        )
        close_value = self._decimal_from(
            day,
            "c",
            "close",
        )
        volume_value = self._decimal_from(
            day,
            "v",
            "volume",
        )

        bid_value = self._decimal_from(
            quote,
            "p",
            "bid",
            "bid_price",
        )

        ask_value = self._decimal_from(
            quote,
            "P",
            "ask",
            "ask_price",
        )

        bid_size_value = self._decimal_from(
            quote,
            "s",
            "bid_size",
        )

        ask_size_value = self._decimal_from(
            quote,
            "S",
            "ask_size",
        )

        trade_size_value = self._decimal_from(
            trade,
            "s",
            "size",
            "trade_size",
        )

        raw_conditions = self._first_value(
            trade,
            "c",
            "conditions",
            "trade_conditions",
        )

        if raw_conditions is None:
            trade_conditions_value = None
        elif isinstance(raw_conditions, (list, tuple)):
            trade_conditions_value = tuple(str(value) for value in raw_conditions)
        else:
            trade_conditions_value = (str(raw_conditions),)

        trade_exchange_value = self._first_value(
            trade,
            "x",
            "exchange",
            "trade_exchange",
        )

        if trade_exchange_value is not None:
            trade_exchange_value = str(trade_exchange_value)

        fields_present = tuple(
            name
            for name, value in (
                ("price", price),
                ("open", open_value),
                ("high", high_value),
                ("low", low_value),
                ("close", close_value),
                ("volume", volume_value),
                ("bid", bid_value),
                ("ask", ask_value),
                ("bid_size", bid_size_value),
                ("ask_size", ask_size_value),
                ("trade_size", trade_size_value),
                ("trade_conditions", trade_conditions_value),
                ("trade_exchange", trade_exchange_value),
            )
            if value is not None
        )

        observation = MarketObservation(
            observed_at=observed_at,
            price=price,
            open=open_value,
            high=high_value,
            low=low_value,
            close=close_value,
            volume=volume_value,
            bid=bid_value,
            ask=ask_value,
            bid_size=bid_size_value,
            ask_size=ask_size_value,
            trade_size=trade_size_value,
            trade_conditions=trade_conditions_value,
            trade_exchange=trade_exchange_value,
            observation_kind=ObservationKind.OBSERVED,
            fields_present=fields_present,
        )


        return self._build_snapshot(
            market="EQUITY",
            segment="SPOT",
            country="US",
            instrument_type="EQUITY",
            asset_class="EQUITY",
            symbol=symbol,
            venue=str(
                payload.get(
                    "primary_exchange",
                    "MASSIVE",
                )
            ),
            observation=observation,
            observed_at=observed_at,
            received_at=received_at,
            metadata={
                "provider": "MASSIVE",
                "provider_endpoint": response.endpoint,
                "change": self._first_value(
                    payload,
                    "todaysChange",
                    "change",
                ),
                "change_percent": self._first_value(
                    payload,
                    "todaysChangePerc",
                    "change_percent",
                ),
                "raw_payload": payload,
            },
        )

    # ------------------------------------------------------------------
    # OPTION SNAPSHOT -> CANONICAL
    # ------------------------------------------------------------------

    def _snapshot_from_option(
        self,
        response: MassiveRawResponse,
        option_contract: str,
    ) -> MarketSnapshot:
        payload = self._single_record(response)

        details = self._mapping(
            payload.get("details")
        )
        day = self._mapping(
            payload.get("day")
        )
        greeks = self._mapping(
            payload.get("greeks")
        )
        quote = self._mapping(
            payload.get("last_quote")
            or payload.get("lastQuote")
        )
        trade = self._mapping(
            payload.get("last_trade")
            or payload.get("lastTrade")
        )

        observed_at = self._timestamp(
            self._first_value(
                quote,
                "last_updated",
                "t",
                "timestamp",
            )
            or self._first_value(
                trade,
                "sip_timestamp",
                "t",
                "timestamp",
            )
        )

        received_at = datetime.now(
            timezone.utc
        )

        contract_type = str(
            details.get(
                "contract_type",
                "",
            )
        ).upper()

        if contract_type not in {
            "CALL",
            "PUT",
        }:
            contract_type = None

        expiry = self._date(
            details.get(
                "expiration_date"
            )
        )

        strike = self._decimal(
            details.get(
                "strike_price"
            )
        )

        contract = ContractIdentity(
            contract_id=str(
                details.get(
                    "ticker",
                    option_contract,
                )
            ),
            contract_type="OPTION",
            option_type=contract_type,
            expiry=expiry,
            strike=strike,
            contract_size=self._decimal(
                details.get(
                    "shares_per_contract"
                )
            ),
        )

        price = self._decimal_from(
            trade,
            "price",
            "p",
        )

        if price is None:
            price = self._decimal_from(
                quote,
                "midpoint",
                "price",
            )

        return self._build_snapshot(
            market="OPTIONS",
            segment="OPTIONS",
            country="US",
            instrument_type="OPTIONS",
            asset_class="OPTIONS",
            symbol=option_contract,
            venue="OPRA",
            contract=contract,
            observation=MarketObservation(
                observed_at=observed_at,
                price=price,
                open=self._decimal_from(
                    day,
                    "open",
                    "o",
                ),
                high=self._decimal_from(
                    day,
                    "high",
                    "h",
                ),
                low=self._decimal_from(
                    day,
                    "low",
                    "l",
                ),
                close=self._decimal_from(
                    day,
                    "close",
                    "c",
                ),
                volume=self._decimal_from(
                    day,
                    "volume",
                    "v",
                ),
                bid=self._decimal_from(
                    quote,
                    "bid",
                ),
                ask=self._decimal_from(
                    quote,
                    "ask",
                ),
                open_interest=self._decimal_from(
                    payload,
                    "open_interest",
                ),
                observation_kind=(
                    ObservationKind.OBSERVED
                ),
                fields_present=(
                    "price",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "bid",
                    "ask",
                    "open_interest",
                ),
            ),
            observed_at=observed_at,
            received_at=received_at,
            metadata={
                "provider": "MASSIVE",
                "provider_endpoint": response.endpoint,
                "underlying": details.get(
                    "underlying_ticker"
                ),
                "change": self._first_value(
                    day,
                    "change",
                ),
                "change_percent": self._first_value(
                    day,
                    "change_percent",
                ),
                "implied_volatility": payload.get(
                    "implied_volatility"
                ),
                "greeks": dict(greeks),
                "delta": greeks.get("delta"),
                "gamma": greeks.get("gamma"),
                "theta": greeks.get("theta"),
                "vega": greeks.get("vega"),
                "open_interest": payload.get(
                    "open_interest"
                ),
                "break_even_price": payload.get(
                    "break_even_price"
                ),
                "underlying_asset": payload.get(
                    "underlying_asset"
                ),
                "raw_payload": payload,
            },
        )

    # ------------------------------------------------------------------
    # FUTURES SNAPSHOT -> CANONICAL
    # ------------------------------------------------------------------

    def _snapshot_from_futures(
        self,
        response: MassiveRawResponse,
        symbol: str,
    ) -> MarketSnapshot:
        payload = self._single_record(response)

        trade = self._mapping(
            payload.get("last_trade")
            or payload.get("lastTrade")
        )

        quote = self._mapping(
            payload.get("last_quote")
            or payload.get("lastQuote")
        )

        session = self._mapping(
            payload.get("session")
        )

        observed_at = self._timestamp(
            self._first_value(
                trade,
                "timestamp",
                "t",
            )
            or self._first_value(
                quote,
                "timestamp",
                "t",
            )
            or self._first_value(
                session,
                "timestamp",
            )
        )

        received_at = datetime.now(
            timezone.utc
        )

        product_code = (
            payload.get("product_code")
            or payload.get("productCode")
        )

        contract_id = (
            payload.get("contract_id")
            or payload.get("ticker")
            or symbol
        )

        contract = ContractIdentity(
            contract_id=str(contract_id),
            contract_type="FUTURES",
            product_code=(
                str(product_code)
                if product_code is not None
                else None
            ),
            expiry=self._date(
                payload.get(
                    "expiration_date"
                )
            ),
            tick_size=self._decimal(
                payload.get(
                    "tick_size"
                )
            ),
            contract_size=self._decimal(
                payload.get(
                    "contract_size"
                )
            ),
            currency=(
                str(
                    payload.get(
                        "currency"
                    )
                )
                if payload.get("currency")
                else None
            ),
        )

        price = self._decimal_from(
            trade,
            "price",
            "p",
        )

        if price is None:
            price = self._decimal_from(
                payload,
                "price",
                "last_price",
            )

        return self._build_snapshot(
            market="FUTURES",
            segment="FUTURES",
            country="US",
            instrument_type="FUTURES",
            asset_class="FUTURES",
            symbol=symbol,
            venue=str(
                payload.get(
                    "trading_venue",
                    "MASSIVE",
                )
            ),
            contract=contract,
            observation=MarketObservation(
                observed_at=observed_at,
                price=price,
                open=self._decimal_from(
                    session,
                    "open",
                    "o",
                ),
                high=self._decimal_from(
                    session,
                    "high",
                    "h",
                ),
                low=self._decimal_from(
                    session,
                    "low",
                    "l",
                ),
                close=self._decimal_from(
                    session,
                    "close",
                    "c",
                ),
                volume=self._decimal_from(
                    session,
                    "volume",
                    "v",
                ),
                bid=self._decimal_from(
                    quote,
                    "bid_price",
                    "bid",
                ),
                ask=self._decimal_from(
                    quote,
                    "ask_price",
                    "ask",
                ),
                observation_kind=(
                    ObservationKind.OBSERVED
                ),
                fields_present=(
                    "price",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "bid",
                    "ask",
                ),
            ),
            observed_at=observed_at,
            received_at=received_at,
            metadata={
                "provider": "MASSIVE",
                "provider_endpoint": response.endpoint,
                "product_code": product_code,
                "settlement_price": payload.get(
                    "settlement_price"
                ),
                "change": payload.get(
                    "change"
                ),
                "change_percent": payload.get(
                    "change_percent"
                ),
                "open_interest": payload.get(
                    "open_interest"
                ),
                "raw_payload": payload,
            },
        )

    # ------------------------------------------------------------------
    # FOREX SNAPSHOT -> CANONICAL
    # ------------------------------------------------------------------

    def _snapshot_from_forex(
        self,
        response: MassiveRawResponse,
        symbol: str,
    ) -> MarketSnapshot:
        payload = self._single_record(response)

        day = self._mapping(
            payload.get("day")
        )

        last_trade = self._mapping(
            payload.get("lastTrade")
            or payload.get("last_trade")
        )

        last_quote = self._mapping(
            payload.get("lastQuote")
            or payload.get("last_quote")
        )

        price = self._decimal_from(
            last_trade,
            "p",
            "price",
        )

        if price is None:
            price = self._decimal_from(
                last_quote,
                "p",
                "midpoint",
            )

        observed_at = self._timestamp(
            self._first_value(
                last_trade,
                "t",
                "timestamp",
            )
            or self._first_value(
                last_quote,
                "t",
                "timestamp",
            )
        )

        received_at = datetime.now(
            timezone.utc
        )

        return self._build_snapshot(
            market="FOREX",
            segment="SPOT",
            country="GLOBAL",
            instrument_type="FOREX",
            asset_class="FOREX",
            symbol=symbol,
            venue="MASSIVE",
            observation=MarketObservation(
                observed_at=observed_at,
                price=price,
                open=self._decimal_from(
                    day,
                    "o",
                    "open",
                ),
                high=self._decimal_from(
                    day,
                    "h",
                    "high",
                ),
                low=self._decimal_from(
                    day,
                    "l",
                    "low",
                ),
                close=self._decimal_from(
                    day,
                    "c",
                    "close",
                ),
                volume=self._decimal_from(
                    day,
                    "v",
                    "volume",
                ),
                bid=self._decimal_from(
                    last_quote,
                    "p",
                    "bid",
                ),
                ask=self._decimal_from(
                    last_quote,
                    "P",
                    "ask",
                ),
                observation_kind=(
                    ObservationKind.OBSERVED
                ),
                fields_present=(
                    "price",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "bid",
                    "ask",
                ),
            ),
            observed_at=observed_at,
            received_at=received_at,
            metadata={
                "provider": "MASSIVE",
                "provider_endpoint": response.endpoint,
                "change": payload.get(
                    "todaysChange"
                ),
                "change_percent": payload.get(
                    "todaysChangePerc"
                ),
                "raw_payload": payload,
            },
        )

    # ------------------------------------------------------------------
    # SNAPSHOT BUILDER
    # ------------------------------------------------------------------

    def _build_snapshot(
        self,
        *,
        market: str,
        segment: str,
        country: str,
        instrument_type: str,
        asset_class: str,
        symbol: str,
        venue: str,
        observation: MarketObservation,
        observed_at: datetime,
        received_at: datetime,
        contract: ContractIdentity | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> MarketSnapshot:
        latency_ms = max(
            0.0,
            (
                received_at - observed_at
            ).total_seconds()
            * 1000.0,
        )

        return MarketSnapshot(
            market=MarketIdentity(
                market=market,
                segment=segment,
                country=country,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
                instrument_id=symbol.upper(),
                asset_class=asset_class,
            ),
            venue=VenueIdentity(
                venue=venue.upper(),
                venue_id=venue.upper(),
            ),
            contract=contract,
            observation=observation,
            timing=MarketTiming(
                source_timestamp=observed_at,
                received_timestamp=received_at,
                observed_at=observed_at,
            ),
            data_quality=MarketDataQuality(
                source="massive",
                source_timestamp=observed_at,
                received_timestamp=received_at,
                latency_ms=latency_ms,
                is_complete=True,
                is_stale=False,
            ),
            state=MarketState(
                session=MarketSessionState.UNKNOWN,
                halted=False,
                tradable=True,
            ),
            metadata=dict(metadata or {}),
        )

    # ------------------------------------------------------------------
    # GENERIC HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _optional_params(
        values: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            key: value
            for key, value in values.items()
            if value is not None
        }

    @staticmethod
    def _mapping(
        value: Any,
    ) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)

        return {}

    @staticmethod
    def _first_value(
        payload: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in payload:
                value = payload[key]

                if value is not None:
                    return value

        return None

    @classmethod
    def _decimal_from(
        cls,
        payload: Mapping[str, Any],
        *keys: str,
    ) -> Decimal | None:
        return cls._decimal(
            cls._first_value(
                payload,
                *keys,
            )
        )

    @staticmethod
    def _decimal(
        value: Any,
    ) -> Decimal | None:
        if value is None or value == "":
            return None

        try:
            result = Decimal(
                str(value)
            )
        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ):
            return None

        if not result.is_finite():
            return None

        return result

    @staticmethod
    def _timestamp(
        value: Any,
    ) -> datetime:
        if value is None:
            return datetime.now(
                timezone.utc
            )

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(
                    tzinfo=timezone.utc
                )

            return value.astimezone(
                timezone.utc
            )

        if isinstance(value, (int, float)):
            numeric = float(value)

            # Massive uses nanoseconds for many
            # market-data timestamps.
            if numeric > 1e16:
                seconds = numeric / 1_000_000_000
            elif numeric > 1e13:
                seconds = numeric / 1_000_000
            elif numeric > 1e10:
                seconds = numeric / 1_000
            else:
                seconds = numeric

            try:
                return datetime.fromtimestamp(
                    seconds,
                    tz=timezone.utc,
                )
            except (
                OverflowError,
                OSError,
                ValueError,
            ):
                return datetime.now(
                    timezone.utc
                )

        text = str(value).strip()

        if not text:
            return datetime.now(
                timezone.utc
            )

        try:
            parsed = datetime.fromisoformat(
                text.replace(
                    "Z",
                    "+00:00",
                )
            )

            if parsed.tzinfo is None:
                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed.astimezone(
                timezone.utc
            )

        except ValueError:
            return datetime.now(
                timezone.utc
            )

    @staticmethod
    def _date(
        value: Any,
    ) -> date | None:
        if value is None:
            return None

        if isinstance(value, date):
            return value

        text = str(value).strip()

        if not text:
            return None

        try:
            return date.fromisoformat(
                text[:10]
            )
        except ValueError:
            return None

    @staticmethod
    def _single_record(
        response: MassiveRawResponse,
    ) -> dict[str, Any]:
        """
        Normalize only the outer response shape.

        Provider-native fields inside the record are preserved.
        """

        results = response.results

        if results:
            first = results[0]

            if isinstance(first, Mapping):
                return dict(first)

        payload = response.raw()

        # Single-object endpoints may return the object directly
        # under results or at the response root.
        return payload
