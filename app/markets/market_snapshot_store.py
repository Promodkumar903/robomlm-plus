from __future__ import annotations

from typing import Dict, Tuple

from schemas.market.market_snapshot import MarketSnapshot


class MarketSnapshotStore:
    """
    In-memory snapshot store.

    Stores the latest MarketSnapshot by:
        market + venue + symbol
    """

    def __init__(self) -> None:
        self._snapshots: Dict[
            Tuple[str, str, str],
            MarketSnapshot,
        ] = {}

    def _key(
        self,
        market: str,
        venue: str,
        symbol: str,
    ) -> tuple[str, str, str]:
        return (
            str(market).upper(),
            str(venue).upper(),
            str(symbol).upper(),
        )

    def put(
        self,
        snapshot: MarketSnapshot,
    ) -> None:
        key = self._key(
            snapshot.market.market,
            snapshot.venue.venue,
            snapshot.instrument.symbol,
        )

        self._snapshots[key] = snapshot

    def get(
        self,
        *,
        market: str,
        venue: str,
        symbol: str,
    ) -> MarketSnapshot | None:
        return self._snapshots.get(
            self._key(
                market,
                venue,
                symbol,
            )
        )

    def count(self) -> int:
        return len(self._snapshots)