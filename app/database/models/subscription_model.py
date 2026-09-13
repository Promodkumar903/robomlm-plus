"""
ROBOMLM PLUS
Subscription Database Model

Purpose:
    Define the persistent structure for user subscriptions,
    plan assignments, billing state and entitlement periods.

Design:
    - Subscription data is separate from authorization logic.
    - Supports plan lifecycle and entitlement timing.
    - Does not grant permissions by itself.
    - No payment processing logic.
    - No broker/exchange interaction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class SubscriptionRecord:
    """Structured subscription record."""

    subscription_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    user_id: str = ""

    plan_id: str = ""

    status: str = ""

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    expires_at: Optional[datetime] = None

    cancelled_at: Optional[datetime] = None

    trial: bool = False

    auto_renew: bool = False

    billing_reference: Optional[str] = None

    provider: Optional[str] = None

    currency: Optional[str] = None

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
        """Normalize and validate subscription fields."""

        self.subscription_id = str(
            self.subscription_id
        ).strip()

        self.user_id = str(
            self.user_id
        ).strip()

        self.plan_id = str(
            self.plan_id
        ).strip()

        self.status = str(
            self.status
        ).strip()

        if not self.subscription_id:
            raise ValueError(
                "subscription_id cannot be empty."
            )

        if not self.user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if not self.plan_id:
            raise ValueError(
                "plan_id cannot be empty."
            )

        if not self.status:
            raise ValueError(
                "status cannot be empty."
            )

        if self.billing_reference is not None:
            self.billing_reference = (
                str(self.billing_reference).strip()
                or None
            )

        if self.provider is not None:
            self.provider = (
                str(self.provider).strip()
                or None
            )

        if self.currency is not None:
            self.currency = (
                str(self.currency).strip()
                or None
            )

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        self.started_at = self._normalize_datetime(
            self.started_at
        )

        if self.expires_at is not None:
            self.expires_at = self._normalize_datetime(
                self.expires_at
            )

        if self.cancelled_at is not None:
            self.cancelled_at = self._normalize_datetime(
                self.cancelled_at
            )

        self.created_at = self._normalize_datetime(
            self.created_at
        )

        self.updated_at = self._normalize_datetime(
            self.updated_at
        )

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        """Ensure datetime values are timezone-aware UTC."""

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

    def touch(self) -> None:
        """Update the modification timestamp."""

        self.updated_at = datetime.now(
            timezone.utc
        )

    @property
    def is_cancelled(self) -> bool:
        """Return whether the subscription has been cancelled."""

        return self.cancelled_at is not None

    @property
    def is_expired(self) -> bool:
        """Return whether the subscription has passed its expiry."""

        if self.expires_at is None:
            return False

        return datetime.now(
            timezone.utc
        ) >= self.expires_at

    @property
    def is_active(self) -> bool:
        """
        Return whether the subscription is currently active.

        Final entitlement authorization remains the responsibility
        of the subscription/authorization services.
        """

        if self.is_cancelled:
            return False

        if self.is_expired:
            return False

        return self.status.lower() in {
            "active",
            "trial",
        }

    def cancel(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Mark the subscription as cancelled."""

        self.cancelled_at = (
            self._normalize_datetime(timestamp)
            if timestamp is not None
            else datetime.now(timezone.utc)
        )

        self.status = "cancelled"

        self.touch()

    def expire(
        self,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Mark the subscription as expired."""

        expiry_time = (
            self._normalize_datetime(timestamp)
            if timestamp is not None
            else datetime.now(timezone.utc)
        )

        self.expires_at = expiry_time
        self.status = "expired"

        self.touch()

    def activate(
        self,
        started_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """Activate the subscription."""

        if started_at is not None:
            self.started_at = self._normalize_datetime(
                started_at
            )

        if expires_at is not None:
            self.expires_at = self._normalize_datetime(
                expires_at
            )

        self.cancelled_at = None
        self.status = "active"

        self.touch()

    def set_plan(
        self,
        plan_id: str,
    ) -> None:
        """Change the assigned plan."""

        plan_id = str(plan_id).strip()

        if not plan_id:
            raise ValueError(
                "plan_id cannot be empty."
            )

        self.plan_id = plan_id
        self.touch()

    def set_auto_renew(
        self,
        enabled: bool,
    ) -> None:
        """Update automatic renewal preference."""

        if not isinstance(enabled, bool):
            raise TypeError(
                "auto_renew must be a boolean."
            )

        self.auto_renew = enabled
        self.touch()

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Add or replace a metadata value."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value
        self.touch()

    def remove_metadata(
        self,
        key: str,
    ) -> bool:
        """Remove metadata if present."""

        key = str(key).strip()

        if key in self.metadata:
            del self.metadata[key]
            self.touch()
            return True

        return False

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""

        data = asdict(self)

        data["started_at"] = (
            self.started_at.isoformat()
        )

        if self.expires_at is not None:
            data["expires_at"] = (
                self.expires_at.isoformat()
            )

        if self.cancelled_at is not None:
            data["cancelled_at"] = (
                self.cancelled_at.isoformat()
            )

        data["created_at"] = (
            self.created_at.isoformat()
        )

        data["updated_at"] = (
            self.updated_at.isoformat()
        )

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "SubscriptionRecord":
        """Create a subscription record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping."
            )

        values = dict(data)

        for field_name in (
            "started_at",
            "expires_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = (
                    datetime.fromisoformat(value)
                )

        return cls(**values)

    def with_metadata(
        self,
        key: str,
        value: Any,
    ) -> "SubscriptionRecord":
        """Return a copy containing additional metadata."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        copied_metadata = dict(
            self.metadata
        )

        copied_metadata[key] = value

        return SubscriptionRecord(
            subscription_id=self.subscription_id,
            user_id=self.user_id,
            plan_id=self.plan_id,
            status=self.status,
            started_at=self.started_at,
            expires_at=self.expires_at,
            cancelled_at=self.cancelled_at,
            trial=self.trial,
            auto_renew=self.auto_renew,
            billing_reference=self.billing_reference,
            provider=self.provider,
            currency=self.currency,
            metadata=copied_metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


def create_subscription_record(
    *,
    user_id: str,
    plan_id: str,
    status: str = "active",
    started_at: Optional[datetime] = None,
    expires_at: Optional[datetime] = None,
    trial: bool = False,
    auto_renew: bool = False,
    billing_reference: Optional[str] = None,
    provider: Optional[str] = None,
    currency: Optional[str] = None,
    metadata: Optional[
        Mapping[str, Any]
    ] = None,
) -> SubscriptionRecord:
    """Convenience factory for subscription records."""

    return SubscriptionRecord(
        user_id=user_id,
        plan_id=plan_id,
        status=status,
        started_at=(
            started_at
            or datetime.now(timezone.utc)
        ),
        expires_at=expires_at,
        trial=trial,
        auto_renew=auto_renew,
        billing_reference=billing_reference,
        provider=provider,
        currency=currency,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "SubscriptionRecord",
    "create_subscription_record",
]