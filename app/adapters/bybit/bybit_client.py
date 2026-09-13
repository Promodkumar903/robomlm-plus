from __future__ import annotations

from typing import Any, Mapping, Optional

import requests


class BybitClient:
    """
    ROBOMLM Bybit Provider Client.

    Responsibility:
        - Manage Bybit connectivity
        - Execute provider requests
        - Return provider-native responses

    No intelligence.
    No signals.
    No opportunity generation.
    """

    BASE_URL = "https://api.bybit.com"

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
        return "Bybit"

    def connect(self) -> None:
        if self._session is not None:
            return

        session = requests.Session()

        if self._api_key:
            session.headers.update(
                {
                    "X-BAPI-API-KEY": self._api_key,
                }
            )

        self._session = session

    def close(self) -> None:
        if self._session is not None:
            self._session.close()

        self._session = None

    def is_connected(self) -> bool:
        return self._session is not None

    def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:

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

    def ping(self) -> bool:
        response = self.get("/v5/market/time")
        return response is not None

    def get_server_time(self) -> dict[str, Any]:
        return self.get("/v5/market/time")