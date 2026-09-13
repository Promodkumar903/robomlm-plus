from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ContractIdentity:
    """
    Canonical identity of a tradable contract/instrument.

    Keeps contract-level identity separate from market observations,
    decisions, evidence, and execution results.
    """

    contract_id: str
    instrument_id: str
    symbol: str

    market: str | None = None
    exchange: str | None = None
    venue: str | None = None

    asset_class: str | None = None
    contract_type: str | None = None

    underlying_symbol: str | None = None

    expiry: str | None = None
    strike: float | None = None
    option_type: str | None = None

    currency: str | None = None
    quote_currency: str | None = None

    contract_size: float | None = None
    lot_size: float | None = None
    tick_size: float | None = None

    status: str = "ACTIVE"

    metadata: Mapping[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["created_at"] = self.created_at.isoformat()
        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        if not self.contract_id:
            return False

        if not self.instrument_id:
            return False

        if not self.symbol:
            return False

        if self.strike is not None and self.strike < 0:
            return False

        if self.contract_size is not None and self.contract_size <= 0:
            return False

        if self.lot_size is not None and self.lot_size <= 0:
            return False

        if self.tick_size is not None and self.tick_size <= 0:
            return False

        return True

    def is_expired(self, now: datetime | None = None) -> bool:
        """
        Determine expiry status when an expiry value is available.

        ISO date/datetime strings are supported. Invalid/unknown expiry
        values are treated as non-expired rather than guessed.
        """

        if not self.expiry:
            return False

        try:
            expiry_value = self.expiry.strip()

            if "T" in expiry_value:
                expiry_dt = datetime.fromisoformat(
                    expiry_value.replace("Z", "+00:00")
                )
            else:
                expiry_dt = datetime.fromisoformat(
                    f"{expiry_value}T23:59:59+00:00"
                )

            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)

            reference_time = now or datetime.now(timezone.utc)

            if reference_time.tzinfo is None:
                reference_time = reference_time.replace(
                    tzinfo=timezone.utc
                )

            return reference_time >= expiry_dt

        except (TypeError, ValueError):
            return False


@dataclass(frozen=True)
class ContractSpecification:
    """
    Static specification describing how a contract behaves.
    """

    contract_id: str

    price_precision: int | None = None
    quantity_precision: int | None = None

    min_quantity: float | None = None
    max_quantity: float | None = None

    min_notional: float | None = None

    margin_required: float | None = None

    settlement_type: str | None = None
    settlement_currency: str | None = None

    trading_session: str | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        if not self.contract_id:
            return False

        if self.price_precision is not None and self.price_precision < 0:
            return False

        if (
            self.quantity_precision is not None
            and self.quantity_precision < 0
        ):
            return False

        if self.min_quantity is not None and self.min_quantity < 0:
            return False

        if self.max_quantity is not None and self.max_quantity < 0:
            return False

        if (
            self.min_quantity is not None
            and self.max_quantity is not None
            and self.min_quantity > self.max_quantity
        ):
            return False

        if self.min_notional is not None and self.min_notional < 0:
            return False

        if self.margin_required is not None and self.margin_required < 0:
            return False

        return True