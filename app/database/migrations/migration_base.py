"""
ROBOMLM PLUS
Database Migration Base

Purpose:
    Defines the common contract for database migrations.

Design:
    - Migration execution is explicit.
    - No migration runs automatically on import.
    - Supports forward and rollback operations.
    - Keeps schema evolution versioned and auditable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


class MigrationError(Exception):
    """Base exception for migration failures."""


class MigrationValidationError(MigrationError):
    """Raised when migration metadata is invalid."""


@dataclass(frozen=True)
class MigrationInfo:
    """Immutable migration metadata."""

    version: str
    name: str
    description: str = ""
    dependencies: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not str(self.version).strip():
            raise MigrationValidationError(
                "Migration version cannot be empty."
            )

        if not str(self.name).strip():
            raise MigrationValidationError(
                "Migration name cannot be empty."
            )

        if not isinstance(
            self.dependencies,
            tuple,
        ):
            raise MigrationValidationError(
                "Migration dependencies must be a tuple."
            )


@dataclass
class MigrationContext:
    """
    Runtime context supplied to a migration.

    The context intentionally remains storage-agnostic so the
    migration layer can later support SQLite, PostgreSQL, or
    another database backend without changing migration contracts.
    """

    environment: str = "development"
    dry_run: bool = False
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Store migration execution metadata."""

        key = str(key).strip()

        if not key:
            raise ValueError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value


@dataclass
class MigrationResult:
    """Result of a migration operation."""

    version: str
    name: str
    operation: str
    success: bool
    started_at: datetime
    completed_at: datetime
    message: str = ""
    details: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def duration_seconds(self) -> float:
        """Return migration execution duration."""

        return (
            self.completed_at
            - self.started_at
        ).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "version": self.version,
            "name": self.name,
            "operation": self.operation,
            "success": self.success,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "message": self.message,
            "details": dict(self.details),
        }


class Migration(ABC):
    """
    Abstract base class for all ROBOMLM PLUS migrations.

    Every migration must define:
        - metadata
        - upgrade()
        - downgrade()
    """

    info: MigrationInfo

    @abstractmethod
    def upgrade(
        self,
        context: MigrationContext,
    ) -> None:
        """
        Apply the migration.

        Implementations must be deterministic and should not
        perform unrelated application operations.
        """

        raise NotImplementedError

    @abstractmethod
    def downgrade(
        self,
        context: MigrationContext,
    ) -> None:
        """
        Roll back the migration.

        Implementations must reverse only the changes introduced
        by the corresponding upgrade().
        """

        raise NotImplementedError

    def validate(self) -> None:
        """Validate migration metadata."""

        if not isinstance(
            self.info,
            MigrationInfo,
        ):
            raise MigrationValidationError(
                "Migration must define valid MigrationInfo."
            )

    def run_upgrade(
        self,
        context: Optional[MigrationContext] = None,
    ) -> MigrationResult:
        """Execute upgrade with lifecycle tracking."""

        self.validate()

        if context is None:
            context = MigrationContext()

        started_at = datetime.now(
            timezone.utc
        )

        try:
            self.upgrade(context)

            success = True
            message = (
                f"Migration {self.info.version} "
                "upgrade completed."
            )

        except Exception as exc:
            success = False
            message = (
                f"Migration {self.info.version} "
                f"upgrade failed: {exc}"
            )

        completed_at = datetime.now(
            timezone.utc
        )

        result = MigrationResult(
            version=self.info.version,
            name=self.info.name,
            operation="upgrade",
            success=success,
            started_at=started_at,
            completed_at=completed_at,
            message=message,
            details=dict(context.metadata),
        )

        if not success:
            raise MigrationError(
                result.message
            )

        return result

    def run_downgrade(
        self,
        context: Optional[MigrationContext] = None,
    ) -> MigrationResult:
        """Execute downgrade with lifecycle tracking."""

        self.validate()

        if context is None:
            context = MigrationContext()

        started_at = datetime.now(
            timezone.utc
        )

        try:
            self.downgrade(context)

            success = True
            message = (
                f"Migration {self.info.version} "
                "downgrade completed."
            )

        except Exception as exc:
            success = False
            message = (
                f"Migration {self.info.version} "
                f"downgrade failed: {exc}"
            )

        completed_at = datetime.now(
            timezone.utc
        )

        result = MigrationResult(
            version=self.info.version,
            name=self.info.name,
            operation="downgrade",
            success=success,
            started_at=started_at,
            completed_at=completed_at,
            message=message,
            details=dict(context.metadata),
        )

        if not success:
            raise MigrationError(
                result.message
            )

        return result


__all__ = [
    "MigrationError",
    "MigrationValidationError",
    "MigrationInfo",
    "MigrationContext",
    "MigrationResult",
    "Migration",
]