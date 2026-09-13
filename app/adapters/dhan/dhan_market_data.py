from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping

from app.adapters.dhan.dhan_client import DhanClient
from schemas.market.market_snapshot import (
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    VenueIdentity,
)


class DhanMarketData:
    """
    ROBOMLM Dhan market-data adapter.

    Flow:

        Dhan raw API
            -> provider response
            -> normalization
            -> canonical MarketSnapshot

    No intelligence is produced here.
    """

    def __init__(
        self,
        client: DhanClient,
    ) -> None:
        self._client = client

    @property
    def provider_name(self) -> str:
        return "Dhan"

    def get_ltp(
        self,
        exchange_segment: str,
        security_id: str | int,
    ) -> Mapping[str, Any]:
        """
        Retrieve raw Dhan LTP response.
        """
        payload = {
            exchange_segment: [int(security_id)],
        }

        response = self._client.post(
            "/marketfeed/ltp",
            payload=payload,
        )

        return response

    def get_ohlc(
        self,
        exchange_segment: str,
        security_id: str | int,
    ) -> Mapping[str, Any]:
        """
        Retrieve raw Dhan OHLC response.
        """
        payload = {
            exchange_segment: [int(security_id)],
        }

        response = self._client.post(
            "/marketfeed/ohlc",
            payload=payload,
        )

        return response

    def get_quote(
        self,
        exchange_segment: str,
        security_id: str | int,
    ) -> Mapping[str, Any]:
        """
        Retrieve raw Dhan quote/depth response.
        """
        payload = {
            exchange_segment: [int(security_id)],
        }

        response = self._client.post(
            "/marketfeed/quote",
            payload=payload,
        )

        return response

    @staticmethod
    def _extract_instrument_data(
        response: Mapping[str, Any],
        exchange_segment: str,
        security_id: str | int,
    ) -> Mapping[str, Any]:
        data = response.get("data", {})

        if not isinstance(data, Mapping):
            raise ValueError("Invalid Dhan market-data response")

        segment_data = data.get(exchange_segment)

        if not isinstance(segment_data, Mapping):
            raise ValueError(
                f"Dhan segment not present: {exchange_segment}"
            )

        instrument = segment_data.get(str(security_id))

        if not isinstance(instrument, Mapping):
            raise ValueError(
                f"Dhan security not present: "
                f"{exchange_segment}:{security_id}"
            )

        return instrument

    @staticmethod
    def _decimal(
        value: Any,
    ) -> Decimal | None:
        if value is None:
            return None

        if value == "":
            return None

        return Decimal(str(value))

    def get_market_snapshot(
        self,
        *,
        symbol: str,
        exchange_segment: str,
        security_id: str | int,
        instrument_type: str = "EQUITY",
        market: str = "INDIA",
        country: str | None = "IN",
    ) -> MarketSnapshot:
        """
        Retrieve Dhan quote data and normalize it into
        the canonical MarketSnapshot.
        """
        response = self.get_quote(
            exchange_segment,
            security_id,
        )

        raw = self._extract_instrument_data(
            response,
            exchange_segment,
            security_id,
        )

        now = datetime.now(timezone.utc)

        ohlc = raw.get("ohlc", {})

        if not isinstance(ohlc, Mapping):
            ohlc = {}

        price = self._decimal(raw.get("last_price"))

        if price is None:
            raise ValueError(
                "Dhan quote did not contain last_price"
            )

        observation = MarketObservation(
            price=price,
            open=self._decimal(ohlc.get("open")),
            high=self._decimal(ohlc.get("high")),
            low=self._decimal(ohlc.get("low")),
            close=self._decimal(ohlc.get("close")),
            volume=self._decimal(raw.get("volume")),
            open_interest=self._decimal(raw.get("oi")),
        )

        quality = MarketDataQuality(
            source="dhan",
            source_timestamp=now,
            received_timestamp=now,
            latency_ms=0.0,
            is_complete=True,
        )

        state = MarketState(
            session=MarketSessionState.OPEN,
            halted=False,
            tradable=True,
        )

        metadata = {
            "provider": "dhan",
            "exchange_segment": exchange_segment,
            "security_id": str(security_id),
            "average_price": raw.get("average_price"),
            "buy_quantity": raw.get("buy_quantity"),
            "sell_quantity": raw.get("sell_quantity"),
            "last_quantity": raw.get("last_quantity"),
            "net_change": raw.get("net_change"),
            "oi_day_high": raw.get("oi_day_high"),
            "oi_day_low": raw.get("oi_day_low"),
            "upper_circuit_limit": raw.get(
                "upper_circuit_limit"
            ),
            "lower_circuit_limit": raw.get(
                "lower_circuit_limit"
            ),
        }

        return MarketSnapshot(
            market=MarketIdentity(
                market=market,
                segment=exchange_segment,
                country=country,
            ),
            instrument=InstrumentIdentity(
                symbol=symbol.upper(),
                instrument_type=instrument_type,
                instrument_id=str(security_id),
            ),
            venue=VenueIdentity(
                venue="DHAN",
            ),
            observed_at=now,
            observation=observation,
            data_quality=quality,
            state=state,
            metadata=metadata,
        )