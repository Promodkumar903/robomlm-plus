from __future__ import annotations

import json
import os
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class MassiveClient:
    """
    Massive REST API client.

    Responsibilities:
        - API authentication
        - HTTP GET transport
        - JSON decoding
        - timeout handling
        - structured API errors
        - connection state

    This client does NOT:
        - normalize market data
        - create MarketSnapshot
        - calculate intelligence
        - calculate indicators
        - make trading decisions
    """

    DEFAULT_BASE_URL = "https://api.massive.com"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self._api_key = (
            api_key
            or os.getenv("MASSIVE_API_KEY")
            or os.getenv("POLYGON_API_KEY")
        )

        self._base_url = (
            base_url
            or os.getenv(
                "MASSIVE_BASE_URL",
                self.DEFAULT_BASE_URL,
            )
        ).rstrip("/")

        self._timeout = (
            timeout
            if timeout is not None
            else float(
                os.getenv(
                    "MASSIVE_API_TIMEOUT",
                    str(self.DEFAULT_TIMEOUT),
                )
            )
        )

        self._connected = False

    @property
    def provider_name(self) -> str:
        return "Massive"

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def timeout(self) -> float:
        return self._timeout

    def _require_api_key(self) -> str:
        if not self._api_key:
            raise RuntimeError(
                "MASSIVE_API_KEY_NOT_CONFIGURED"
            )

        return self._api_key

    def _build_url(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
    ) -> str:
        normalized_path = path.strip()

        if not normalized_path.startswith("/"):
            normalized_path = "/" + normalized_path

        query: dict[str, Any] = {}

        if params:
            for key, value in params.items():
                if value is None:
                    continue

                query[key] = value

        # Massive officially supports apiKey query authentication.
        # Keep authentication inside this transport boundary.
        query["apiKey"] = self._require_api_key()

        encoded_query = urlencode(
            query,
            doseq=True,
        )

        return (
            f"{self._base_url}"
            f"{normalized_path}"
            f"?{encoded_query}"
        )

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a GET request against Massive REST API.

        Returns:
            Decoded JSON object.

        Raises:
            RuntimeError:
                Configuration, transport, HTTP or JSON errors.
        """

        url = self._build_url(
            path,
            params,
        )

        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json",
                "User-Agent": (
                    "ROBOMLM_PLUS/1.0 "
                    "MassiveMarketDataAdapter"
                ),
            },
        )

        try:
            with urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                status_code = response.status
                raw_body = response.read()

        except HTTPError as exc:
            body = self._read_error_body(exc)

            raise RuntimeError(
                "MASSIVE_HTTP_ERROR:"
                f"{exc.code}:"
                f"{body}"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                "MASSIVE_CONNECTION_ERROR:"
                f"{exc.reason}"
            ) from exc

        except TimeoutError as exc:
            raise RuntimeError(
                "MASSIVE_TIMEOUT"
            ) from exc

        if not raw_body:
            raise RuntimeError(
                "MASSIVE_EMPTY_RESPONSE:"
                f"{status_code}"
            )

        try:
            payload = json.loads(
                raw_body.decode("utf-8")
            )
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            raise RuntimeError(
                "MASSIVE_INVALID_JSON_RESPONSE"
            ) from exc

        if not isinstance(payload, dict):
            raise RuntimeError(
                "MASSIVE_RESPONSE_NOT_OBJECT"
            )

        self._connected = True

        self._validate_api_response(
            payload,
            status_code,
        )

        return payload

    @staticmethod
    def _read_error_body(
        error: HTTPError,
    ) -> str:
        try:
            raw = error.read()

            if not raw:
                return error.reason or "unknown"

            text = raw.decode(
                "utf-8",
                errors="replace",
            ).strip()

            if not text:
                return error.reason or "unknown"

            return text[:2000]

        except Exception:
            return str(
                error.reason
                or "unknown"
            )

    @staticmethod
    def _validate_api_response(
        payload: Mapping[str, Any],
        status_code: int,
    ) -> None:
        if status_code < 200 or status_code >= 300:
            raise RuntimeError(
                "MASSIVE_HTTP_STATUS:"
                f"{status_code}"
            )

        status = payload.get("status")

        if isinstance(status, str):
            normalized = status.strip().upper()

            if normalized in {
                "ERROR",
                "FAILED",
                "FAILURE",
            }:
                message = (
                    payload.get("error")
                    or payload.get("message")
                    or payload.get("status")
                )

                raise RuntimeError(
                    "MASSIVE_API_ERROR:"
                    f"{message}"
                )

    def ping(self) -> dict[str, Any]:
        """
        Verify authenticated access using a lightweight
        Massive market-status endpoint.
        """

        result = self.get(
            "/v1/marketstatus/now"
        )

        self._connected = True

        return result

    def connect(self) -> None:
        """
        Establish/verify the provider connection.

        No persistent socket is created here because this
        adapter currently uses REST.
        """

        self.ping()
        self._connected = True

    def close(self) -> None:
        """
        Close the logical REST connection.
        """

        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_market_status(
        self,
    ) -> dict[str, Any]:
        return self.get(
            "/v1/marketstatus/now"
        )

    def get_reference_tickers(
        self,
        *,
        market: str | None = None,
        active: bool | None = None,
        order: str | None = None,
        limit: int | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}

        if market is not None:
            params["market"] = market

        if active is not None:
            params["active"] = (
                "true"
                if active
                else "false"
            )

        if order is not None:
            params["order"] = order

        if limit is not None:
            params["limit"] = limit

        if sort is not None:
            params["sort"] = sort

        return self.get(
            "/v3/reference/tickers",
            params=params,
        )

    def get_reference_exchanges(
        self,
        *,
        asset_class: str | None = None,
        locale: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}

        if asset_class is not None:
            params["asset_class"] = asset_class

        if locale is not None:
            params["locale"] = locale

        return self.get(
            "/v3/reference/exchanges",
            params=params,
        )

    def __enter__(self) -> "MassiveClient":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()


__all__ = ["MassiveClient"]