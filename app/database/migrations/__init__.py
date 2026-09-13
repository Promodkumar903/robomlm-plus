"""
ROBOMLM PLUS
Database Migrations Package

Purpose:
    Migration package foundation for ROBOMLM PLUS.

Design:
    - Keeps database schema evolution isolated.
    - Does not execute migrations automatically on import.
    - Provides a clean package boundary for future migrations.
"""

from __future__ import annotations


MIGRATIONS_PACKAGE = "app.database.migrations"


__all__ = [
    "MIGRATIONS_PACKAGE",
]