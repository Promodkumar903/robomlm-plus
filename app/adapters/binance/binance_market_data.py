from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

from app.adapters.binance.binance_client import BinanceClient
from app.adapters.binance.binance_raw import BinanceRawMarketData

from schemas.market.market_snapshot import (
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    MarketTiming,
    ObservationKind,
    VenueIdentity,
)

class BinanceMarketData:
    """
    Binance provider adapter.

    Flow:

        Binance provider response
            ->
        BinanceRawMarketData
            ->
        canonical MarketSnapshot

    Provider-native data remains preserved in the raw boundary.

    This adapter does not calculate intelligence.
    """

    def __init__(self, client: BinanceClient) -> None:
        self._client = client
        self._last_raw: BinanceRawMarketData | None = None

    @property
    def provider_name(self) -> str:
        return self._client.provider_name

    @property
    def last_raw(self) -> BinanceRawMarketData | None:
        return self._last_raw

    def connect(self) -> None:
        self._client.ping()

    def close(self) -> None:
        self._client.close()

    def is_connected(self) -> bool:
        return self._client.is_connected()

    def fetch_raw_market_data(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        provider_symbol = (
            str(symbol)
            .strip()
            .replace("/", "")
            .replace("-", "")
            .upper()
        )

        return self._client.get(
            "/api/v3/ticker/24hr",
            params={"symbol": provider_symbol},
        )

    def get_raw_ticker(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        return self.fetch_raw_market_data(symbol)

    def get_raw_market_packet(
        self,
        symbol: str,
    ):
        return self._client.get_market_data_packet(
            symbol
        )

    def get_market_snapshot(
        self,
        symbol: str,
    ) -> MarketSnapshot:
        """
        Fetch Binance provider-native response,
        preserve it as raw data, then normalize it
        into the canonical MarketSnapshot boundary.
        """

        raw_payload = self.fetch_raw_market_data(symbol)

        raw_data = BinanceRawMarketData(
            raw_payload
        )

        self._last_raw = raw_data

        return self.normalize_raw_to_snapshot(
            raw_data
        )

    def normalize_raw_to_snapshot(
        self,
        raw_data: BinanceRawMarketData,
    ) -> MarketSnapshot:
        """
        Explicit provider-native -> canonical boundary.

        No intelligence or decision calculations happen here.
        """

        payload = raw_data.payload

        symbol = str(
            payload.get("symbol") or ""
        ).strip().upper()

        if not symbol:
            raise ValueError(
                "BINANCE_RAW_MISSING_SYMBOL"
            )

        price = self._decimal(
            payload.get("lastPrice"),
            field="lastPrice",
            required=True,
        )

        high = self._decimal(
            payload.get("highPrice"),
            field="highPrice",
            required=True,
        )

        low = self._decimal(
            payload.get("lowPrice"),
            field="lowPrice",
            required=True,
        )

        volume = self._decimal(
            payload.get("volume"),
            field="volume",
            required=True,
        )

        turnover = self._decimal(
            payload.get("quoteVolume"),
            field="quoteVolume",
            required=True,
        )

        received_at = datetime.now(
            timezone.utc
        )

        provider_timestamp = (
            self._timestamp_from_ms(
                payload.get("closeTime")
            )
        )

        source_timestamp = min(
            provider_timestamp,
            received_at,
        )

        latency_ms = max(
            0.0,
            (
                received_at - source_timestamp
            ).total_seconds()
            * 1000.0,
        )

        observation = MarketObservation(
            observed_at=received_at,
            price=price,
            high=high,
            low=low,
            volume=volume,
            turnover=turnover,
            observation_kind=ObservationKind.OBSERVED,
            fields_present=(
                "price",
                "high",
                "low",
                "volume",
                "turnover",
            ),
        )

        return MarketSnapshot(
            market=MarketIdentity(
                market="CRYPTO",
                segment="SPOT",
                country="GLOBAL",
            ),
            instrument=InstrumentIdentity(
                symbol=symbol,
                instrument_type="SPOT",
                instrument_id=symbol,
            ),
                        venue=VenueIdentity(
                venue="BINANCE",
                venue_id="BINANCE",
            ),
            observation=observation,
            timing=MarketTiming(
                source_timestamp=source_timestamp,
                received_timestamp=received_at,
                observed_at=received_at,
            ),
            data_quality=MarketDataQuality(
                source="binance",
                source_timestamp=source_timestamp,
                received_timestamp=received_at,
                sequence=None,
                latency_ms=latency_ms,
                is_complete=True,
                is_stale=False,
                quality_flags=(),
            ),
            state=MarketState(
                session=MarketSessionState.OPEN,
                halted=False,
                tradable=True,
                state_reason=None,
            ),
            contract=None,
            snapshot_id=None,
            metadata={
                "provider": "binance",
                "endpoint": "/api/v3/ticker/24hr",
                "observation_kind": "PROVIDER_OBSERVED",
            },
        )

    @staticmethod
    def _decimal(
        value: Any,
        *,
        field: str,
        required: bool,
    ) -> Decimal | None:
        if value is None or value == "":
            if required:
                raise ValueError(
                    f"BINANCE_RAW_MISSING_FIELD:{field}"
                )
            return None

        try:
            result = Decimal(str(value))
        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as exc:
            raise ValueError(
                f"BINANCE_RAW_INVALID_FIELD:{field}"
            ) from exc

        if not result.is_finite():
            raise ValueError(
                f"BINANCE_RAW_NON_FINITE_FIELD:{field}"
            )

        return result

    @staticmethod
    def _timestamp_from_ms(
        value: Any,
    ) -> datetime:
        if value is None:
            return datetime.now(
                timezone.utc
            )

        try:
            milliseconds = int(value)
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "BINANCE_RAW_INVALID_TIMESTAMP"
            ) from exc

        return datetime.fromtimestamp(
            milliseconds / 1000.0,
            tz=timezone.utc,
        )