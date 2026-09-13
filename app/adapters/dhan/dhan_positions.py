from __future__ import annotations

from typing import Any

from app.adapters.dhan.dhan_client import DhanClient


class DhanPositions:
    """
    ROBOMLM Dhan position adapter.

    Responsibility:
        - Retrieve provider positions
        - Retrieve provider holdings
        - Provider-side position conversion/exit boundary

    No portfolio intelligence.
    No risk decision.
    No trade recommendation.
    """

    def __init__(
        self,
        client: DhanClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Dhan"

    def get_positions(self) -> Any:
        """
        Retrieve all open Dhan positions.
        """
        return self._client.get("/positions")

    def get_holdings(self) -> Any:
        """
        Retrieve Dhan holdings.
        """
        return self._client.get("/holdings")

    def convert_position(
        self,
        *,
        security_id: str | int,
        exchange_segment: str,
        transaction_type: str,
        product_type: str,
        quantity: int,
    ) -> Any:
        """
        Convert an existing Dhan position between
        supported product types.
        """
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        payload = {
            "dhanClientId": self._client.client_id,
            "securityId": str(security_id),
            "exchangeSegment": exchange_segment,
            "transactionType": transaction_type.upper(),
            "convertQty": str(quantity),
            "toProductType": product_type,
        }

        return self._client.post(
            "/positions/convert",
            payload=payload,
        )

    def exit_all_positions(self) -> Any:
        """
        Provider-side exit-all endpoint.

        This is intentionally exposed only as a low-level
        provider operation. Higher-level ROBOMLM execution
        authority must decide whether it is permitted.
        """
        return self._client.delete(
            "/positions"
        )