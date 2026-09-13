"""
ROBOMLM PLUS
Database Migration Manager

Purpose:
    Coordinate migration discovery, validation, execution,
    rollback, and migration state tracking.

Design:
    - Explicit execution only.
    - No automatic migration on import.
    - Migration ordering is version-based.
    - Duplicate versions are rejected.
    - Migration state is persisted separately from application data.
"""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Iterable, Optional

from app.database.migrations.migration_base import (
    Migration,
    MigrationContext,
    MigrationError,
    MigrationResult,
)


class MigrationManagerError(MigrationError):
    """Base exception for migration manager failures."""


class DuplicateMigrationError(MigrationManagerError):
    """Raised when duplicate migration versions are registered."""


class MigrationNotFoundError(MigrationManagerError):
    """Raised when a migration version cannot be found."""


class MigrationManager:
    """Manage registered database migrations."""

    STATE_FILE_NAME = "migration_state.json"

    def __init__(
        self,
        storage_dir: Optional[str | Path] = None,
    ) -> None:
        if storage_dir is None:
            storage_dir = (
                Path(__file__).resolve().parents[3]
                / "robomlm_data"
                / "database"
            )

        self.storage_dir = Path(storage_dir)
        self.state_file = (
            self.storage_dir
            / self.STATE_FILE_NAME
        )

        self._lock = RLock()
        self._migrations: dict[str, Migration] = {}

        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """Create migration state storage."""

        try:
            self.storage_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            if not self.state_file.exists():
                self._write_state(
                    {
                        "applied": [],
                        "history": [],
                    }
                )

        except OSError as exc:
            raise MigrationManagerError(
                f"Unable to initialize migration storage: {exc}"
            ) from exc

    def _read_state(self) -> dict:
        """Read migration state."""

        if not self.state_file.exists():
            return {
                "applied": [],
                "history": [],
            }

        try:
            with self.state_file.open(
                "r",
                encoding="utf-8",
            ) as handle:
                payload = json.load(handle)

            if not isinstance(payload, dict):
                raise MigrationManagerError(
                    "Migration state must be a JSON object."
                )

            payload.setdefault(
                "applied",
                [],
            )
            payload.setdefault(
                "history",
                [],
            )

            return payload

        except json.JSONDecodeError as exc:
            raise MigrationManagerError(
                f"Invalid migration state: {exc}"
            ) from exc

        except OSError as exc:
            raise MigrationManagerError(
                f"Unable to read migration state: {exc}"
            ) from exc

    def _write_state(
        self,
        state: dict,
    ) -> None:
        """Persist migration state."""

        temp_file = (
            self.storage_dir
            / f"{self.STATE_FILE_NAME}.tmp"
        )

        try:
            with temp_file.open(
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(
                    state,
                    handle,
                    ensure_ascii=False,
                    indent=2,
                )

            temp_file.replace(
                self.state_file
            )

        except OSError as exc:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except OSError:
                pass

            raise MigrationManagerError(
                f"Unable to write migration state: {exc}"
            ) from exc

    def register(
        self,
        migration: Migration,
    ) -> None:
        """Register a migration."""

        if not isinstance(
            migration,
            Migration,
        ):
            raise TypeError(
                "migration must inherit from Migration."
            )

        migration.validate()

        version = migration.info.version

        with self._lock:
            if version in self._migrations:
                raise DuplicateMigrationError(
                    f"Migration already registered: {version}"
                )

            self._migrations[version] = migration

    def register_many(
        self,
        migrations: Iterable[Migration],
    ) -> None:
        """Register multiple migrations."""

        for migration in migrations:
            self.register(migration)

    def unregister(
        self,
        version: str,
    ) -> bool:
        """Remove a registered migration."""

        version = str(version).strip()

        with self._lock:
            if version not in self._migrations:
                return False

            del self._migrations[version]
            return True

    def get(
        self,
        version: str,
    ) -> Migration:
        """Return a registered migration."""

        version = str(version).strip()

        with self._lock:
            migration = self._migrations.get(
                version
            )

        if migration is None:
            raise MigrationNotFoundError(
                f"Migration not registered: {version}"
            )

        return migration

    def list_registered(
        self,
    ) -> list[Migration]:
        """Return registered migrations in version order."""

        with self._lock:
            migrations = list(
                self._migrations.values()
            )

        return sorted(
            migrations,
            key=lambda migration: migration.info.version,
        )

    def registered_versions(
        self,
    ) -> list[str]:
        """Return registered migration versions."""

        return [
            migration.info.version
            for migration in self.list_registered()
        ]

    def applied_versions(
        self,
    ) -> list[str]:
        """Return successfully applied migration versions."""

        with self._lock:
            state = self._read_state()

        return list(
            state.get("applied", [])
        )

    def pending_migrations(
        self,
    ) -> list[Migration]:
        """Return registered but unapplied migrations."""

        applied = set(
            self.applied_versions()
        )

        return [
            migration
            for migration in self.list_registered()
            if migration.info.version not in applied
        ]

    def is_applied(
        self,
        version: str,
    ) -> bool:
        """Check whether a migration is applied."""

        version = str(version).strip()

        return version in set(
            self.applied_versions()
        )

    def _record_success(
        self,
        result: MigrationResult,
    ) -> None:
        """Record a successful migration."""

        state = self._read_state()

        applied = list(
            state.get("applied", [])
        )

        if result.version not in applied:
            applied.append(
                result.version
            )

        history = list(
            state.get("history", [])
        )

        history.append(
            result.to_dict()
        )

        state["applied"] = applied
        state["history"] = history

        self._write_state(state)

    def _record_rollback(
        self,
        result: MigrationResult,
    ) -> None:
        """Record a successful rollback."""

        state = self._read_state()

        applied = [
            version
            for version in state.get(
                "applied",
                [],
            )
            if version != result.version
        ]

        history = list(
            state.get("history", [])
        )

        history.append(
            result.to_dict()
        )

        state["applied"] = applied
        state["history"] = history

        self._write_state(state)

    def upgrade_one(
        self,
        version: str,
        context: Optional[MigrationContext] = None,
    ) -> MigrationResult:
        """Apply one migration."""

        migration = self.get(version)

        with self._lock:
            if self.is_applied(version):
                raise MigrationManagerError(
                    f"Migration already applied: {version}"
                )

            result = migration.run_upgrade(
                context
            )

            self._record_success(
                result
            )

            return result

    def upgrade_pending(
        self,
        context: Optional[MigrationContext] = None,
    ) -> list[MigrationResult]:
        """Apply all pending migrations in order."""

        results: list[MigrationResult] = []

        for migration in self.pending_migrations():
            result = self.upgrade_one(
                migration.info.version,
                context,
            )
            results.append(result)

        return results

    def downgrade_one(
        self,
        version: str,
        context: Optional[MigrationContext] = None,
    ) -> MigrationResult:
        """Roll back one applied migration."""

        migration = self.get(version)

        with self._lock:
            if not self.is_applied(version):
                raise MigrationManagerError(
                    f"Migration is not applied: {version}"
                )

            result = migration.run_downgrade(
                context
            )

            self._record_rollback(
                result
            )

            return result

    def downgrade_latest(
        self,
        context: Optional[MigrationContext] = None,
    ) -> MigrationResult:
        """Roll back the latest applied migration."""

        applied = self.applied_versions()

        if not applied:
            raise MigrationManagerError(
                "No applied migrations available for rollback."
            )

        latest_version = applied[-1]

        return self.downgrade_one(
            latest_version,
            context,
        )

    def migration_status(self) -> dict:
        """Return migration status summary."""

        registered = self.registered_versions()
        applied = self.applied_versions()
        pending = [
            version
            for version in registered
            if version not in applied
        ]

        return {
            "registered_count": len(registered),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "registered_versions": registered,
            "applied_versions": applied,
            "pending_versions": pending,
        }

    def history(self) -> list[dict]:
        """Return migration execution history."""

        with self._lock:
            state = self._read_state()

        return list(
            state.get("history", [])
        )

    def validate_registry(self) -> None:
        """Validate the registered migration chain."""

        migrations = self.list_registered()

        seen: set[str] = set()

        for migration in migrations:
            migration.validate()

            version = migration.info.version

            if version in seen:
                raise DuplicateMigrationError(
                    f"Duplicate migration version: {version}"
                )

            seen.add(version)

            for dependency in (
                migration.info.dependencies
            ):
                if dependency not in self._migrations:
                    raise MigrationManagerError(
                        f"Missing dependency "
                        f"{dependency} for migration "
                        f"{version}"
                    )

    def clear_state(self) -> None:
        """
        Clear migration state.

        This does not execute downgrade operations and does not
        modify application schema. It is intended for controlled
        administrative/test environments only.
        """

        with self._lock:
            self._write_state(
                {
                    "applied": [],
                    "history": [],
                }
            )


migration_manager = MigrationManager()


def get_migration_manager() -> MigrationManager:
    """Return the global migration manager."""

    return migration_manager


__all__ = [
    "MigrationManagerError",
    "DuplicateMigrationError",
    "MigrationNotFoundError",
    "MigrationManager",
    "migration_manager",
    "get_migration_manager",
]