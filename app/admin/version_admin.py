from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class VersionRecord:
    """
    Immutable record describing a ROBOMLM version.
    """

    version: str
    status: str

    component: str = "ROBOMLM"

    released_at: datetime | None = None
    deprecated_at: datetime | None = None

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "status": self.status,
            "component": self.component,
            "released_at": (
                self.released_at.isoformat()
                if self.released_at is not None
                else None
            ),
            "deprecated_at": (
                self.deprecated_at.isoformat()
                if self.deprecated_at is not None
                else None
            ),
            "metadata": dict(self.metadata),
        }

    def is_active(self) -> bool:
        return self.status.upper() in {
            "ACTIVE",
            "CURRENT",
            "RELEASED",
        }

    def is_deprecated(self) -> bool:
        return self.status.upper() == "DEPRECATED"

    def is_valid(self) -> bool:
        if not self.version:
            return False

        if not self.status:
            return False

        if not self.component:
            return False

        if (
            self.deprecated_at is not None
            and self.released_at is not None
            and self.deprecated_at < self.released_at
        ):
            return False

        return True


class VersionAdmin:
    """
    Administrative version registry for ROBOMLM components.

    This class tracks version lifecycle and does not modify deployed
    runtime code by itself.
    """

    def __init__(
        self,
        *,
        component: str = "ROBOMLM",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if not component or not component.strip():
            raise ValueError("component must not be empty")

        self.component = component.strip()
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._versions: dict[str, VersionRecord] = {}
        self._current_version: str | None = None

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    @property
    def current_version(self) -> VersionRecord | None:
        if self._current_version is None:
            return None

        return self._versions.get(self._current_version)

    def register_version(
        self,
        *,
        version: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> VersionRecord:
        """
        Register a new version in REGISTERED state.
        """

        if not version or not version.strip():
            raise ValueError("version must not be empty")

        normalized_version = version.strip()

        if normalized_version in self._versions:
            raise ValueError(
                f"version already registered: {normalized_version}"
            )

        version_metadata = dict(self._metadata)
        version_metadata.update(metadata or {})

        record = VersionRecord(
            version=normalized_version,
            status="REGISTERED",
            component=self.component,
            metadata=version_metadata,
        )

        self._versions[normalized_version] = record

        return record

    def activate_version(
        self,
        version: str | VersionRecord,
    ) -> VersionRecord:
        """
        Mark a registered version as the current active version.
        """

        record = self._resolve_version(version)

        if not record.is_valid():
            raise ValueError("invalid version record")

        if record.is_deprecated():
            raise ValueError(
                "deprecated version cannot be activated"
            )

        if self._current_version is not None:
            current = self._versions[self._current_version]

            if current.version != record.version:
                self._versions[current.version] = VersionRecord(
                    version=current.version,
                    status="INACTIVE",
                    component=current.component,
                    released_at=current.released_at,
                    deprecated_at=current.deprecated_at,
                    metadata=dict(current.metadata),
                )

        activated = VersionRecord(
            version=record.version,
            status="ACTIVE",
            component=record.component,
            released_at=datetime.now(timezone.utc),
            deprecated_at=None,
            metadata=dict(record.metadata),
        )

        self._versions[activated.version] = activated
        self._current_version = activated.version

        return activated

    def deprecate_version(
        self,
        version: str | VersionRecord,
    ) -> VersionRecord:
        """
        Mark a version as deprecated.
        """

        record = self._resolve_version(version)

        if record.is_deprecated():
            raise ValueError("version is already deprecated")

        deprecated = VersionRecord(
            version=record.version,
            status="DEPRECATED",
            component=record.component,
            released_at=record.released_at,
            deprecated_at=datetime.now(timezone.utc),
            metadata=dict(record.metadata),
        )

        self._versions[deprecated.version] = deprecated

        if self._current_version == deprecated.version:
            self._current_version = None

        return deprecated

    def get_version(
        self,
        version: str,
    ) -> VersionRecord | None:
        """
        Retrieve a registered version.
        """

        return self._versions.get(version)

    def list_versions(self) -> tuple[VersionRecord, ...]:
        """
        Return all registered versions in registration order.
        """

        return tuple(self._versions.values())

    def status(self) -> dict[str, Any]:
        """
        Return current version registry state.
        """

        return {
            "component": self.component,
            "current_version": self._current_version,
            "version_count": len(self._versions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": dict(self._metadata),
        }

    def _resolve_version(
        self,
        version: str | VersionRecord,
    ) -> VersionRecord:
        if isinstance(version, VersionRecord):
            stored = self._versions.get(version.version)

            if stored is None:
                raise ValueError(
                    f"version is not registered: {version.version}"
                )

            return stored

        if not isinstance(version, str):
            raise TypeError(
                "version must be a string or VersionRecord"
            )

        normalized_version = version.strip()

        if not normalized_version:
            raise ValueError("version must not be empty")

        record = self._versions.get(normalized_version)

        if record is None:
            raise ValueError(
                f"version is not registered: {normalized_version}"
            )

        return record