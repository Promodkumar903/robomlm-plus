"""
ROBOMLM PLUS
Startup Folder Manager

Purpose:
    Create and validate the runtime directories required by ROBOMLM PLUS.

Design:
    - Idempotent: safe to run multiple times.
    - Does not delete user data.
    - Does not overwrite existing files.
    - Centralizes runtime folder preparation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


class FolderManagerError(RuntimeError):
    """Raised when required runtime folders cannot be prepared."""


@dataclass(frozen=True)
class FolderResult:
    """Result for a single folder operation."""

    name: str
    path: Path
    existed_before: bool
    created: bool
    writable: bool
    error: Optional[str] = None


class FolderManager:
    """
    Manage ROBOMLM PLUS runtime directories.

    The manager only creates missing directories.
    It never deletes or clears existing runtime data.
    """

    DEFAULT_RELATIVE_FOLDERS = (
        "robomlm_data",
        "robomlm_data/backups",
        "robomlm_data/blackbox",
        "robomlm_data/decisions",
        "robomlm_data/evidence",
        "robomlm_data/memory",
        "robomlm_data/outcomes",
        "robomlm_data/cache",
        "robomlm_data/exports",
        "robomlm_data/logs",
    )

    def __init__(
        self,
        project_root: Optional[Path | str] = None,
        relative_folders: Optional[Iterable[str]] = None,
    ) -> None:
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else self._detect_project_root()
        )

        self.relative_folders = tuple(
            relative_folders
            if relative_folders is not None
            else self.DEFAULT_RELATIVE_FOLDERS
        )

    @staticmethod
    def _detect_project_root() -> Path:
        """
        Detect project root from this file.

        folder_manager.py
            startup/
            core/
            app/
            ROBOMLM_PLUS/
        """

        return Path(__file__).resolve().parents[3]

    def folder_path(self, relative_path: str) -> Path:
        """Return an absolute path for a configured relative folder."""

        relative = Path(relative_path)

        if relative.is_absolute():
            raise FolderManagerError(
                f"Absolute runtime folder paths are not allowed: {relative}"
            )

        resolved = (self.project_root / relative).resolve()

        try:
            resolved.relative_to(self.project_root)
        except ValueError as exc:
            raise FolderManagerError(
                f"Folder path escapes project root: {relative_path}"
            ) from exc

        return resolved

    @staticmethod
    def _is_writable(path: Path) -> bool:
        """Check whether a directory is writable."""

        try:
            test_file = path / ".robomlm_write_test"

            test_file.write_text(
                "ROBOMLM_PLUS_WRITE_TEST",
                encoding="utf-8",
            )

            test_file.unlink(missing_ok=True)

            return True

        except Exception:
            return False

    def ensure_folder(
        self,
        name: str,
        relative_path: str,
    ) -> FolderResult:
        """Create one folder if necessary and validate write access."""

        path = self.folder_path(relative_path)
        existed_before = path.exists()
        created = False

        try:
            if path.exists() and not path.is_dir():
                return FolderResult(
                    name=name,
                    path=path,
                    existed_before=existed_before,
                    created=False,
                    writable=False,
                    error="Path exists but is not a directory",
                )

            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created = True

            writable = self._is_writable(path)

            return FolderResult(
                name=name,
                path=path,
                existed_before=existed_before,
                created=created,
                writable=writable,
                error=None if writable else "Directory is not writable",
            )

        except Exception as exc:
            return FolderResult(
                name=name,
                path=path,
                existed_before=existed_before,
                created=created,
                writable=False,
                error=f"{type(exc).__name__}: {exc}",
            )

    def ensure_all(self) -> list[FolderResult]:
        """Create and validate all configured runtime folders."""

        results: list[FolderResult] = []

        for relative_path in self.relative_folders:
            name = Path(relative_path).name
            results.append(
                self.ensure_folder(
                    name=name,
                    relative_path=relative_path,
                )
            )

        return results

    def validate(self) -> list[FolderResult]:
        """
        Ensure all folders are ready.

        Raises FolderManagerError if any folder is unavailable
        or not writable.
        """

        results = self.ensure_all()

        failures = [
            result
            for result in results
            if not result.writable
        ]

        if failures:
            details = "; ".join(
                f"{result.name}: {result.error}"
                for result in failures
            )

            raise FolderManagerError(
                f"Runtime folder validation failed: {details}"
            )

        return results

    def summary(self) -> dict:
        """Return folder configuration summary."""

        return {
            "project_root": str(self.project_root),
            "folders": [
                str(self.folder_path(relative_path))
                for relative_path in self.relative_folders
            ],
            "folder_count": len(self.relative_folders),
        }


folder_manager = FolderManager()


def ensure_runtime_folders() -> list[FolderResult]:
    """Convenience function to prepare runtime folders."""
    return folder_manager.ensure_all()


def validate_runtime_folders() -> list[FolderResult]:
    """Convenience function to validate runtime folders."""
    return folder_manager.validate()


__all__ = [
    "FolderManagerError",
    "FolderResult",
    "FolderManager",
    "folder_manager",
    "ensure_runtime_folders",
    "validate_runtime_folders",
]