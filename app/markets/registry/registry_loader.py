"""
ROBOMLM PLUS
Registry Loader

Loads canonical market, venue, and related registry definitions into
in-memory registries.

This module is intentionally deterministic and side-effect limited:
it does not connect to brokers/exchanges, fetch market data, or execute
orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional

from .market_registry import (
    MarketDefinition,
    MarketRegistry,
    market_registry,
)


class RegistryLoaderError(Exception):
    """Base exception for registry-loader failures."""


class RegistryLoaderValidationError(
    RegistryLoaderError
):
    """Raised when registry-loader input is invalid."""


@dataclass(frozen=True)
class RegistryLoadResult:
    """Result of a registry loading operation."""

    registry: str
    loaded: int
    replaced: int
    skipped: int
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def success(self) -> bool:
        """Return whether loading completed without errors."""
        return not self.errors

    @property
    def total_processed(self) -> int:
        """Return the total number of processed definitions."""
        return (
            self.loaded
            + self.replaced
            + self.skipped
            + len(self.errors)
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the load result."""
        return {
            "registry": self.registry,
            "loaded": self.loaded,
            "replaced": self.replaced,
            "skipped": self.skipped,
            "errors": list(self.errors),
            "success": self.success,
            "total_processed": self.total_processed,
        }


class RegistryLoader:
    """
    Loader for canonical registry definitions.

    The loader supports explicit definitions supplied by the application,
    configuration, tests, or future research/deployment layers.
    """

    def __init__(
        self,
        *,
        market_registry_instance: Optional[
            MarketRegistry
        ] = None,
    ) -> None:
        self.market_registry = (
            market_registry_instance
            or market_registry
        )

    def load_markets(
        self,
        definitions: Iterable[
            MarketDefinition | Mapping[str, Any]
        ],
        *,
        replace: bool = False,
        strict: bool = True,
    ) -> RegistryLoadResult:
        """
        Load market definitions into the market registry.

        When strict=True, the first invalid or duplicate definition
        raises an exception.

        When strict=False, errors are collected and loading continues.
        """
        if definitions is None:
            raise RegistryLoaderValidationError(
                "definitions cannot be None"
            )

        items = list(definitions)

        loaded = 0
        replaced = 0
        skipped = 0
        errors: list[str] = []

        for raw_definition in items:
            try:
                definition = self._coerce_market(
                    raw_definition
                )

                existed = self.market_registry.exists(
                    definition.market
                )

                self.market_registry.register(
                    definition,
                    replace=replace,
                )

                if existed:
                    replaced += 1
                else:
                    loaded += 1

            except Exception as exc:
                if strict:
                    raise RegistryLoaderError(
                        f"Failed to load market definition: "
                        f"{exc}"
                    ) from exc

                errors.append(str(exc))
                skipped += 1

        return RegistryLoadResult(
            registry="market_registry",
            loaded=loaded,
            replaced=replaced,
            skipped=skipped,
            errors=tuple(errors),
        )

    def load_market(
        self,
        definition: MarketDefinition | Mapping[str, Any],
        *,
        replace: bool = False,
    ) -> MarketDefinition:
        """Load one market definition."""
        market = self._coerce_market(definition)

        return self.market_registry.register(
            market,
            replace=replace,
        )

    def load_from_mapping(
        self,
        data: Mapping[str, Any],
        *,
        replace: bool = False,
        strict: bool = True,
    ) -> RegistryLoadResult:
        """
        Load market definitions from a mapping.

        Supported forms:

        {
            "markets": [
                {...},
                {...}
            ]
        }

        or a direct mapping containing a single market definition.
        """
        if not isinstance(data, Mapping):
            raise RegistryLoaderValidationError(
                "data must be a mapping"
            )

        if "markets" in data:
            definitions = data["markets"]

            if definitions is None:
                definitions = []

            if isinstance(
                definitions,
                Mapping,
            ):
                definitions = [definitions]

            if not isinstance(
                definitions,
                Iterable,
            ) or isinstance(
                definitions,
                (str, bytes),
            ):
                raise RegistryLoaderValidationError(
                    "markets must be an iterable of definitions"
                )

            return self.load_markets(
                definitions,
                replace=replace,
                strict=strict,
            )

        return self.load_markets(
            [data],
            replace=replace,
            strict=strict,
        )

    def validate_markets(
        self,
        definitions: Iterable[
            MarketDefinition | Mapping[str, Any]
        ],
    ) -> RegistryLoadResult:
        """
        Validate market definitions without registering them.

        The returned result reports valid definitions as loaded and
        invalid definitions as skipped/errors.
        """
        if definitions is None:
            raise RegistryLoaderValidationError(
                "definitions cannot be None"
            )

        loaded = 0
        errors: list[str] = []
        skipped = 0

        for raw_definition in list(definitions):
            try:
                self._coerce_market(
                    raw_definition
                )
                loaded += 1
            except Exception as exc:
                skipped += 1
                errors.append(str(exc))

        return RegistryLoadResult(
            registry="market_registry",
            loaded=loaded,
            replaced=0,
            skipped=skipped,
            errors=tuple(errors),
        )

    def ensure_defaults(
        self,
        definitions: Iterable[
            MarketDefinition | Mapping[str, Any]
        ],
    ) -> RegistryLoadResult:
        """
        Register only markets that are not already present.

        Existing definitions remain unchanged.
        """
        if definitions is None:
            raise RegistryLoaderValidationError(
                "definitions cannot be None"
            )

        loaded = 0
        skipped = 0
        errors: list[str] = []

        for raw_definition in list(definitions):
            try:
                definition = self._coerce_market(
                    raw_definition
                )

                if self.market_registry.exists(
                    definition.market
                ):
                    skipped += 1
                    continue

                self.market_registry.register(
                    definition,
                    replace=False,
                )

                loaded += 1

            except Exception as exc:
                errors.append(str(exc))

        return RegistryLoadResult(
            registry="market_registry",
            loaded=loaded,
            replaced=0,
            skipped=skipped,
            errors=tuple(errors),
        )

    def export_markets(self) -> list[dict[str, Any]]:
        """Export all registered markets as dictionaries."""
        return [
            item.to_dict()
            for item in self.market_registry.list_all()
        ]

    def snapshot(self) -> dict[str, Any]:
        """Return a complete registry snapshot."""
        return {
            "market_registry": (
                self.market_registry.snapshot()
            ),
            "summary": self.market_registry.summary(),
        }

    def summary(self) -> dict[str, Any]:
        """Return loader and registry summary."""
        return {
            "loader": self.__class__.__name__,
            "market_registry": (
                self.market_registry.summary()
            ),
        }

    @staticmethod
    def _coerce_market(
        definition: MarketDefinition
        | Mapping[str, Any],
    ) -> MarketDefinition:
        """Convert supported input into MarketDefinition."""
        if isinstance(
            definition,
            MarketDefinition,
        ):
            return definition.copy()

        if isinstance(
            definition,
            Mapping,
        ):
            try:
                return MarketDefinition.from_mapping(
                    definition
                )
            except Exception as exc:
                raise RegistryLoaderValidationError(
                    f"Invalid market definition: {exc}"
                ) from exc

        raise RegistryLoaderValidationError(
            "market definition must be a "
            "MarketDefinition or mapping"
        )


registry_loader = RegistryLoader()


def load_markets(
    definitions: Iterable[
        MarketDefinition | Mapping[str, Any]
    ],
    *,
    replace: bool = False,
    strict: bool = True,
) -> RegistryLoadResult:
    """Load markets using the global registry loader."""
    return registry_loader.load_markets(
        definitions,
        replace=replace,
        strict=strict,
    )


def load_market(
    definition: MarketDefinition | Mapping[str, Any],
    *,
    replace: bool = False,
) -> MarketDefinition:
    """Load one market using the global registry loader."""
    return registry_loader.load_market(
        definition,
        replace=replace,
    )


def validate_markets(
    definitions: Iterable[
        MarketDefinition | Mapping[str, Any]
    ],
) -> RegistryLoadResult:
    """Validate market definitions without registering them."""
    return registry_loader.validate_markets(
        definitions
    )


def ensure_default_markets(
    definitions: Iterable[
        MarketDefinition | Mapping[str, Any]
    ],
) -> RegistryLoadResult:
    """Register missing markets without replacing existing ones."""
    return registry_loader.ensure_defaults(
        definitions
    )


__all__ = [
    "RegistryLoaderError",
    "RegistryLoaderValidationError",
    "RegistryLoadResult",
    "RegistryLoader",
    "registry_loader",
    "load_markets",
    "load_market",
    "validate_markets",
    "ensure_default_markets",
]