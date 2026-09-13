from __future__ import annotations

from typing import Any, Mapping

from app.adapters.binance.binance_client import BinanceClient


class BinanceOrders:
    """
    ROBOMLM Binance Order Adapter.

    Responsibility:
        - Provider order submission
        - Provider order cancellation
        - Provider order status retrieval

    MUST NOT:
        - Decide whether to trade
        - Generate signals
        - Generate opportunities
        - Generate risk decisions
        - Generate CAS decisions
    """

    def __init__(
        self,
        client: BinanceClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Binance"

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        **kwargs: Any,
    ) -> Mapping[str, Any]:
        """
        Order-routing boundary.

        Real authenticated Binance execution
        can be wired later.

        Current implementation preserves
        provider contract structure only.
        """
        return {
            "provider": "binance",
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
            "provider": "binance",
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
            "provider": "binance",
            "symbol": symbol.upper(),
            "order_id": order_id,
            "status": "UNKNOWN",
        }