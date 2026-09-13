"""
ROBOMLM PLUS
V6 Loader

Purpose:
    Controlled loader for the newly engineered V6 bridge components.

Rules:
    - V6 is newly engineered from the V4.5 + V5 foundation.
    - No legacy/v6_current path is assumed.
    - No V7+ dependency.
    - No trading decisions.
    - No execution.
"""

from __future__ import annotations

import importlib
import sys
import importlib.util
from dataclasses import dataclass, field, asdict
from pathlib import Path
from types import ModuleType
from typing import Any, Optional



V6_LOADER_VERSION = "2.0.0"
V6_LOADER_LAYER = "V6_LOADER"

APP_ROOT = Path(__file__).resolve().parents[1]
V6_BRIDGE_ROOT = APP_ROOT / "v6_bridge"


@dataclass
class V6LoadResult:
    success: bool
    status: str
    module_name: Optional[str] = None
    object_name: Optional[str] = None
    source: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class V6Loader:
    """
    Loader for the newly engineered V6 bridge package.
    """

    DEFAULT_MODULES = (
        "app.v6_bridge.v6_blackbox_bridge",
        "app.v6_bridge.v6_bridge",
        "app.v6_bridge.v6_compatibility",
        "app.v6_bridge.v6_mapper",
        "app.v6_bridge.v6_normalizer",
    )

    def __init__(
        self,
        v6_root: Optional[Path | str] = None,
    ) -> None:
        self._root = (
            Path(v6_root).resolve()
            if v6_root is not None
            else V6_BRIDGE_ROOT.resolve()
        )

        self._module_cache: dict[str, ModuleType] = {}
        self._object_cache: dict[str, Any] = {}

    @property
    def root_exists(self) -> bool:
        return self._root.exists() and self._root.is_dir()

    def get_root(self) -> Path:
        return self._root

    def discover_python_files(self) -> list[Path]:
        """
        Discover Python files inside the V6 bridge directory.
        """

        if not self.root_exists:
            return []

        return sorted(
            path
            for path in self._root.glob("*.py")
            if path.is_file()
        )

    def load_module(
        self,
        module_name: str,
        *,
        force_reload: bool = False,
    ) -> V6LoadResult:
        """
        Import a V6 module by its Python module name.
        """

        if not module_name:
            return V6LoadResult(
                success=False,
                status="INVALID",
                message="Module name is required.",
            )

        if not force_reload and module_name in self._module_cache:
            return V6LoadResult(
                success=True,
                status="CACHED",
                module_name=module_name,
                message="V6 module loaded from cache.",
            )

        try:
            module = importlib.import_module(module_name)

            if force_reload:
                module = importlib.reload(module)

            self._module_cache[module_name] = module

            return V6LoadResult(
                success=True,
                status="LOADED",
                module_name=module_name,
                source=getattr(module, "__file__", None),
                message="V6 module loaded successfully.",
            )

        except Exception as exc:
            return V6LoadResult(
                success=False,
                status="ERROR",
                module_name=module_name,
                message="V6 module loading failed.",
                error=f"{type(exc).__name__}: {exc}",
            )

    def load_file(
        self,
        file_path: Path | str,
        *,
        module_name: Optional[str] = None,
    ) -> V6LoadResult:
        """
        Load a Python file directly from the V6 bridge directory.

        Only files contained inside the configured V6 root are allowed.
        The module is registered in sys.modules before execution so that
        Python runtime introspection and dataclass handling work correctly.
        """

        path = Path(file_path).resolve()

        if not path.exists() or not path.is_file():
            return V6LoadResult(
                success=False,
                status="NOT_FOUND",
                source=str(path),
                message="V6 Python file does not exist.",
            )

        if path.suffix.lower() != ".py":
            return V6LoadResult(
                success=False,
                status="INVALID",
                source=str(path),
                message="Only Python files can be loaded.",
            )

        try:
            root = self._root.resolve()

            try:
                path.relative_to(root)
            except ValueError:
                return V6LoadResult(
                    success=False,
                    status="INVALID",
                    source=str(path),
                    message="File is outside the V6 bridge root.",
                    error="V6 root boundary violation.",
                )

            name = module_name or f"_robomlm_v6_{path.stem}"

            if name in self._module_cache:
                return V6LoadResult(
                    success=True,
                    status="CACHED",
                    module_name=name,
                    source=str(path),
                    message="V6 file loaded from cache.",
                )

            spec = importlib.util.spec_from_file_location(
                name,
                path,
            )

            if spec is None or spec.loader is None:
                return V6LoadResult(
                    success=False,
                    status="ERROR",
                    source=str(path),
                    message="Unable to create module specification.",
                )

            module = importlib.util.module_from_spec(spec)

            sys.modules[name] = module

            try:
                spec.loader.exec_module(module)
            except Exception:
                sys.modules.pop(name, None)
                raise

            self._module_cache[name] = module

            return V6LoadResult(
                success=True,
                status="LOADED",
                module_name=name,
                source=str(path),
                message="V6 file loaded successfully.",
            )

        except Exception as exc:
            return V6LoadResult(
                success=False,
                status="ERROR",
                source=str(path),
                message="V6 file loading failed.",
                error=f"{type(exc).__name__}: {exc}",
            )
    def inspect_v6_root(self) -> dict[str, Any]:
        """
        Return structural information about the V6 bridge directory.
        """

        files = self.discover_python_files()

        return {
            "root": str(self._root),
            "root_exists": self.root_exists,
            "python_file_count": len(files),
            "python_files": [str(path) for path in files],
        }

    def loaded_modules(self) -> list[str]:
        return sorted(self._module_cache.keys())

    def loaded_objects(self) -> list[str]:
        return sorted(self._object_cache.keys())

    def clear_cache(self) -> None:
        self._module_cache.clear()
        self._object_cache.clear()

    def health(self) -> dict[str, Any]:
        """
        Return structural health information.
        """

        return {
            "layer": V6_LOADER_LAYER,
            "version": V6_LOADER_VERSION,
            "status": "ready",
            "v6_root": str(self._root),
            "v6_root_exists": self.root_exists,
            "python_file_count": len(self.discover_python_files()),
            "loaded_module_count": len(self._module_cache),
            "loaded_object_count": len(self._object_cache),
            "legacy_v6_path_dependency": False,
            "v7_dependency": False,
        }


_default_loader = V6Loader()


def get_v6_loader() -> V6Loader:
    return _default_loader


def load_v6_module(
    module_name: str,
    *,
    force_reload: bool = False,
) -> V6LoadResult:
    return _default_loader.load_module(
        module_name,
        force_reload=force_reload,
    )


def load_v6_object(
    module_name: str,
    object_name: str,
    *,
    force_reload: bool = False,
) -> V6LoadResult:
    return _default_loader.load_object(
        module_name,
        object_name,
        force_reload=force_reload,
    )


def inspect_v6_root() -> dict[str, Any]:
    return _default_loader.inspect_v6_root()


def v6_loader_health() -> dict[str, Any]:
    return _default_loader.health()
