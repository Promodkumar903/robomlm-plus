from __future__ import annotations

from typing import Any, Mapping

from app.adapters.dhan.dhan_client import DhanClient


class DhanOrders:
    """
    ROBOMLM Dhan order adapter.

    This class is only an execution/provider boundary.

    It does NOT decide:
        - whether an instrument should be traded
        - BUY vs SELL recommendation
        - position sizing
        - risk
        - opportunity quality
        - CAS authority
    """

    def __init__(
        self,
        client: DhanClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Dhan"

    def place_order(
        self,
        *,
        transaction_type: str,
        exchange_segment: str,
        product_type: str,
        order_type: str,
        validity: str,
        security_id: str | int,
        quantity: int,
        correlation_id: str | None = None,
        disclosed_quantity: int | None = None,
        price: float | None = None,
        trigger_price: float | None = None,
        after_market_order: bool = False,
        amo_time: str | None = None,
        bo_profit_value: float | None = None,
        bo_stop_loss_value: float | None = None,
    ) -> Mapping[str, Any]:
        """
        Submit an actual Dhan order.

        The caller is responsible for upstream authorization,
        risk checks and execution gating.
        """
        if transaction_type.upper() not in {"BUY", "SELL"}:
            raise ValueError(
                "transaction_type must be BUY or SELL"
            )

        if quantity <= 0:
            raise ValueError("quantity must be positive")

        payload: dict[str, Any] = {
            "dhanClientId": self._client_id(),
            "transactionType": transaction_type.upper(),
            "exchangeSegment": exchange_segment,
            "productType": product_type,
            "orderType": order_type,
            "validity": validity,
            "securityId": str(security_id),
            "quantity": str(quantity),
            "disclosedQuantity": (
                str(disclosed_quantity)
                if disclosed_quantity is not None
                else ""
            ),
            "price": (
                str(price)
                if price is not None
                else ""
            ),
            "triggerPrice": (
                str(trigger_price)
                if trigger_price is not None
                else ""
            ),
            "afterMarketOrder": after_market_order,
            "amoTime": amo_time or "",
            "boProfitValue": (
                str(bo_profit_value)
                if bo_profit_value is not None
                else ""
            ),
            "boStopLossValue": (
                str(bo_stop_loss_value)
                if bo_stop_loss_value is not None
                else ""
            ),
        }

        if correlation_id:
            payload["correlationId"] = correlation_id

        return self._client.post(
            "/orders",
            payload=payload,
        )

    def get_order_status(
        self,
        order_id: str,
    ) -> Mapping[str, Any]:
        return self._client.get(
            f"/orders/{order_id}"
        )

    def get_orders(self) -> Any:
        return self._client.get("/orders")

    def get_order_by_correlation_id(
        self,
        correlation_id: str,
    ) -> Mapping[str, Any]:
        return self._client.get(
            f"/orders/external/{correlation_id}"
        )

    def cancel_order(
        self,
        order_id: str,
    ) -> Mapping[str, Any]:
        return self._client.delete(
            f"/orders/{order_id}"
        )

    def modify_order(
        self,
        *,
        order_id: str,
        order_type: str,
        quantity: int,
        validity: str,
        price: float | None = None,
        disclosed_quantity: int | None = None,
        trigger_price: float | None = None,
        leg_name: str | None = None,
    ) -> Mapping[str, Any]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        payload: dict[str, Any] = {
            "dhanClientId": self._client_id(),
            "orderId": str(order_id),
            "orderType": order_type,
            "quantity": str(quantity),
            "validity": validity,
            "price": (
                str(price)
                if price is not None
                else ""
            ),
            "disclosedQuantity": (
                str(disclosed_quantity)
                if disclosed_quantity is not None
                else ""
            ),
            "triggerPrice": (
                str(trigger_price)
                if trigger_price is not None
                else ""
            ),
        }

        if leg_name:
            payload["legName"] = leg_name

        return self._client.put(
            f"/orders/{order_id}",
            payload=payload,
        )

    def _client_id(self) -> str:
        return self._client.client_id