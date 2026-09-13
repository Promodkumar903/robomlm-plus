from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class InstrumentIdentity:
    """
    Canonical identity of a tradable market instrument.

    This schema identifies the instrument itself and does not contain
    broker-specific execution instructions.
    """

    instrument_id: str
    symbol: str

    exchange: str | None = None
    market: str | None = None
    asset_class: str | None = None
    instrument_type: str | None = None

    currency: str | None = None
    quote_currency: str | None = None

    underlying_symbol: str | None = None
    expiry: str | None = None
    strike: float | None = None
    option_type: str | None = None

    contract_size: float | None = None
    tick_size: float | None = None
    lot_size: float | None = None

    venue: str | None = None
    status: str = "ACTIVE"

    metadata: Mapping[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        """Return whether the minimum instrument identity is valid."""
        if not self.instrument_id:
            return False

        if not self.symbol:
            return False

        if self.contract_size is not None and self.contract_size <= 0:
            return False

        if self.tick_size is not None and self.tick_size <= 0:
            return False

        if self.lot_size is not None and self.lot_size <= 0:
            return False

        if self.strike is not None and self.strike < 0:
            return False

        return True