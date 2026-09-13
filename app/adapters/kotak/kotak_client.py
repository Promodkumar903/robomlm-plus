from __future__ import annotations

from typing import Any, Mapping

import requests


class KotakAPIError(RuntimeError):
    """Raised when Kotak Neo returns an API-level error."""


class KotakClient:
    """
    ROBOMLM Kotak Neo provider client.

    Responsibility:
        - Manage Kotak Neo API session
        - Maintain authentication headers
        - Execute provider HTTP requests
        - Return provider-native responses

    This class MUST NOT perform:
        - market intelligence
        - signals
        - opportunity ranking
        - BUY / SELL decisions
        - risk decisions
        - CAS decisions
    """

    FIXED_BASE_URL = "https://mis.kotaksecurities.com"

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str | None = None,
        client_id: str | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        if not access_token:
            raise ValueError(
                "Kotak Neo access_token is required"
            )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be positive"
            )

        self._access_token = access_token
        self._client_id = client_id
        self._base_url = (
            base_url.rstrip("/")
            if base_url
            else self.FIXED_BASE_URL
        )
        self._timeout_seconds = timeout_seconds
        self._session: requests.Session | None = None

    @property
    def provider_name(self) -> str:
        return "Kotak Neo"

    @property
    def base_url(self) -> str:
        return self._base_url

    def connect(self) -> None:
        """
        Create reusable HTTP session.
        """
        if self._session is not None:
            return

        session = requests.Session()

        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": self._access_token,
            }
        )

        if self._client_id:
            session.headers.update(
                {
                    "neo-fin-key": self._client_id,
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
        return self._session is not None

    def _ensure_connected(self) -> requests.Session:
        if self._session is None:
            self.connect()

        if self._session is None:
            raise RuntimeError(
                "Unable to initialize Kotak Neo session"
            )

        return self._session

    @staticmethod
    def _decode_response(
        response: requests.Response,
    ) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise KotakAPIError(
                "Kotak Neo returned a non-JSON response: "
                f"HTTP {response.status_code}"
            ) from exc

    @staticmethod
    def _raise_for_error(
        response: requests.Response,
        data: Any,
    ) -> None:
        if response.ok:
            return

        if isinstance(data, Mapping):
            message = (
                data.get("message")
                or data.get("error")
                or data.get("errorMessage")
                or str(data)
            )
        else:
            message = str(data)

        raise KotakAPIError(
            f"Kotak Neo HTTP {response.status_code}: "
            f"{message}"
        )

    def get(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """
        Execute provider GET request.
        """
        session = self._ensure_connected()

        response = session.get(
            f"{self._base_url}{endpoint}",
            params=params,
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_error(response, data)

        return data

    def post(
        self,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """
        Execute provider POST request.
        """
        session = self._ensure_connected()

        response = session.post(
            f"{self._base_url}{endpoint}",
            json=dict(payload or {}),
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_error(response, data)

        return data

    def put(
        self,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """
        Execute provider PUT request.
        """
        session = self._ensure_connected()

        response = session.put(
            f"{self._base_url}{endpoint}",
            json=dict(payload or {}),
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_error(response, data)

        return data

    def delete(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """
        Execute provider DELETE request.
        """
        session = self._ensure_connected()

        response = session.delete(
            f"{self._base_url}{endpoint}",
            params=params,
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_error(response, data)

        return data

    def get_quotes(
        self,
        *,
        endpoint: str,
        payload: Mapping[str, Any],
    ) -> Any:
        """
        Provider quote boundary.

        The exact post-login quote endpoint is supplied by
        the current Kotak Neo baseUrl/API configuration.
        """
        return self.post(
            endpoint,
            payload=payload,
        )