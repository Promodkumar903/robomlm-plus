"""
ROBOMLM PLUS
Database Package

Purpose:
    Central database-layer package exports.

Design:
    - Models remain responsible for data structures.
    - Repositories remain responsible for persistence.
    - Migrations remain responsible for schema evolution.
    - No database connection is opened on package import.
"""

from __future__ import annotations


DATABASE_PACKAGE = "app.database"


__all__ = [
    "DATABASE_PACKAGE",
]