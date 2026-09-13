from __future__ import annotations

from typing import Any, Mapping, Optional

import requests


class BinanceClient:
    """
    ROBOMLM Binance Provider Client.

    Responsibility:
        - Manage Binance connectivity
        - Execute authenticated requests
        - Return provider-native responses

    MUST NOT:
        - Generate signals
        - Generate decisions
        - Generate opportunities
        - Perform intelligence calculations
    """

    BASE_URL = "https://api.binance.com"

    def __init__(
        self,
        api_key: str | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._session: Optional[requests.Session] = None

    @property
    def provider_name(self) -> str:
        return "Binance"

    def connect(self) -> None:
        """
        Create reusable HTTP session.
        """
        if self._session is not None:
            return

        session = requests.Session()

        if self._api_key:
            session.headers.update(
                {
                    "X-MBX-APIKEY": self._api_key,
                }
            )

        self._session = session

    def close(self) -> None:
        """
        Release HTTP resources.
        """
        if self._session is not None:
            self._session.close()

        self._session = None

    def is_connected(self) -> bool:
        """
        Session state only.
        """
        return self._session is not None

    def ping(self) -> bool:
        """
        Connectivity validation.
        """
        response = self.get("/api/v3/ping")
        return response is not None

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute GET request against Binance.
        """
        if self._session is None:
            self.connect()

        assert self._session is not None

        response = self._session.get(
            f"{self.BASE_URL}{endpoint}",
            params=params,
            timeout=self._timeout_seconds,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            return {"data": data}

        return data

    def get_server_time(self) -> dict[str, Any]:
        """
        Provider-native server time.
        """
        return self.get("/api/v3/time")

    def get_exchange_info(self) -> dict[str, Any]:
        """
        Provider-native exchange metadata.
        """
        return self.get("/api/v3/exchangeInfo")
