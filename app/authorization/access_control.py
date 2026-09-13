from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    user_id: str
    resource: str
    action: str
    reason: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AccessControl:
    """
    Central access-control service.

    Maintains user -> resource -> allowed actions in memory and
    evaluates access requests deterministically.
    """

    def __init__(self) -> None:
        self._permissions: dict[str, dict[str, set[str]]] = {}
        self._disabled_users: set[str] = set()
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
        resource: str,
        action: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        resource = self._normalize(resource, "resource")
        action = self._normalize(action, "action").lower()

        with self._lock:
            resources = self._permissions.setdefault(user_id, {})
            actions = resources.setdefault(resource, set())
            before = len(actions)
            actions.add(action)
            return len(actions) > before

    def revoke(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        resource = self._normalize(resource, "resource")
        action = self._normalize(action, "action").lower()

        with self._lock:
            resources = self._permissions.get(user_id)

            if not resources:
                return False

            actions = resources.get(resource)

            if not actions or action not in actions:
                return False

            actions.remove(action)

            if not actions:
                resources.pop(resource, None)

            if not resources:
                self._permissions.pop(user_id, None)

            return True

    def disable_user(self, user_id: str) -> None:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            self._disabled_users.add(user_id)

    def enable_user(self, user_id: str) -> None:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            self._disabled_users.discard(user_id)

    def is_user_disabled(self, user_id: str) -> bool:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            return user_id in self._disabled_users

    def check(
        self,
        user_id: str,
        resource: str,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> AccessDecision:
        user_id = self._normalize(user_id, "user_id")
        resource = self._normalize(resource, "resource")
        action = self._normalize(action, "action").lower()
        timestamp = datetime.now(timezone.utc)

        with self._lock:
            if user_id in self._disabled_users:
                return AccessDecision(
                    allowed=False,
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    reason="User access is disabled",
                    timestamp=timestamp,
                    metadata=dict(metadata) if metadata else None,
                )

            resources = self._permissions.get(user_id, {})
            actions = resources.get(resource, set())

            if action in actions or "*" in actions:
                return AccessDecision(
                    allowed=True,
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    reason="Permission granted",
                    timestamp=timestamp,
                    metadata=dict(metadata) if metadata else None,
                )

            return AccessDecision(
                allowed=False,
                user_id=user_id,
                resource=resource,
                action=action,
                reason="Permission denied",
                timestamp=timestamp,
                metadata=dict(metadata) if metadata else None,
            )

    def has_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> bool:
        return self.check(user_id, resource, action).allowed

    def permissions_for_user(
        self,
        user_id: str,
    ) -> dict[str, tuple[str, ...]]:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            resources = self._permissions.get(user_id, {})

            return {
                resource: tuple(sorted(actions))
                for resource, actions in resources.items()
            }

    def revoke_all(self, user_id: str) -> int:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            resources = self._permissions.pop(user_id, {})

            return sum(len(actions) for actions in resources.values())

    def clear(self) -> None:
        with self._lock:
            self._permissions.clear()
            self._disabled_users.clear()

    def user_count(self) -> int:
        with self._lock:
            return len(self._permissions)

    def disabled_user_count(self) -> int:
        with self._lock:
            return len(self._disabled_users)