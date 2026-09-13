from __future__ import annotations

from typing import Any, Mapping

import requests


class DhanAPIError(RuntimeError):
    """Raised when Dhan returns an API-level error."""


class DhanClient:
    """
    ROBOMLM DhanHQ REST client.

    Responsibility:
        - Dhan authentication headers
        - HTTP connectivity
        - Raw Dhan API requests
        - Provider-native response handling

    This layer contains NO:
        - intelligence
        - signal generation
        - opportunity ranking
        - BUY/SELL recommendation
        - risk decision
        - CAS decision
    """

    BASE_URL = "https://api.dhan.co/v2"

    def __init__(
        self,
        client_id: str,
        access_token: str,
        *,
        timeout_seconds: int = 10,
    ) -> None:
        if not client_id:
            raise ValueError("Dhan client_id is required")

        if not access_token:
            raise ValueError("Dhan access_token is required")

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._client_id = client_id
        self._access_token = access_token
        self._timeout_seconds = timeout_seconds
        self._session: requests.Session | None = None

    @property
    def provider_name(self) -> str:
        return "Dhan"

    @property
    def client_id(self) -> str:
        return self._client_id

    def connect(self) -> None:
        """Create the reusable HTTP session."""
        if self._session is not None:
            return

        session = requests.Session()

        session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "access-token": self._access_token,
                "client-id": self._client_id,
            }
        )

        self._session = session

    def close(self) -> None:
        """Close the HTTP session."""
        if self._session is not None:
            self._session.close()

        self._session = None

    def is_connected(self) -> bool:
        """Return only local connection/session state."""
        return self._session is not None

    def _ensure_connected(self) -> requests.Session:
        if self._session is None:
            self.connect()

        if self._session is None:
            raise RuntimeError("Unable to initialize Dhan HTTP session")

        return self._session

    @staticmethod
    def _decode_response(response: requests.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise DhanAPIError(
                f"Dhan returned non-JSON response: "
                f"HTTP {response.status_code}"
            ) from exc

    @classmethod
    def _raise_for_api_error(
        cls,
        response: requests.Response,
        data: Any,
    ) -> None:
        if response.ok:
            if isinstance(data, Mapping):
                error_code = data.get("errorCode")
                error_type = data.get("errorType")

                if error_code or error_type:
                    raise DhanAPIError(
                        f"Dhan API error: "
                        f"{error_code or error_type}: "
                        f"{data.get('errorMessage', data)}"
                    )

                status = data.get("status")

                if isinstance(status, str) and status.lower() == "failure":
                    raise DhanAPIError(
                        f"Dhan request failed: {data}"
                    )

            return

        if isinstance(data, Mapping):
            message = data.get(
                "errorMessage",
                data.get("message", str(data)),
            )
        else:
            message = str(data)

        raise DhanAPIError(
            f"Dhan HTTP {response.status_code}: {message}"
        )

    def get(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Execute a Dhan GET request."""
        session = self._ensure_connected()

        response = session.get(
            f"{self.BASE_URL}{endpoint}",
            params=params,
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_api_error(response, data)

        return data

    def post(
        self,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """Execute a Dhan POST request."""
        session = self._ensure_connected()

        response = session.post(
            f"{self.BASE_URL}{endpoint}",
            json=dict(payload or {}),
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_api_error(response, data)

        return data

    def put(
        self,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """Execute a Dhan PUT request."""
        session = self._ensure_connected()

        response = session.put(
            f"{self.BASE_URL}{endpoint}",
            json=dict(payload or {}),
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_api_error(response, data)

        return data

    def delete(
        self,
        endpoint: str,
        *,
        payload: Mapping[str, Any] | None = None,
    ) -> Any:
        """Execute a Dhan DELETE request."""
        session = self._ensure_connected()

        response = session.delete(
            f"{self.BASE_URL}{endpoint}",
            json=dict(payload or {}),
            timeout=self._timeout_seconds,
        )

        data = self._decode_response(response)
        self._raise_for_api_error(response, data)

        return data

    def get_profile(self) -> Any:
        """Retrieve Dhan account/profile information."""
        return self.get("/profile")

    def get_fund_limits(self) -> Any:
        """Retrieve Dhan fund/margin information."""
        return self.get("/fundlimit")

    def get_orders(self) -> Any:
        """Retrieve today's order book."""
        return self.get("/orders")

    def get_positions(self) -> Any:
        """Retrieve open positions."""
        return self.get("/positions")