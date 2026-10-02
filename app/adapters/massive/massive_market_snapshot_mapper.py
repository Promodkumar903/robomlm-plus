from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from schemas.market.market_snapshot import (
    ContractIdentity,
    InstrumentIdentity,
    MarketDataQuality,
    MarketIdentity,
    MarketObservation,
    MarketProvenance,
    MarketSessionState,
    MarketSnapshot,
    MarketState,
    MarketTiming,
    VenueIdentity,
)


class MassiveMarketSnapshotMapper:
    """
    Massive raw payload -> canonical MarketSnapshot
    """

    PROVIDER = "MASSIVE"

    @staticmethod
    def _decimal(value: Any) -> Decimal | None:
        if value is None:
            return None

        try:
            return Decimal(str(value))
        except Exception:
            return None

    @staticmethod
    def _timestamp(
        value: Any,
    ) -> datetime:
        if isinstance(value, datetime):
            if value.tzinfo:
                return value

            return value.replace(
                tzinfo=timezone.utc
            )

        if value is None:
            return datetime.now(
                timezone.utc
            )

        try:
            return datetime.fromtimestamp(
                float(value),
                tz=timezone.utc,
            )
        except Exception:
            return datetime.now(
                timezone.utc
            )

    def map_snapshot(
        self,
        payload: dict[str, Any],
    ) -> MarketSnapshot:

        symbol = str(
            payload.get(
                "ticker",
                payload.get(
                    "symbol",
                    "UNKNOWN",
                ),
            )
        )

        observed_at = self._timestamp(
            payload.get("updated")
            or payload.get("sip_timestamp")
            or payload.get("participant_timestamp")
        )

        observation = MarketObservation(
            observed_at=observed_at,
            price=self._decimal(
                payload.get("last")
            ),
            open=self._decimal(
                payload.get("open")
            ),
            high=self._decimal(
                payload.get("high")
            ),
            low=self._decimal(
                payload.get("low")
            ),
            close=self._decimal(
                payload.get("close")
            ),
            volume=self._decimal(
                payload.get("volume")
            ),
            bid=self._decimal(
                payload.get("bid")
            ),
            ask=self._decimal(
                payload.get("ask")
            ),
            fields_present=tuple(
                sorted(payload.keys())
            ),
        )

        timing = MarketTiming(
            source_timestamp=observed_at,
            received_timestamp=datetime.now(
                timezone.utc
            ),
            observed_at=observed_at,
        )

        quality = MarketDataQuality(
            source=self.PROVIDER,
            source_timestamp=timing.source_timestamp,
            received_timestamp=timing.received_timestamp,
        )

        provenance = MarketProvenance(
            provider=self.PROVIDER,
            provider_symbol=symbol,
            metadata={
                "raw_fields": list(
                    payload.keys()
                )
            },
        )

        return MarketSnapshot(
            market=MarketIdentity(
                market="EQUITY",
                segment="SPOT",
                country="US",
            ),
            instrument=InstrumentIdentity(
                symbol=symbol,
                instrument_type="EQUITY",
                instrument_id=symbol,
            ),
            venue=VenueIdentity(
                venue="MASSIVE"
            ),
            contract=None,
            observation=observation,
            timing=timing,
            data_quality=quality,
            provenance=provenance,
            state=MarketState(
                session=MarketSessionState.UNKNOWN
            ),
            metadata={
                "provider": self.PROVIDER
            },
        )