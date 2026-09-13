"""
ROBOMLM PLUS
Trade Database Model

Purpose:
    Define the persistent structure for a trade lifecycle record.

Design:
    - Separates trade records from execution logic.
    - Supports BUY/SELL, entry/exit, SL/TP and P&L tracking.
    - Preserves market/instrument/venue identity.
    - Supports PAPER, DEMO and LIVE modes.
    - Does not place, modify or cancel orders.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class TradeRecord:
    """Structured trade lifecycle record."""

    trade_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    user_id: str = ""

    session_id: Optional[str] = None

    request_id: Optional[str] = None

    mode: str = ""

    status: str = ""

    side: str = ""

    market: str = ""

    instrument: str = ""

    venue: str = ""

    contract: Optional[str] = None

    timeframe: Optional[str] = None

    quantity: float = 0.0

    entry_price: Optional[float] = None

    exit_price: Optional[float] = None

    stop_loss: Optional[float] = None

    take_profit: Optional[float] = None

    realized_pnl: Optional[float] = None

    unrealized_pnl: Optional[float] = None

    fees: float = 0.0

    entry_reason: Optional[str] = None

    exit_reason: Optional[str] = None

    decision_id: Optional[str] = None

    evidence_ids: list[str] = field(
        default_factory=list
    )

    opened_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate trade fields."""

        self.trade_id = str(
            self.trade_id
        ).strip()

        self.user_id = str(
            self.user_id
        ).strip()

        self.mode = str(
            self.mode
        ).strip()

        self.status = str(
            self.status
        ).strip()

        self.side = str(
            self.side
        ).strip().upper()

        self.market = str(
            self.market
        ).strip()

        self.instrument = str(
            self.instrument
        ).strip()

        self.venue = str(
            self.venue
        ).strip()

        if not self.trade_id:
            raise ValueError(
                "trade_id cannot be empty."
            )

        if not self.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if not self.mode:
            raise ValueError(
                "mode cannot be empty."
            )

        if not self.status:
            raise ValueError(
                "status cannot be empty."
            )

        if not self.side:
            raise ValueError(
                "side cannot be empty."
            )

        if not self.market:
            raise ValueError(
                "market cannot be empty."
            )

        if not self.instrument:
            raise ValueError(
                "instrument cannot be empty."
            )

        if not self.venue:
            raise ValueError(
                "venue cannot be empty."
            )

        self.quantity = self._validate_nonnegative(
            self.quantity,
            "quantity",
        )

        self.fees = self._validate_nonnegative(
            self.fees,
            "fees",
        )

        if self.entry_price is not None:
            self.entry_price = self._validate_positive(
                self.entry_price,
                "entry_price",
            )

        if self.exit_price is not None:
            self.exit_price = self._validate_positive(
                self.exit_price,
                "exit_price",
            )

        if self.stop_loss is not None:
            self.stop_loss = self._validate_positive(
                self.stop_loss,
                "stop_loss",
            )

        if self.take_profit is not None:
            self.take_profit = self._validate_positive(
                self.take_profit,
                "take_profit",
            )

        if self.realized_pnl is not None:
            self.realized_pnl = float(
                self.realized_pnl
            )

        if self.unrealized_pnl is not None:
            self.unrealized_pnl = float(
                self.unrealized_pnl
            )

        self.session_id = self._clean_optional(
            self.session_id
        )

        self.request_id = self._clean_optional(
            self.request_id
        )

        self.contract = self._clean_optional(
            self.contract
        )

        self.timeframe = self._clean_optional(
            self.timeframe
        )

        self.entry_reason = self._clean_optional(
            self.entry_reason
        )

        self.exit_reason = self._clean_optional(
            self.exit_reason
        )

        self.decision_id = self._clean_optional(
            self.decision_id
        )

        if not isinstance(self.evidence_ids, list):
            self.evidence_ids = list(
                self.evidence_ids
            )

        self.evidence_ids = [
            str(item).strip()
            for item in self.evidence_ids
            if str(item).strip()
        ]

        if not isinstance(self.metadata, dict):
            self.metadata = dict(
                self.metadata
            )

        self.opened_at = self._normalize_optional_datetime(
            self.opened_at
        )

        self.closed_at = self._normalize_optional_datetime(
            self.closed_at
        )

        self.created_at = self._normalize_datetime(
            self.created_at
        )

        self.updated_at = self._normalize_datetime(
            self.updated_at
        )

    @staticmethod
    def _clean_optional(
        value: Optional[Any],
    ) -> Optional[str]:
        """Normalize an optional string."""

        if value is None:
            return None

        cleaned = str(value).strip()

        return cleaned or None

    @staticmethod
    def _validate_nonnegative(
        value: float,
        field_name: str,
    ) -> float:
        """Validate a non-negative numeric value."""

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric."
            ) from exc

        if numeric < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        return numeric

    @staticmethod
    def _validate_positive(
        value: float,
        field_name: str,
    ) -> float:
        """Validate a strictly positive numeric value."""

        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{field_name} must be numeric."
            ) from exc

        if numeric <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return numeric

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """Normalize datetime to timezone-aware UTC."""

        if not isinstance(value, datetime):
            raise TypeError(
                "Datetime value must be a datetime instance."
            )

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    @classmethod
    def _normalize_optional_datetime(
        cls,
        value: Optional[datetime],
    ) -> Optional[datetime]:
        """Normalize an optional datetime."""

        if value is None:
            return None

        return cls._normalize_datetime(value)

    @property
    def is_open(self) -> bool:
        """Return whether the trade is currently open."""

        if self.closed_at is not None:
            return False

        return self.status.lower() in {
            "open",
            "active",
            "pending_exit",
        }

    @property
    def is_closed(self) -> bool:
        """Return whether the trade is closed."""

        if self.closed_at is not None:
            return True

        return self.status.lower() in {
            "closed",
            "completed",
            "cancelled",
            "rejected",
        }

    @property
    def net_realized_pnl(self) -> Optional[float]:
        """Return realized P&L after fees."""

        if self.realized_pnl is None:
            return None

        return self.realized_pnl - self.fees

    def open_trade(
        self,
        entry_price: float,
        opened_at: Optional[datetime] = None,
    ) -> None:
        """Mark the trade as opened."""

        self.entry_price = self._validate_positive(
            entry_price,
            "entry_price",
        )

        self.opened_at = (
            self._normalize_datetime(opened_at)
            if opened_at is not None
            else datetime.now(timezone.utc)
        )

        self.status = "open"
        self.touch()

    def close_trade(
        self,
        exit_price: float,
        realized_pnl: Optional[float] = None,
        exit_reason: Optional[str] = None,
        closed_at: Optional[datetime] = None,
    ) -> None:
        """Mark the trade as closed."""

        self.exit_price = self._validate_positive(
            exit_price,
            "exit_price",
        )

        self.closed_at = (
            self._normalize_datetime(closed_at)
            if closed_at is not None
            else datetime.now(timezone.utc)
        )

        if realized_pnl is not None:
            self.realized_pnl = float(
                realized_pnl
            )

        if exit_reason is not None:
            self.exit_reason = str(
                exit_reason
            ).strip() or None

        self.status = "closed"
        self.unrealized_pnl = None

        self.touch()

    def update_unrealized_pnl(
        self,
        value: float,
    ) -> None:
        """Update current unrealized P&L."""

        self.unrealized_pnl = float(value)
        self.touch()

    def update_levels(
        self,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> None:
        """Update SL/TP levels."""

        if stop_loss is not None:
            self.stop_loss = self._validate_positive(
                stop_loss,
                "stop_loss",
            )

        if take_profit is not None:
            self.take_profit = self._validate_positive(
                take_profit,
                "take_profit",
            )

        self.touch()

    def add_evidence(
        self,
        evidence_id: str,
    ) -> None:
        """Attach an evidence identifier to the trade."""

        evidence_id = str(
            evidence_id
        ).strip()

        if not evidence_id:
            raise ValueError(
                "evidence_id cannot be empty."
            )

        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(
                evidence_id
            )
            self.touch()

    def remove_evidence(
        self,
        evidence_id: str,
    ) -> bool:
        """Remove an evidence identifier."""

        evidence_id = str(
            evidence_id
        ).strip()

        if evidence_id in self.evidence_ids:
            self.evidence_ids.remove(
                evidence_id
            )
            self.touch()
            return True

        return False

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Add or replace trade metadata."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value
        self.touch()

    def touch(self) -> None:
        """Update modification timestamp."""

        self.updated_at = datetime.now(
            timezone.utc
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary."""

        data = asdict(self)

        for field_name in (
            "opened_at",
            "closed_at",
            "created_at",
            "updated_at",
        ):
            value = getattr(self, field_name)

            if value is not None:
                data[field_name] = value.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "TradeRecord":
        """Create a trade record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        values = dict(data)

        for field_name in (
            "opened_at",
            "closed_at",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = (
                    datetime.fromisoformat(value)
                )

        return cls(**values)


def create_trade_record(
    *,
    user_id: str,
    mode: str,
    side: str,
    market: str,
    instrument: str,
    venue: str,
    quantity: float,
    status: str = "pending",
    contract: Optional[str] = None,
    timeframe: Optional[str] = None,
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    decision_id: Optional[str] = None,
    evidence_ids: Optional[list[str]] = None,
    entry_reason: Optional[str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> TradeRecord:
    """Convenience factory for creating a trade record."""

    return TradeRecord(
        user_id=user_id,
        mode=mode,
        status=status,
        side=side,
        market=market,
        instrument=instrument,
        venue=venue,
        quantity=quantity,
        contract=contract,
        timeframe=timeframe,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        decision_id=decision_id,
        evidence_ids=list(
            evidence_ids or []
        ),
        entry_reason=entry_reason,
        metadata=dict(
            metadata or {}
        ),
    )


__all__ = [
    "TradeRecord",
    "create_trade_record",
]