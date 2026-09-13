from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class Permission:
    name: str
    resource: str
    action: str
    description: str = ""
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    user_id: str
    permission: str
    resource: str
    action: str
    reason: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class PermissionService:
    """
    Central permission registry.

    Separates permission definitions from user grants.

    Permission:
        what action is possible on which resource

    User grant:
        which user is allowed to use that permission
    """

    def __init__(self) -> None:
        self._permissions: dict[str, Permission] = {}
        self._user_permissions: dict[str, set[str]] = {}
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    def register(
        self,
        name: str,
        resource: str,
        action: str,
        description: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Permission:
        name = self._normalize(name, "name")
        resource = self._normalize(resource, "resource")
        action = self._normalize(action, "action").lower()

        if not isinstance(description, str):
            raise TypeError("description must be a string")

        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description.strip(),
            metadata=dict(metadata) if metadata else None,
        )

        with self._lock:
            existing = self._permissions.get(name)

            if existing is not None:
                if existing != permission:
                    raise ValueError(
                        f"Permission already exists with different definition: {name}"
                    )
                return existing

            self._permissions[name] = permission

        return permission

    def unregister(self, name: str) -> bool:
        name = self._normalize(name, "name")

        with self._lock:
            if name not in self._permissions:
                return False

            del self._permissions[name]

            for granted in self._user_permissions.values():
                granted.discard(name)

            return True

    def grant(
        self,
        user_id: str,
        permission: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        permission = self._normalize(permission, "permission")

        with self._lock:
            if permission not in self._permissions:
                raise KeyError(
                    f"Unknown permission: {permission}"
                )

            granted = self._user_permissions.setdefault(
                user_id,
                set(),
            )

            before = len(granted)
            granted.add(permission)

            return len(granted) > before

    def revoke(
        self,
        user_id: str,
        permission: str,
    ) -> bool:
        user_id = self._normalize(user_id, "user_id")
        permission = self._normalize(permission, "permission")

        with self._lock:
            granted = self._user_permissions.get(user_id)

            if not granted or permission not in granted:
                return False

            granted.remove(permission)

            if not granted:
                self._user_permissions.pop(user_id, None)

            return True

    def check(
        self,
        user_id: str,
        permission: str,
    ) -> PermissionDecision:
        user_id = self._normalize(user_id, "user_id")
        permission = self._normalize(permission, "permission")

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            definition = self._permissions.get(permission)

            if definition is None:
                return PermissionDecision(
                    allowed=False,
                    user_id=user_id,
                    permission=permission,
                    resource="",
                    action="",
                    reason="Permission is not registered",
                    timestamp=timestamp,
                )

            granted = self._user_permissions.get(
                user_id,
                set(),
            )

            if permission not in granted:
                return PermissionDecision(
                    allowed=False,
                    user_id=user_id,
                    permission=permission,
                    resource=definition.resource,
                    action=definition.action,
                    reason="Permission not granted to user",
                    timestamp=timestamp,
                )

            return PermissionDecision(
                allowed=True,
                user_id=user_id,
                permission=permission,
                resource=definition.resource,
                action=definition.action,
                reason="Permission granted",
                timestamp=timestamp,
            )

    def is_allowed(
        self,
        user_id: str,
        permission: str,
    ) -> bool:
        return self.check(user_id, permission).allowed

    def get(self, name: str) -> Permission | None:
        name = self._normalize(name, "name")

        with self._lock:
            return self._permissions.get(name)

    def permissions_for_user(
        self,
        user_id: str,
    ) -> tuple[Permission, ...]:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            granted = self._user_permissions.get(
                user_id,
                set(),
            )

            return tuple(
                self._permissions[name]
                for name in sorted(granted)
                if name in self._permissions
            )

    def permissions_for_resource(
        self,
        resource: str,
    ) -> tuple[Permission, ...]:
        resource = self._normalize(resource, "resource")

        with self._lock:
            return tuple(
                permission
                for permission in self._permissions.values()
                if permission.resource == resource
            )

    def revoke_all_for_user(self, user_id: str) -> int:
        user_id = self._normalize(user_id, "user_id")

        with self._lock:
            permissions = self._user_permissions.pop(
                user_id,
                set(),
            )
            return len(permissions)

    def user_count(self) -> int:
        with self._lock:
            return len(self._user_permissions)

    def permission_count(self) -> int:
        with self._lock:
            return len(self._permissions)

    def granted_permission_count(self) -> int:
        with self._lock:
            return sum(
                len(permissions)
                for permissions in self._user_permissions.values()
            )

    def clear(self) -> None:
        with self._lock:
            self._permissions.clear()
            self._user_permissions.clear()