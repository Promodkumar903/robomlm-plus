"""
ROBOMLM PLUS
Migration 0001 - Initial Schema

Purpose:
    Define the initial ROBOMLM PLUS persistence schema contract.

Important:
    The current repository implementation uses JSONL persistence.
    Therefore this migration does not require a live SQL database.

    This migration establishes the canonical logical entities:
        - users
        - subscriptions
        - markets
        - evidence
        - decisions
        - trades
        - audits

    Future database backends can translate this logical schema into
    SQLite, PostgreSQL, or another supported database system.
"""

from __future__ import annotations

from app.database.migrations.migration_base import (
    Migration,
    MigrationContext,
    MigrationInfo,
)


class InitialSchemaMigration(Migration):
    """Initial ROBOMLM PLUS logical schema migration."""

    info = MigrationInfo(
        version="0001",
        name="initial_schema",
        description=(
            "Establish the initial ROBOMLM PLUS "
            "persistence schema contract."
        ),
    )

    SCHEMA_VERSION = "0001"

    ENTITIES = (
        "users",
        "subscriptions",
        "markets",
        "evidence",
        "decisions",
        "trades",
        "audits",
    )

    def upgrade(
        self,
        context: MigrationContext,
    ) -> None:
        """
        Register the initial logical schema.

        No external database is touched here.
        """

        context.set_metadata(
            "schema_version",
            self.SCHEMA_VERSION,
        )

        context.set_metadata(
            "entities",
            list(self.ENTITIES),
        )

        context.set_metadata(
            "storage_model",
            "repository_managed_jsonl",
        )

        context.set_metadata(
            "migration",
            self.info.name,
        )

    def downgrade(
        self,
        context: MigrationContext,
    ) -> None:
        """
        Remove the initial logical schema registration.

        No application data is deleted by this operation.
        """

        context.set_metadata(
            "schema_version",
            None,
        )

        context.set_metadata(
            "entities",
            [],
        )

        context.set_metadata(
            "storage_model",
            None,
        )

        context.set_metadata(
            "migration",
            self.info.name,
        )


initial_schema_migration = InitialSchemaMigration()


__all__ = [
    "InitialSchemaMigration",
    "initial_schema_migration",
]