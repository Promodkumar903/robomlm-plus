from __future__ import annotations

from typing import Any, Mapping

from app.adapters.bybit.bybit_client import BybitClient


class BybitOrders:
    """
    ROBOMLM Bybit Order Adapter.

    Responsibility:
        - Submit provider orders
        - Cancel provider orders
        - Query provider order status

    No intelligence.
    No signals.
    No opportunity ranking.
    No CAS decisions.
    """

    def __init__(
        self,
        client: BybitClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Bybit"

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        **kwargs: Any,
    ) -> Mapping[str, Any]:

        return {
            "provider": "bybit",
            "symbol": symbol.upper(),
            "side": side.upper(),
            "quantity": quantity,
            "order_type": order_type.upper(),
            "status": "NOT_IMPLEMENTED",
            "details": dict(kwargs),
        }

    def cancel_order(
        self,
        symbol: str,
        order_id: str,
    ) -> Mapping[str, Any]:

        return {
            "provider": "bybit",
            "symbol": symbol.upper(),
            "order_id": order_id,
            "status": "NOT_IMPLEMENTED",
        }

    def get_order_status(
        self,
        symbol: str,
        order_id: str,
    ) -> Mapping[str, Any]:

        return {
            "provider": "bybit",
            "symbol": symbol.upper(),
            "order_id": order_id,
            "status": "UNKNOWN",
        }