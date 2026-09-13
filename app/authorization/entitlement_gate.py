from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class Entitlement:
    user_id: str
    feature: str
    plan: str
    enabled: bool
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = None

    def is_active(self, now: datetime | None = None) -> bool:
        if not self.enabled:
            return False

        if self.expires_at is None:
            return True

        current = now or datetime.now(timezone.utc)
        return current < self.expires_at

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        if self.expires_at is not None:
            data["expires_at"] = self.expires_at.isoformat()

        return data


@dataclass(frozen=True)
class EntitlementDecision:
    allowed: bool
    user_id: str
    feature: str
    plan: str | None
    reason: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class EntitlementGate:
    """
    Controls feature access based on user entitlements and subscription plans.

    An entitlement is specific to:
        user -> feature -> plan

    Expired or disabled entitlements are automatically denied.
    """

    def __init__(self) -> None:
        self._entitlements: dict[str, dict[str, Entitlement]] = {}
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    def grant(
        self,
        user_id: str,
        feature: str,
        plan: str,
        *,
        expires_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Entitlement:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")
        plan = self._normalize(plan, "plan")

        if expires_at is not None:
            if expires_at.tzinfo is None:
                raise ValueError(
                    "expires_at must be timezone-aware"
                )

        entitlement = Entitlement(
            user_id=user_id,
            feature=feature,
            plan=plan,
            enabled=True,
            expires_at=expires_at,
            metadata=dict(metadata) if metadata else None,
        )

        with self._lock:
            self._entitlements.setdefault(user_id, {})[
                feature
            ] = entitlement

        return entitlement

    def disable(
        self,
        user_id: str,
        feature: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")

        with self._lock:
            user_features = self._entitlements.get(user_id)

            if not user_features:
                return False

            entitlement = user_features.get(feature)

            if entitlement is None:
                return False

            if not entitlement.enabled:
                return False

            user_features[feature] = Entitlement(
                user_id=entitlement.user_id,
                feature=entitlement.feature,
                plan=entitlement.plan,
                enabled=False,
                expires_at=entitlement.expires_at,
                metadata=entitlement.metadata,
            )

            return True

    def enable(
        self,
        user_id: str,
        feature: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")

        with self._lock:
            user_features = self._entitlements.get(user_id)

            if not user_features:
                return False

            entitlement = user_features.get(feature)

            if entitlement is None:
                return False

            user_features[feature] = Entitlement(
                user_id=entitlement.user_id,
                feature=entitlement.feature,
                plan=entitlement.plan,
                enabled=True,
                expires_at=entitlement.expires_at,
                metadata=entitlement.metadata,
            )

            return True

    def check(
        self,
        user_id: str,
        feature: str,
        *,
        required_plan: str | None = None,
    ) -> EntitlementDecision:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")

        if required_plan is not None:
            required_plan = self._normalize(
                required_plan,
                "required_plan",
            )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            entitlement = self._entitlements.get(
                user_id,
                {},
            ).get(feature)

            if entitlement is None:
                return EntitlementDecision(
                    allowed=False,
                    user_id=user_id,
                    feature=feature,
                    plan=None,
                    reason="No entitlement exists",
                    timestamp=timestamp,
                )

            if not entitlement.enabled:
                return EntitlementDecision(
                    allowed=False,
                    user_id=user_id,
                    feature=feature,
                    plan=entitlement.plan,
                    reason="Entitlement is disabled",
                    timestamp=timestamp,
                )

            if not entitlement.is_active(timestamp):
                return EntitlementDecision(
                    allowed=False,
                    user_id=user_id,
                    feature=feature,
                    plan=entitlement.plan,
                    reason="Entitlement has expired",
                    timestamp=timestamp,
                )

            if (
                required_plan is not None
                and entitlement.plan != required_plan
            ):
                return EntitlementDecision(
                    allowed=False,
                    user_id=user_id,
                    feature=feature,
                    plan=entitlement.plan,
                    reason="Required subscription plan not satisfied",
                    timestamp=timestamp,
                )

            return EntitlementDecision(
                allowed=True,
                user_id=user_id,
                feature=feature,
                plan=entitlement.plan,
                reason="Entitlement granted",
                timestamp=timestamp,
            )

    def is_entitled(
        self,
        user_id: str,
        feature: str,
        *,
        required_plan: str | None = None,
    ) -> bool:
        return self.check(
            user_id,
            feature,
            required_plan=required_plan,
        ).allowed

    def get(
        self,
        user_id: str,
        feature: str,
    ) -> Entitlement | None:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")

        with self._lock:
            return self._entitlements.get(
                user_id,
                {},
            ).get(feature)

    def features_for_user(
        self,
        user_id: str,
        active_only: bool = True,
    ) -> dict[str, Entitlement]:
        user_id = self._normalize(user_id, "user_id")
        now = datetime.now(timezone.utc)

        with self._lock:
            features = self._entitlements.get(
                user_id,
                {},
            )

            if not active_only:
                return dict(features)

            return {
                feature: entitlement
                for feature, entitlement in features.items()
                if entitlement.is_active(now)
            }

    def revoke_feature(
        self,
        user_id: str,
        feature: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        feature = self._normalize(feature, "feature")

        with self._lock:
            features = self._entitlements.get(user_id)

            if not features or feature not in features:
                return False

            del features[feature]

            if not features:
                self._entitlements.pop(user_id, None)

            return True

    def revoke_all_for_user(self, user_id: str) -> int:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            features = self._entitlements.pop(user_id, {})
            return len(features)

    def cleanup_expired(self) -> int:
        now = datetime.now(timezone.utc)
        removed = 0

        with self._lock:
            for user_id in list(self._entitlements):
                features = self._entitlements[user_id]

                expired_features = [
                    feature
                    for feature, entitlement in features.items()
                    if (
                        entitlement.expires_at is not None
                        and entitlement.expires_at <= now
                    )
                ]

                for feature in expired_features:
                    del features[feature]
                    removed += 1

                if not features:
                    self._entitlements.pop(user_id, None)

        return removed

    def user_count(self) -> int:
        with self._lock:
            return len(self._entitlements)

    def entitlement_count(self) -> int:
        with self._lock:
            return sum(
                len(features)
                for features in self._entitlements.values()
            )

    def clear(self) -> None:
        with self._lock:
            self._entitlements.clear()