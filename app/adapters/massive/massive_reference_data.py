from __future__ import annotations

from typing import Any


class MassiveReferenceData:
    """
    Massive Reference Data Adapter.

    Raw provider access only.

    No normalization.
    No intelligence.
    No calculations.
    """

    def __init__(
        self,
        client: Any,
    ) -> None:
        self._client = client

    @property
    def client(self) -> Any:
        return self._client

    def get_tickers(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get_reference_tickers(
            **params
        )

    def get_exchanges(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get_reference_exchanges(
            **params
        )

    def get_conditions(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/conditions",
            params=params,
        )

    def get_markets(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/markets",
            params=params,
        )

    def get_locales(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/locales",
            params=params,
        )

    def get_ticker_types(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/tickers/types",
            params=params,
        )

    def get_stock_splits(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/splits",
            params=params,
        )

    def get_dividends(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/v3/reference/dividends",
            params=params,
        )

    def get_ticker_details(
        self,
        ticker: str,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            f"/v3/reference/tickers/{ticker}",
            params=params,
        )

    def get_financials(
        self,
        **params: Any,
    ) -> dict[str, Any]:
        return self._client.get(
            "/vX/reference/financials",
            params=params,
        )