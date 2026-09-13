# ============================================================
# STRATEGY REGISTRY — PART 1
# Core Strategy Definition + Basic Registry
# ============================================================

"""
ROBOMLM Strategy Registry
=========================

Purpose
-------
Central registration layer for ROBOMLM strategies.

The Strategy Registry defines WHAT a strategy is and stores
controlled strategy metadata.

It does NOT:
    - generate trading signals
    - calculate entry/exit levels
    - calculate indicators
    - contain trading formulas
    - make market decisions
    - calculate position size
    - execute trades
    - authorize users
    - enforce subscriptions
    - perform CAS decisions
    - perform risk decisions

Architectural boundary
----------------------

    Strategy Registry
            |
            v
    Strategy Identity + Metadata + Lifecycle
            |
            v
    Strategy Engine / Decision Layer
            |
            v
    Risk / CAS / Execution

The registry is a governance/discovery layer, not a strategy
intelligence engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional, Tuple


# ============================================================
# 1.1 — REGISTRY CONSTANTS
# ============================================================

REGISTRY_NAME = "strategy_registry"

REGISTRY_VERSION = "1.0.0"

VALID_STRATEGY_STATUSES = {
    "registered",
    "active",
    "disabled",
    "deprecated",
}


# ============================================================
# 1.2 — REGISTRY EXCEPTIONS
# ============================================================

class StrategyRegistryError(Exception):
    """Base exception for Strategy Registry errors."""


class StrategyAlreadyRegisteredError(
    StrategyRegistryError
):
    """Raised when a strategy ID already exists."""


class StrategyNotFoundError(
    StrategyRegistryError
):
    """Raised when a requested strategy does not exist."""


class InvalidStrategyDefinitionError(
    StrategyRegistryError
):
    """Raised when a strategy definition is invalid."""


class StrategyStateError(
    StrategyRegistryError
):
    """Raised when an invalid strategy lifecycle transition occurs."""


# ============================================================
# 1.3 — STRATEGY DEFINITION
# ============================================================

@dataclass(frozen=True)
class StrategyDefinition:
    """
    Immutable definition of a registered strategy.

    This object contains metadata only.

    Trading intelligence must remain outside this registry.
    """

    strategy_id: str

    name: str

    version: str

    domain: str

    layer: str

    description: str = ""

    status: str = "registered"

    owner: str = ""

    dependencies: Tuple[str, ...] = field(
        default_factory=tuple
    )

    tags: Tuple[str, ...] = field(
        default_factory=tuple
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


# ============================================================
# 1.4 — STRATEGY REGISTRY
# ============================================================

class StrategyRegistry:
    """
    Central registry for ROBOMLM strategy definitions.

    Responsibilities:
        - register strategies
        - retrieve strategies
        - check existence
        - list strategies
        - filter strategies
        - validate strategy definitions

    Non-responsibilities:
        - signal generation
        - formula execution
        - market prediction
        - trade execution
        - risk calculation
        - CAS authorization
    """

    def __init__(self) -> None:
        self._strategies: Dict[
            str,
            StrategyDefinition,
        ] = {}


    # ========================================================
    # 1.5 — REGISTER
    # ========================================================

    def register(
        self,
        definition: StrategyDefinition,
    ) -> StrategyDefinition:
        """
        Register a new strategy.
        """

        self._validate_definition(
            definition
        )

        strategy_id = (
            self._normalize_strategy_id(
                definition.strategy_id
            )
        )

        if strategy_id in self._strategies:
            raise StrategyAlreadyRegisteredError(
                f"Strategy already registered: "
                f"{strategy_id}"
            )

        self._strategies[strategy_id] = (
            definition
        )

        return definition


    # ========================================================
    # 1.6 — REGISTER MANY
    # ========================================================

    def register_many(
        self,
        definitions: Iterable[
            StrategyDefinition
        ],
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Register multiple strategies.

        Validation is performed before mutation so invalid
        definitions do not partially enter the registry.
        """

        definitions = tuple(
            definitions
        )

        for definition in definitions:
            self._validate_definition(
                definition
            )

        normalized_ids = []

        for definition in definitions:
            strategy_id = (
                self._normalize_strategy_id(
                    definition.strategy_id
                )
            )

            if strategy_id in normalized_ids:
                raise StrategyAlreadyRegisteredError(
                    f"Duplicate strategy in batch: "
                    f"{strategy_id}"
                )

            normalized_ids.append(
                strategy_id
            )

            if strategy_id in self._strategies:
                raise StrategyAlreadyRegisteredError(
                    f"Strategy already registered: "
                    f"{strategy_id}"
                )

        for definition in definitions:
            strategy_id = (
                self._normalize_strategy_id(
                    definition.strategy_id
                )
            )

            self._strategies[
                strategy_id
            ] = definition

        return definitions


    # ========================================================
    # 1.7 — GET
    # ========================================================

    def get(
        self,
        strategy_id: str,
    ) -> StrategyDefinition:
        """
        Retrieve one strategy by ID.
        """

        normalized_id = (
            self._normalize_strategy_id(
                strategy_id
            )
        )

        try:
            return self._strategies[
                normalized_id
            ]

        except KeyError as exc:
            raise StrategyNotFoundError(
                f"Strategy not found: "
                f"{normalized_id}"
            ) from exc


    # ========================================================
    # 1.8 — EXISTS
    # ========================================================

    def exists(
        self,
        strategy_id: str,
    ) -> bool:
        """
        Check whether a strategy is registered.
        """

        normalized_id = (
            self._normalize_strategy_id(
                strategy_id
            )
        )

        return (
            normalized_id
            in self._strategies
        )


    # ========================================================
    # 1.9 — COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return number of registered strategies.
        """

        return len(
            self._strategies
        )


    # ========================================================
    # 1.10 — LIST ALL
    # ========================================================

    def list_all(
        self,
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Return all registered strategies.
        """

        return tuple(
            self._strategies.values()
        )


    # ========================================================
    # 1.11 — LIST BY DOMAIN
    # ========================================================

    def list_by_domain(
        self,
        domain: str,
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Return strategies belonging to a domain.
        """

        normalized_domain = (
            self._normalize_text(
                domain
            )
        )

        return tuple(
            strategy
            for strategy in self._strategies.values()
            if strategy.domain
            == normalized_domain
        )


    # ========================================================
    # 1.12 — LIST BY LAYER
    # ========================================================

    def list_by_layer(
        self,
        layer: str,
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Return strategies belonging to a specific
        architecture layer.
        """

        normalized_layer = (
            self._normalize_text(
                layer
            )
        )

        return tuple(
            strategy
            for strategy in self._strategies.values()
            if strategy.layer
            == normalized_layer
        )


    # ========================================================
    # 1.13 — LIST BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Return strategies with a given lifecycle status.
        """

        normalized_status = (
            self._normalize_text(
                status
            )
        )

        return tuple(
            strategy
            for strategy in self._strategies.values()
            if strategy.status
            == normalized_status
        )


    # ========================================================
    # 1.14 — LIST BY TAG
    # ========================================================

    def list_by_tag(
        self,
        tag: str,
    ) -> Tuple[
        StrategyDefinition,
        ...,
    ]:
        """
        Return strategies containing a given tag.
        """

        normalized_tag = (
            self._normalize_text(
                tag
            )
        )

        return tuple(
            strategy
            for strategy in self._strategies.values()
            if normalized_tag
            in strategy.tags
        )


    # ========================================================
    # 1.15 — VALIDATE DEFINITION
    # ========================================================

    def _validate_definition(
        self,
        definition: StrategyDefinition,
    ) -> None:
        """
        Validate structural integrity of a strategy definition.

        This validation intentionally does NOT validate
        trading formulas or strategy intelligence.
        """

        if not isinstance(
            definition,
            StrategyDefinition,
        ):
            raise InvalidStrategyDefinitionError(
                "Expected StrategyDefinition"
            )

        strategy_id = (
            self._normalize_strategy_id(
                definition.strategy_id
            )
        )

        if not strategy_id:
            raise InvalidStrategyDefinitionError(
                "strategy_id cannot be empty"
            )

        name = self._normalize_text(
            definition.name
        )

        if not name:
            raise InvalidStrategyDefinitionError(
                "Strategy name cannot be empty"
            )

        version = self._normalize_text(
            definition.version
        )

        if not version:
            raise InvalidStrategyDefinitionError(
                "Strategy version cannot be empty"
            )

        domain = self._normalize_text(
            definition.domain
        )

        if not domain:
            raise InvalidStrategyDefinitionError(
                "Strategy domain cannot be empty"
            )

        layer = self._normalize_text(
            definition.layer
        )

        if not layer:
            raise InvalidStrategyDefinitionError(
                "Strategy layer cannot be empty"
            )

        status = self._normalize_text(
            definition.status
        )

        if status not in VALID_STRATEGY_STATUSES:
            raise InvalidStrategyDefinitionError(
                f"Invalid strategy status: "
                f"{definition.status}"
            )

        if not isinstance(
            definition.dependencies,
            tuple,
        ):
            raise InvalidStrategyDefinitionError(
                "dependencies must be a tuple"
            )

        if not isinstance(
            definition.tags,
            tuple,
        ):
            raise InvalidStrategyDefinitionError(
                "tags must be a tuple"
            )

        if not isinstance(
            definition.metadata,
            dict,
        ):
            raise InvalidStrategyDefinitionError(
                "metadata must be a dictionary"
            )


    # ========================================================
    # 1.16 — NORMALIZE STRATEGY ID
    # ========================================================

    @staticmethod
    def _normalize_strategy_id(
        strategy_id: str,
    ) -> str:
        """
        Normalize strategy identifier.
        """

        if strategy_id is None:
            return ""

        return str(
            strategy_id
        ).strip().lower()


    # ========================================================
    # 1.17 — NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def _normalize_text(
        value: Any,
    ) -> str:
        """
        Normalize textual metadata.
        """

        if value is None:
            return ""

        return str(
            value
        ).strip()


# ============================================================
# 1.18 — GLOBAL STRATEGY REGISTRY
# ============================================================

strategy_registry = StrategyRegistry()


# ============================================================
# 1.19 — CONVENIENCE REGISTRATION HELPER
# ============================================================

def register_strategy(
    strategy_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    dependencies: Optional[
        Iterable[str]
    ] = None,
    tags: Optional[
        Iterable[str]
    ] = None,
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> StrategyDefinition:
    """
    Convenience helper for creating and registering a strategy.

    This helper creates metadata only. It does not implement
    strategy logic.
    """

    definition = StrategyDefinition(
        strategy_id=strategy_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        status=status,
        owner=owner,
        dependencies=tuple(
            dependencies
            if dependencies is not None
            else ()
        ),
        tags=tuple(
            tags
            if tags is not None
            else ()
        ),
        metadata=dict(
            metadata
            if metadata is not None
            else {}
        ),
    )

    return strategy_registry.register(
        definition
    )


# ============================================================
# END OF STRATEGY REGISTRY — PART 1
# ============================================================
# ============================================================
# STRATEGY REGISTRY — PART 2
# Lifecycle + Conflict + Dependency + Index Governance
# ============================================================


# ============================================================
# 2.1 — PART 2 EXCEPTIONS
# ============================================================

class StrategyRegistrationConflictError(
    StrategyRegistryError
):
    """Raised when a strategy registration conflicts with
    an existing definition.
    """


class StrategyUnregisterError(
    StrategyRegistryError
):
    """Raised when a strategy cannot be unregistered safely."""


class StrategyDependencyError(
    StrategyRegistryError
):
    """Raised when strategy dependencies are invalid."""


class StrategyVersionError(
    StrategyRegistryError
):
    """Raised when strategy version requirements are invalid."""


# ============================================================
# 2.2 — LIFECYCLE: SET STATUS
# ============================================================

def _strategy_set_status(
    self,
    strategy_id: str,
    status: str,
) -> StrategyDefinition:
    """
    Change lifecycle status of a registered strategy.

    Only registry lifecycle state is changed here.
    No strategy intelligence is executed.
    """

    normalized_id = (
        self._normalize_strategy_id(
            strategy_id
        )
    )

    normalized_status = (
        self._normalize_text(
            status
        ).lower()
    )

    if normalized_status not in VALID_STRATEGY_STATUSES:
        raise StrategyStateError(
            f"Invalid strategy status: "
            f"{status}"
        )

    strategy = self.get(
        normalized_id
    )

    updated = StrategyDefinition(
        strategy_id=strategy.strategy_id,
        name=strategy.name,
        version=strategy.version,
        domain=strategy.domain,
        layer=strategy.layer,
        description=strategy.description,
        status=normalized_status,
        owner=strategy.owner,
        dependencies=strategy.dependencies,
        tags=strategy.tags,
        metadata=dict(strategy.metadata),
        registered_at=strategy.registered_at,
    )

    self._strategies[
        normalized_id
    ] = updated

    return updated


PlanRegistry = PlanRegistry  # no-op guard against accidental name reuse


StrategyRegistry.set_status = (
    _strategy_set_status
)


# ============================================================
# 2.3 — ACTIVATE
# ============================================================

def _strategy_activate(
    self,
    strategy_id: str,
) -> StrategyDefinition:
    """
    Mark a strategy as active.
    """

    return self.set_status(
        strategy_id,
        "active",
    )


StrategyRegistry.activate = (
    _strategy_activate
)


# ============================================================
# 2.4 — DISABLE
# ============================================================

def _strategy_disable(
    self,
    strategy_id: str,
) -> StrategyDefinition:
    """
    Disable a registered strategy.
    """

    return self.set_status(
        strategy_id,
        "disabled",
    )


StrategyRegistry.disable = (
    _strategy_disable
)


# ============================================================
# 2.5 — DEPRECATE
# ============================================================

def _strategy_deprecate(
    self,
    strategy_id: str,
) -> StrategyDefinition:
    """
    Mark a strategy as deprecated.
    """

    return self.set_status(
        strategy_id,
        "deprecated",
    )


StrategyRegistry.deprecate = (
    _strategy_deprecate
)


# ============================================================
# 2.6 — CONFLICT CHECK
# ============================================================

def _strategy_check_conflict(
    self,
    definition: StrategyDefinition,
) -> bool:
    """
    Return True when the supplied definition conflicts
    with an existing strategy ID.
    """

    self._validate_definition(
        definition
    )

    strategy_id = (
        self._normalize_strategy_id(
            definition.strategy_id
        )
    )

    if strategy_id not in self._strategies:
        return False

    existing = self._strategies[
        strategy_id
    ]

    return existing != definition


StrategyRegistry.check_conflict = (
    _strategy_check_conflict
)


# ============================================================
# 2.7 — SAFE REGISTER
# ============================================================

def _strategy_register_safe(
    self,
    definition: StrategyDefinition,
) -> StrategyDefinition:
    """
    Register a strategy only when it does not conflict
    with an existing definition.
    """

    self._validate_definition(
        definition
    )

    strategy_id = (
        self._normalize_strategy_id(
            definition.strategy_id
        )
    )

    if self.exists(strategy_id):

        existing = self.get(
            strategy_id
        )

        if existing == definition:
            return existing

        raise StrategyRegistrationConflictError(
            f"Strategy registration conflict: "
            f"{strategy_id}"
        )

    return self.register(
        definition
    )


StrategyRegistry.register_safe = (
    _strategy_register_safe
)


# ============================================================
# 2.8 — REPLACE
# ============================================================

def _strategy_replace(
    self,
    definition: StrategyDefinition,
) -> StrategyDefinition:
    """
    Replace an existing strategy definition.

    Replacement is explicit and controlled.
    """

    self._validate_definition(
        definition
    )

    strategy_id = (
        self._normalize_strategy_id(
            definition.strategy_id
        )
    )

    if strategy_id not in self._strategies:
        raise StrategyNotFoundError(
            f"Cannot replace missing strategy: "
            f"{strategy_id}"
        )

    self._strategies[
        strategy_id
    ] = definition

    return definition


StrategyRegistry.replace = (
    _strategy_replace
)


# ============================================================
# 2.9 — STRATEGY IDS
# ============================================================

def _strategy_ids(
    self,
) -> Tuple[str, ...]:
    """
    Return all registered strategy IDs.
    """

    return tuple(
        self._strategies.keys()
    )


StrategyRegistry.strategy_ids = (
    _strategy_ids
)


# ============================================================
# 2.10 — ACTIVE STRATEGIES
# ============================================================

def _strategy_active(
    self,
) -> Tuple[StrategyDefinition, ...]:
    """
    Return all strategies currently marked active.
    """

    return tuple(
        strategy
        for strategy in self._strategies.values()
        if strategy.status == "active"
    )


StrategyRegistry.active_strategies = (
    _strategy_active
)


# ============================================================
# 2.11 — DOMAIN INDEX
# ============================================================

def _strategy_domain_index(
    self,
) -> Dict[str, Tuple[str, ...]]:
    """
    Build domain -> strategy IDs index.
    """

    index: Dict[
        str,
        list,
    ] = {}

    for strategy in self._strategies.values():

        domain = strategy.domain

        index.setdefault(
            domain,
            [],
        ).append(
            strategy.strategy_id
        )

    return {
        domain: tuple(ids)
        for domain, ids in index.items()
    }


StrategyRegistry.domain_index = (
    _strategy_domain_index
)


# ============================================================
# 2.12 — LAYER INDEX
# ============================================================

def _strategy_layer_index(
    self,
) -> Dict[str, Tuple[str, ...]]:
    """
    Build layer -> strategy IDs index.
    """

    index: Dict[
        str,
        list,
    ] = {}

    for strategy in self._strategies.values():

        layer = strategy.layer

        index.setdefault(
            layer,
            [],
        ).append(
            strategy.strategy_id
        )

    return {
        layer: tuple(ids)
        for layer, ids in index.items()
    }


StrategyRegistry.layer_index = (
    _strategy_layer_index
)


# ============================================================
# 2.13 — STATUS INDEX
# ============================================================

def _strategy_status_index(
    self,
) -> Dict[str, Tuple[str, ...]]:
    """
    Build lifecycle status -> strategy IDs index.
    """

    index: Dict[
        str,
        list,
    ] = {}

    for strategy in self._strategies.values():

        status = strategy.status

        index.setdefault(
            status,
            [],
        ).append(
            strategy.strategy_id
        )

    return {
        status: tuple(ids)
        for status, ids in index.items()
    }


StrategyRegistry.status_index = (
    _strategy_status_index
)


# ============================================================
# 2.14 — TAG INDEX
# ============================================================

def _strategy_tag_index(
    self,
) -> Dict[str, Tuple[str, ...]]:
    """
    Build tag -> strategy IDs index.
    """

    index: Dict[
        str,
        list,
    ] = {}

    for strategy in self._strategies.values():

        for tag in strategy.tags:

            normalized_tag = (
                self._normalize_text(
                    tag
                ).lower()
            )

            index.setdefault(
                normalized_tag,
                [],
            ).append(
                strategy.strategy_id
            )

    return {
        tag: tuple(ids)
        for tag, ids in index.items()
    }


StrategyRegistry.tag_index = (
    _strategy_tag_index
)


# ============================================================
# 2.15 — DEPENDENCY EXTRACTION
# ============================================================

def _strategy_dependencies(
    self,
    strategy_id: str,
) -> Tuple[str, ...]:
    """
    Return declared strategy dependencies.

    Dependencies are metadata/governance relationships only.

    They do not execute another strategy.
    """

    strategy = self.get(
        strategy_id
    )

    dependencies = tuple(
        self._normalize_strategy_id(
            dependency
        )
        for dependency in strategy.dependencies
        if self._normalize_strategy_id(
            dependency
        )
    )

    return dependencies


StrategyRegistry.dependencies = (
    _strategy_dependencies
)


# ============================================================
# 2.16 — DEPENDENTS
# ============================================================

def _strategy_dependents(
    self,
    strategy_id: str,
) -> Tuple[str, ...]:
    """
    Return strategies that depend on the specified strategy.
    """

    normalized_id = (
        self._normalize_strategy_id(
            strategy_id
        )
    )

    if not self.exists(
        normalized_id
    ):
        raise StrategyNotFoundError(
            f"Strategy not found: "
            f"{normalized_id}"
        )

    dependents = []

    for strategy in self._strategies.values():

        dependencies = tuple(
            self._normalize_strategy_id(
                dependency
            )
            for dependency in strategy.dependencies
        )

        if normalized_id in dependencies:
            dependents.append(
                strategy.strategy_id
            )

    return tuple(
        dependents
    )


StrategyRegistry.dependents = (
    _strategy_dependents
)


# ============================================================
# 2.17 — DEPENDENCY GRAPH
# ============================================================

def _strategy_dependency_graph(
    self,
) -> Dict[str, Tuple[str, ...]]:
    """
    Return strategy dependency graph.
    """

    return {
        strategy.strategy_id: tuple(
            self._normalize_strategy_id(
                dependency
            )
            for dependency in strategy.dependencies
        )
        for strategy in self._strategies.values()
    }


StrategyRegistry.dependency_graph = (
    _strategy_dependency_graph
)


# ============================================================
# 2.18 — VALIDATE ONE STRATEGY DEPENDENCY SET
# ============================================================

def _strategy_validate_dependencies(
    self,
    strategy_id: str,
) -> bool:
    """
    Validate dependencies declared by one strategy.
    """

    strategy = self.get(
        strategy_id
    )

    normalized_id = (
        self._normalize_strategy_id(
            strategy.strategy_id
        )
    )

    dependencies = tuple(
        self._normalize_strategy_id(
            dependency
        )
        for dependency in strategy.dependencies
    )

    if normalized_id in dependencies:
        raise StrategyDependencyError(
            f"Strategy cannot depend on itself: "
            f"{normalized_id}"
        )

    missing = [
        dependency
        for dependency in dependencies
        if dependency
        and not self.exists(
            dependency
        )
    ]

    if missing:
        raise StrategyDependencyError(
            f"Missing dependencies for "
            f"{normalized_id}: {missing}"
        )

    return True


StrategyRegistry.validate_dependencies = (
    _strategy_validate_dependencies
)


# ============================================================
# 2.19 — VALIDATE ALL DEPENDENCIES
# ============================================================

def _strategy_validate_all_dependencies(
    self,
) -> bool:
    """
    Validate dependency references for every strategy.
    """

    for strategy in self._strategies.values():

        self.validate_dependencies(
            strategy.strategy_id
        )

    return True


StrategyRegistry.validate_all_dependencies = (
    _strategy_validate_all_dependencies
)


# ============================================================
# 2.20 — DETECT DEPENDENCY CYCLES
# ============================================================

def _strategy_detect_cycles(
    self,
) -> Tuple[Tuple[str, ...], ...]:
    """
    Detect dependency cycles using DFS.

    Returns a tuple of detected cycles.
    """

    graph = self.dependency_graph()

    cycles = []
    visited = set()

    def visit(
        node: str,
        path: list,
        active: set,
    ) -> None:

        if node in active:

            try:
                start = path.index(
                    node
                )
            except ValueError:
                start = 0

            cycle = tuple(
                path[start:]
                + [node]
            )

            if cycle not in cycles:
                cycles.append(
                    cycle
                )

            return

        if node in visited:
            return

        active.add(node)
        path.append(node)

        for dependency in graph.get(
            node,
            (),
        ):

            if dependency in graph:
                visit(
                    dependency,
                    path,
                    active,
                )

        path.pop()
        active.remove(node)
        visited.add(node)

    for node in graph:
        visit(
            node,
            [],
            set(),
        )

    return tuple(
        cycles
    )


StrategyRegistry.detect_cycles = (
    _strategy_detect_cycles
)


# ============================================================
# 2.21 — ASSERT NO CYCLES
# ============================================================

def _strategy_assert_no_cycles(
    self,
) -> bool:
    """
    Raise StrategyDependencyError when dependency cycles exist.
    """

    cycles = self.detect_cycles()

    if cycles:
        raise StrategyDependencyError(
            f"Strategy dependency cycle(s) detected: "
            f"{cycles}"
        )

    return True


StrategyRegistry.assert_no_cycles = (
    _strategy_assert_no_cycles
)


# ============================================================
# 2.22 — SAFE DEPENDENCY-AWARE REGISTRATION
# ============================================================

def _strategy_register_with_dependencies(
    self,
    definition: StrategyDefinition,
) -> StrategyDefinition:
    """
    Register a strategy only when all declared dependencies
    already exist and the resulting graph is acyclic.
    """

    self._validate_definition(
        definition
    )

    strategy_id = (
        self._normalize_strategy_id(
            definition.strategy_id
        )
    )

    dependencies = tuple(
        self._normalize_strategy_id(
            dependency
        )
        for dependency in definition.dependencies
    )

    if strategy_id in dependencies:
        raise StrategyDependencyError(
            f"Strategy cannot depend on itself: "
            f"{strategy_id}"
        )

    missing = [
        dependency
        for dependency in dependencies
        if dependency
        and not self.exists(
            dependency
        )
    ]

    if missing:
        raise StrategyDependencyError(
            f"Missing strategy dependencies for "
            f"{strategy_id}: {missing}"
        )

    result = self.register_safe(
        definition
    )

    self.assert_no_cycles()

    return result


StrategyRegistry.register_with_dependencies = (
    _strategy_register_with_dependencies
)


# ============================================================
# 2.23 — UNREGISTER
# ============================================================

def _strategy_unregister(
    self,
    strategy_id: str,
    force: bool = False,
) -> StrategyDefinition:
    """
    Remove a strategy from the registry.

    By default, a strategy with registered dependents cannot
    be removed.

    force=True explicitly overrides that protection.
    """

    normalized_id = (
        self._normalize_strategy_id(
            strategy_id
        )
    )

    strategy = self.get(
        normalized_id
    )

    dependents = self.dependents(
        normalized_id
    )

    if dependents and not force:
        raise StrategyUnregisterError(
            f"Cannot unregister strategy "
            f"{normalized_id}; dependent strategies exist: "
            f"{dependents}"
        )

    del self._strategies[
        normalized_id
    ]

    return strategy


StrategyRegistry.unregister = (
    _strategy_unregister
)


# ============================================================
# 2.24 — SUMMARY
# ============================================================

def _strategy_summary(
    self,
) -> Dict[str, Any]:
    """
    Return non-mutating registry summary.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "strategy_count": self.count(),
        "strategy_ids": self.strategy_ids(),
        "active_count": len(
            self.active_strategies()
        ),
        "domains": tuple(
            self.domain_index().keys()
        ),
        "layers": tuple(
            self.layer_index().keys()
        ),
        "statuses": tuple(
            self.status_index().keys()
        ),
    }


StrategyRegistry.summary = (
    _strategy_summary
)


# ============================================================
# 2.25 — HEALTH CHECK
# ============================================================

def _strategy_health(
    self,
) -> Dict[str, Any]:
    """
    Perform a lightweight registry health check.
    """

    issues = []

    try:
        for strategy in self.list_all():
            self._validate_definition(
                strategy
            )
    except Exception as exc:
        issues.append(
            {
                "type": "definition_error",
                "detail": str(exc),
            }
        )

    try:
        self.validate_all_dependencies()
    except Exception as exc:
        issues.append(
            {
                "type": "dependency_error",
                "detail": str(exc),
            }
        )

    cycles = self.detect_cycles()

    if cycles:
        issues.append(
            {
                "type": "dependency_cycle",
                "cycles": cycles,
            }
        )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "strategy_count": self.count(),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


StrategyRegistry.health = (
    _strategy_health
)


# ============================================================
# END OF STRATEGY REGISTRY — PART 2
# ============================================================
# ============================================================
# STRATEGY REGISTRY — PART 3
# Search + Dependency-Aware Bootstrap + Snapshot + Audit
# ============================================================


# ============================================================
# 3.1 — PART 3 EXCEPTIONS
# ============================================================

class StrategyBootstrapError(
    StrategyRegistryError
):
    """Raised when strategy bootstrap fails."""


class StrategySnapshotError(
    StrategyRegistryError
):
    """Raised when strategy snapshot operations fail."""


# ============================================================
# 3.2 — GENERAL SEARCH
# ============================================================

def _strategy_find(
    self,
    domain: Optional[str] = None,
    layer: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    owner: Optional[str] = None,
) -> Tuple[StrategyDefinition, ...]:
    """
    Search strategies using optional metadata filters.

    All supplied filters must match.
    """

    normalized_domain = (
        self._normalize_text(domain)
        if domain is not None
        else None
    )

    normalized_layer = (
        self._normalize_text(layer)
        if layer is not None
        else None
    )

    normalized_status = (
        self._normalize_text(status).lower()
        if status is not None
        else None
    )

    normalized_tag = (
        self._normalize_text(tag).lower()
        if tag is not None
        else None
    )

    normalized_owner = (
        self._normalize_text(owner)
        if owner is not None
        else None
    )

    results = []

    for strategy in self._strategies.values():

        if (
            normalized_domain is not None
            and strategy.domain != normalized_domain
        ):
            continue

        if (
            normalized_layer is not None
            and strategy.layer != normalized_layer
        ):
            continue

        if (
            normalized_status is not None
            and strategy.status != normalized_status
        ):
            continue

        if (
            normalized_tag is not None
            and normalized_tag not in tuple(
                tag.lower()
                for tag in strategy.tags
            )
        ):
            continue

        if (
            normalized_owner is not None
            and strategy.owner != normalized_owner
        ):
            continue

        results.append(strategy)

    return tuple(results)


StrategyRegistry.find = _strategy_find


# ============================================================
# 3.3 — SEARCH BY PREFIX
# ============================================================

def _strategy_find_by_prefix(
    self,
    prefix: str,
) -> Tuple[StrategyDefinition, ...]:
    """
    Find strategies whose IDs start with the supplied prefix.
    """

    normalized_prefix = (
        self._normalize_strategy_id(prefix)
    )

    return tuple(
        strategy
        for strategy in self._strategies.values()
        if strategy.strategy_id.startswith(
            normalized_prefix
        )
    )


StrategyRegistry.find_by_prefix = (
    _strategy_find_by_prefix
)


# ============================================================
# 3.4 — SEARCH BY DOMAIN
# ============================================================

def _strategy_find_by_domain(
    self,
    domain: str,
) -> Tuple[StrategyDefinition, ...]:
    return self.find(
        domain=domain
    )


StrategyRegistry.find_by_domain = (
    _strategy_find_by_domain
)


# ============================================================
# 3.5 — SEARCH BY LAYER
# ============================================================

def _strategy_find_by_layer(
    self,
    layer: str,
) -> Tuple[StrategyDefinition, ...]:
    return self.find(
        layer=layer
    )


StrategyRegistry.find_by_layer = (
    _strategy_find_by_layer
)


# ============================================================
# 3.6 — SEARCH BY STATUS
# ============================================================

def _strategy_find_by_status(
    self,
    status: str,
) -> Tuple[StrategyDefinition, ...]:
    return self.find(
        status=status
    )


StrategyRegistry.find_by_status = (
    _strategy_find_by_status
)


# ============================================================
# 3.7 — SEARCH BY TAG
# ============================================================

def _strategy_find_by_tag(
    self,
    tag: str,
) -> Tuple[StrategyDefinition, ...]:
    return self.find(
        tag=tag
    )


StrategyRegistry.find_by_tag = (
    _strategy_find_by_tag
)


# ============================================================
# 3.8 — BOOTSTRAP VALIDATION
# ============================================================

def _strategy_validate_bootstrap(
    self,
    definitions: Iterable[
        StrategyDefinition
    ],
) -> bool:
    """
    Validate a strategy bootstrap batch.

    Dependencies may refer to:
        1. strategies already present in registry
        2. another strategy in the same bootstrap batch

    No mutation occurs during validation.
    """

    definitions = tuple(definitions)

    batch_ids = set()

    for definition in definitions:

        self._validate_definition(
            definition
        )

        strategy_id = (
            self._normalize_strategy_id(
                definition.strategy_id
            )
        )

        if strategy_id in batch_ids:
            raise StrategyBootstrapError(
                f"Duplicate strategy in bootstrap: "
                f"{strategy_id}"
            )

        batch_ids.add(strategy_id)

    existing_ids = set(
        self.strategy_ids()
    )

    available_ids = (
        existing_ids
        | batch_ids
    )

    for definition in definitions:

        strategy_id = (
            self._normalize_strategy_id(
                definition.strategy_id
            )
        )

        for dependency in definition.dependencies:

            dependency_id = (
                self._normalize_strategy_id(
                    dependency
                )
            )

            if not dependency_id:
                continue

            if dependency_id == strategy_id:
                raise StrategyBootstrapError(
                    f"Strategy cannot depend on itself: "
                    f"{strategy_id}"
                )

            if dependency_id not in available_ids:
                raise StrategyBootstrapError(
                    f"Missing dependency "
                    f"{dependency_id} for strategy "
                    f"{strategy_id}"
                )

    return True


StrategyRegistry.validate_bootstrap = (
    _strategy_validate_bootstrap
)


# ============================================================
# 3.9 — DEPENDENCY-AWARE BOOTSTRAP
# ============================================================

def _strategy_bootstrap(
    self,
    definitions: Iterable[
        StrategyDefinition
    ],
) -> Tuple[StrategyDefinition, ...]:
    """
    Bootstrap multiple strategies in dependency-resolved order.

    Same-batch dependencies are supported.

    The registry is mutated only after each definition's
    dependencies are resolvable.
    """

    definitions = tuple(definitions)

    self._validate_bootstrap(
        definitions
    )

    pending = {
        self._normalize_strategy_id(
            definition.strategy_id
        ): definition
        for definition in definitions
    }

    installed = []

    while pending:

        progress = False

        for strategy_id, definition in tuple(
            pending.items()
        ):

            dependencies = tuple(
                self._normalize_strategy_id(
                    dependency
                )
                for dependency in definition.dependencies
            )

            unresolved = [
                dependency
                for dependency in dependencies
                if dependency
                and not self.exists(dependency)
            ]

            if unresolved:
                continue

            try:
                result = self.register_safe(
                    definition
                )

            except Exception as exc:
                raise StrategyBootstrapError(
                    f"Failed to bootstrap strategy "
                    f"{strategy_id}"
                ) from exc

            installed.append(result)

            del pending[strategy_id]

            progress = True

        if not progress:

            unresolved_map = {
                strategy_id: tuple(
                    self._normalize_strategy_id(
                        dependency
                    )
                    for dependency
                    in definition.dependencies
                    if dependency
                    and not self.exists(
                        self._normalize_strategy_id(
                            dependency
                        )
                    )
                )
                for strategy_id, definition
                in pending.items()
            }

            raise StrategyBootstrapError(
                "Unable to resolve strategy "
                f"dependency graph: {unresolved_map}"
            )

    self.assert_no_cycles()

    return tuple(installed)


StrategyRegistry.bootstrap = (
    _strategy_bootstrap
)


# ============================================================
# 3.10 — SNAPSHOT
# ============================================================

def _strategy_snapshot(
    self,
) -> Dict[str, Any]:
    """
    Create a serializable registry snapshot.
    """

    plans = []

    for strategy in self.list_all():

        plans.append(
            {
                "strategy_id": strategy.strategy_id,
                "name": strategy.name,
                "version": strategy.version,
                "domain": strategy.domain,
                "layer": strategy.layer,
                "description": strategy.description,
                "status": strategy.status,
                "owner": strategy.owner,
                "dependencies": tuple(
                    strategy.dependencies
                ),
                "tags": tuple(
                    strategy.tags
                ),
                "metadata": deepcopy(
                    strategy.metadata
                ),
                "registered_at": (
                    strategy.registered_at.isoformat()
                ),
            }
        )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "strategy_count": self.count(),
        "strategies": tuple(plans),
    }


StrategyRegistry.snapshot = (
    _strategy_snapshot
)


# ============================================================
# 3.11 — RESTORE SNAPSHOT
# ============================================================

def _strategy_restore_snapshot(
    self,
    snapshot: Dict[str, Any],
    replace_existing: bool = False,
) -> Tuple[StrategyDefinition, ...]:
    """
    Restore strategies from a previously generated snapshot.
    """

    if not isinstance(
        snapshot,
        dict,
    ):
        raise StrategySnapshotError(
            "Snapshot must be a dictionary."
        )

    if (
        snapshot.get("registry_name")
        != REGISTRY_NAME
    ):
        raise StrategySnapshotError(
            "Snapshot registry name mismatch."
        )

    raw_strategies = snapshot.get(
        "strategies"
    )

    if raw_strategies is None:
        raise StrategySnapshotError(
            "Snapshot does not contain strategies."
        )

    definitions = []

    for raw in raw_strategies:

        if not isinstance(
            raw,
            dict,
        ):
            raise StrategySnapshotError(
                "Invalid strategy snapshot entry."
            )

        registered_at_raw = raw.get(
            "registered_at"
        )

        try:
            registered_at = (
                datetime.fromisoformat(
                    registered_at_raw
                )
                if registered_at_raw
                else datetime.now(
                    timezone.utc
                )
            )
        except Exception as exc:
            raise StrategySnapshotError(
                "Invalid registered_at value."
            ) from exc

        definition = StrategyDefinition(
            strategy_id=raw.get(
                "strategy_id",
                "",
            ),
            name=raw.get(
                "name",
                "",
            ),
            version=raw.get(
                "version",
                "",
            ),
            domain=raw.get(
                "domain",
                "",
            ),
            layer=raw.get(
                "layer",
                "",
            ),
            description=raw.get(
                "description",
                "",
            ),
            status=raw.get(
                "status",
                "registered",
            ),
            owner=raw.get(
                "owner",
                "",
            ),
            dependencies=tuple(
                raw.get(
                    "dependencies",
                    (),
                )
            ),
            tags=tuple(
                raw.get(
                    "tags",
                    (),
                )
            ),
            metadata=dict(
                raw.get(
                    "metadata",
                    {},
                )
            ),
            registered_at=registered_at,
        )

        definitions.append(
            definition
        )

    previous = deepcopy(
        self._strategies
    )

    try:

        if replace_existing:

            self._strategies.clear()

        results = self.bootstrap(
            definitions
        )

        return tuple(results)

    except Exception as exc:

        self._strategies = previous

        raise StrategySnapshotError(
            "Strategy snapshot restore failed."
        ) from exc


StrategyRegistry.restore_snapshot = (
    _strategy_restore_snapshot
)


# ============================================================
# 3.12 — METADATA EXPORT
# ============================================================

def _strategy_export_metadata(
    self,
) -> Tuple[Dict[str, Any], ...]:
    """
    Export strategy registry metadata.

    No strategy execution logic is exported.
    """

    exported = []

    for strategy in self.list_all():

        exported.append(
            {
                "strategy_id": strategy.strategy_id,
                "name": strategy.name,
                "version": strategy.version,
                "domain": strategy.domain,
                "layer": strategy.layer,
                "description": strategy.description,
                "status": strategy.status,
                "owner": strategy.owner,
                "dependencies": tuple(
                    strategy.dependencies
                ),
                "tags": tuple(
                    strategy.tags
                ),
                "metadata": deepcopy(
                    strategy.metadata
                ),
                "registered_at": (
                    strategy.registered_at.isoformat()
                ),
            }
        )

    return tuple(exported)


StrategyRegistry.export_metadata = (
    _strategy_export_metadata
)


# ============================================================
# 3.13 — CONSISTENCY CHECK
# ============================================================

def _strategy_consistency_check(
    self,
) -> Dict[str, Any]:
    """
    Perform structural consistency validation.
    """

    issues = []

    seen_ids = set()

    for strategy in self.list_all():

        strategy_id = (
            self._normalize_strategy_id(
                strategy.strategy_id
            )
        )

        if strategy_id in seen_ids:
            issues.append(
                {
                    "strategy_id": strategy_id,
                    "issue": "duplicate_id",
                }
            )

        seen_ids.add(strategy_id)

        try:
            self._validate_definition(
                strategy
            )
        except Exception as exc:
            issues.append(
                {
                    "strategy_id": strategy_id,
                    "issue": "invalid_definition",
                    "detail": str(exc),
                }
            )

        for dependency in strategy.dependencies:

            dependency_id = (
                self._normalize_strategy_id(
                    dependency
                )
            )

            if dependency_id == strategy_id:
                issues.append(
                    {
                        "strategy_id": strategy_id,
                        "issue": "self_dependency",
                    }
                )

            elif (
                dependency_id
                and not self.exists(
                    dependency_id
                )
            ):
                issues.append(
                    {
                        "strategy_id": strategy_id,
                        "issue": "missing_dependency",
                        "dependency": dependency_id,
                    }
                )

    cycles = self.detect_cycles()

    if cycles:
        issues.append(
            {
                "issue": "dependency_cycles",
                "cycles": cycles,
            }
        )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "strategy_count": self.count(),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


StrategyRegistry.consistency_check = (
    _strategy_consistency_check
)


# ============================================================
# 3.14 — FULL AUDIT
# ============================================================

def _strategy_full_audit(
    self,
) -> Dict[str, Any]:
    """
    Perform complete Part-3 registry audit.
    """

    consistency = (
        self.consistency_check()
    )

    health = self.health()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "summary": self.summary(),
        "consistency": consistency,
        "health": health,
        "healthy": (
            consistency["healthy"]
            and health["healthy"]
        ),
    }


StrategyRegistry.full_audit = (
    _strategy_full_audit
)


# ============================================================
# 3.15 — ASSERT HEALTHY
# ============================================================

def _strategy_assert_healthy(
    self,
) -> bool:
    """
    Raise StrategyRegistryError when the registry is unhealthy.
    """

    audit = self.full_audit()

    if not audit["healthy"]:
        raise StrategyRegistryError(
            f"Strategy registry audit failed: "
            f"{audit}"
        )

    return True


StrategyRegistry.assert_healthy = (
    _strategy_assert_healthy
)


# ============================================================
# 3.16 — REGISTRY STATE
# ============================================================

def _strategy_state(
    self,
) -> Dict[str, Any]:
    """
    Return compact registry state.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "strategy_count": self.count(),
        "active_count": len(
            self.active_strategies()
        ),
        "strategy_ids": self.strategy_ids(),
        "domains": tuple(
            self.domain_index().keys()
        ),
        "layers": tuple(
            self.layer_index().keys()
        ),
        "statuses": tuple(
            self.status_index().keys()
        ),
        "healthy": self.health()[
            "healthy"
        ],
    }


StrategyRegistry.state = (
    _strategy_state
)


# ============================================================
# END OF STRATEGY REGISTRY — PART 3
# ============================================================
# ============================================================
# STRATEGY REGISTRY — PART 4
# Declarative Specifications / Discovery / Registration
# ============================================================

from dataclasses import dataclass
from typing import Iterable


# ============================================================
# 4.1 STRATEGY REGISTRATION SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class StrategyRegistrationSpec:
    """
    Declarative specification for registering a ROBOMLM strategy.

    This object describes WHAT a strategy is.

    It does NOT:
        - calculate signals
        - calculate indicators
        - generate entries
        - generate exits
        - calculate position size
        - execute orders
        - authorize users
        - enforce subscriptions
        - perform CAS decisions
    """

    strategy_id: str
    name: str
    version: str
    domain: str
    layer: str

    description: str = ""
    status: str = "registered"
    owner: str = ""

    dependencies: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_definition(self) -> StrategyDefinition:
        """
        Convert declarative specification into a StrategyDefinition.
        """

        return StrategyDefinition(
            strategy_id=self.strategy_id,
            name=self.name,
            version=self.version,
            domain=self.domain,
            layer=self.layer,
            description=self.description,
            status=self.status,
            owner=self.owner,
            dependencies=tuple(self.dependencies),
            tags=tuple(self.tags),
            metadata=deepcopy(self.metadata),
        )


# ============================================================
# 4.2 SPEC VALIDATION
# ============================================================

def _validate_strategy_spec(
    spec: StrategyRegistrationSpec,
) -> None:
    """
    Validate a declarative strategy specification.
    """

    if not isinstance(spec, StrategyRegistrationSpec):
        raise InvalidStrategyDefinitionError(
            "Strategy specification must be "
            "StrategyRegistrationSpec."
        )

    if not spec.strategy_id:
        raise InvalidStrategyDefinitionError(
            "Strategy specification requires strategy_id."
        )

    if not spec.name:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' requires name."
        )

    if not spec.version:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' requires version."
        )

    if not spec.domain:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' requires domain."
        )

    if not spec.layer:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' requires layer."
        )

    if spec.status not in VALID_STRATEGY_STATUSES:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' has invalid "
            f"status '{spec.status}'."
        )

    if not isinstance(spec.dependencies, tuple):
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' dependencies "
            "must be a tuple."
        )

    if not isinstance(spec.tags, tuple):
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' tags "
            "must be a tuple."
        )

    if not isinstance(spec.metadata, dict):
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' metadata "
            "must be a dictionary."
        )

    if spec.strategy_id in spec.dependencies:
        raise InvalidStrategyDefinitionError(
            f"Strategy '{spec.strategy_id}' cannot depend "
            "on itself."
        )


# ============================================================
# 4.3 REGISTER SPEC
# ============================================================

def _strategy_register_spec(
    self: StrategyRegistry,
    spec: StrategyRegistrationSpec,
    *,
    replace_existing: bool = False,
) -> StrategyDefinition:
    """
    Register one declarative strategy specification.
    """

    _validate_strategy_spec(spec)

    definition = spec.to_definition()

    if replace_existing:
        if self.exists(definition.strategy_id):
            return self.replace(definition)

    return self.register(definition)


StrategyRegistry.register_spec = _strategy_register_spec


# ============================================================
# 4.4 REGISTER MULTIPLE SPECS
# ============================================================

def _strategy_register_specs(
    self: StrategyRegistry,
    specs: Iterable[StrategyRegistrationSpec],
    *,
    replace_existing: bool = False,
) -> list[StrategyDefinition]:
    """
    Register multiple declarative strategy specifications.
    """

    normalized_specs = list(specs)

    if not normalized_specs:
        return []

    for spec in normalized_specs:
        _validate_strategy_spec(spec)

    definitions = [
        spec.to_definition()
        for spec in normalized_specs
    ]

    ids = [
        definition.strategy_id
        for definition in definitions
    ]

    if len(ids) != len(set(ids)):
        raise StrategyRegistrationConflictError(
            "Duplicate strategy_id detected in "
            "registration specifications."
        )

    if replace_existing:
        registered = []

        for definition in definitions:
            if self.exists(definition.strategy_id):
                registered.append(
                    self.replace(definition)
                )
            else:
                registered.append(
                    self.register(definition)
                )

        return registered

    return self.register_many(definitions)


StrategyRegistry.register_specs = _strategy_register_specs


# ============================================================
# 4.5 DISCOVERY CATALOG
# ============================================================

_STRATEGY_REGISTRATION_SPECS: dict[
    str,
    StrategyRegistrationSpec,
] = {}


# ============================================================
# 4.6 STRATEGY SPEC DECORATOR
# ============================================================

def strategy_spec(
    *,
    strategy_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    dependencies: Iterable[str] = (),
    tags: Iterable[str] = (),
    metadata: Optional[dict[str, Any]] = None,
):
    """
    Declarative strategy registration decorator.

    The decorated object is NOT treated as strategy execution logic.

    It is only a discovery marker carrying registration metadata.
    """

    spec = StrategyRegistrationSpec(
        strategy_id=strategy_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        status=status,
        owner=owner,
        dependencies=tuple(dependencies),
        tags=tuple(tags),
        metadata=deepcopy(metadata or {}),
    )

    _validate_strategy_spec(spec)

    existing = _STRATEGY_REGISTRATION_SPECS.get(
        strategy_id
    )

    if existing is not None and existing != spec:
        raise StrategyRegistrationConflictError(
            f"Conflicting strategy specification already "
            f"exists for '{strategy_id}'."
        )

    _STRATEGY_REGISTRATION_SPECS[strategy_id] = spec

    def decorator(target):
        setattr(
            target,
            "__robomlm_strategy_spec__",
            spec,
        )
        return target

    return decorator


# ============================================================
# 4.7 DISCOVER STRATEGY SPECS
# ============================================================

def discover_strategy_specs() -> list[StrategyRegistrationSpec]:
    """
    Return all discovered strategy specifications.
    """

    return list(
        _STRATEGY_REGISTRATION_SPECS.values()
    )


def get_strategy_spec(
    strategy_id: str,
) -> StrategyRegistrationSpec:
    """
    Retrieve one discovered strategy specification.
    """

    normalized_id = strategy_registry._normalize_strategy_id(
        strategy_id
    )

    try:
        return _STRATEGY_REGISTRATION_SPECS[
            normalized_id
        ]
    except KeyError as exc:
        raise StrategyNotFoundError(
            f"Discovered strategy specification "
            f"'{strategy_id}' not found."
        ) from exc


# ============================================================
# 4.8 REGISTER DISCOVERED STRATEGIES
# ============================================================

def _strategy_register_discovered(
    self: StrategyRegistry,
    *,
    replace_existing: bool = False,
) -> list[StrategyDefinition]:
    """
    Register all discovered strategy specifications.

    Dependencies remain declarative metadata.
    No execution semantics are introduced here.
    """

    specs = discover_strategy_specs()

    if not specs:
        return []

    return self.register_specs(
        specs,
        replace_existing=replace_existing,
    )


StrategyRegistry.register_discovered = (
    _strategy_register_discovered
)


# ============================================================
# 4.9 DISCOVERY REPORT
# ============================================================

def _strategy_discovery_report(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Compare discovered specifications with the
    currently registered strategy definitions.
    """

    discovered = discover_strategy_specs()

    discovered_ids = {
        spec.strategy_id
        for spec in discovered
    }

    registered_ids = set(self.strategy_ids())

    missing_from_registry = sorted(
        discovered_ids - registered_ids
    )

    registered_without_spec = sorted(
        registered_ids - discovered_ids
    )

    mismatches: list[dict[str, Any]] = []

    for spec in discovered:
        if not self.exists(spec.strategy_id):
            continue

        registered = self.get(spec.strategy_id)
        expected = spec.to_definition()

        differences: dict[str, Any] = {}

        fields = (
            "name",
            "version",
            "domain",
            "layer",
            "description",
            "status",
            "owner",
            "dependencies",
            "tags",
            "metadata",
        )

        for field_name in fields:
            actual_value = getattr(
                registered,
                field_name,
            )

            expected_value = getattr(
                expected,
                field_name,
            )

            if actual_value != expected_value:
                differences[field_name] = {
                    "registered": deepcopy(
                        actual_value
                    ),
                    "discovered": deepcopy(
                        expected_value
                    ),
                }

        if differences:
            mismatches.append(
                {
                    "strategy_id": spec.strategy_id,
                    "differences": differences,
                }
            )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "discovered_count": len(discovered),
        "registered_count": self.count(),
        "discovered_ids": sorted(discovered_ids),
        "registered_ids": sorted(registered_ids),
        "missing_from_registry": missing_from_registry,
        "registered_without_spec": registered_without_spec,
        "mismatches": mismatches,
        "healthy": (
            not missing_from_registry
            and not mismatches
        ),
    }


StrategyRegistry.discovery_report = (
    _strategy_discovery_report
)


# ============================================================
# 4.10 DISCOVERED METADATA EXPORT
# ============================================================

def _strategy_export_discovered_metadata(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Export discovered strategy metadata only.
    """

    specs = discover_strategy_specs()

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": len(specs),
        "strategies": [
            {
                "strategy_id": spec.strategy_id,
                "name": spec.name,
                "version": spec.version,
                "domain": spec.domain,
                "layer": spec.layer,
                "description": spec.description,
                "status": spec.status,
                "owner": spec.owner,
                "dependencies": list(
                    spec.dependencies
                ),
                "tags": list(spec.tags),
                "metadata": deepcopy(
                    spec.metadata
                ),
            }
            for spec in specs
        ],
    }


StrategyRegistry.export_discovered_strategy_metadata = (
    _strategy_export_discovered_metadata
)


# ============================================================
# 4.11 SPEC CONSISTENCY CHECK
# ============================================================

def _strategy_spec_consistency_check(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Validate discovered specifications internally and
    against registry definitions.
    """

    errors: list[str] = []

    discovered = discover_strategy_specs()

    seen_ids: set[str] = set()

    for spec in discovered:
        try:
            _validate_strategy_spec(spec)
        except Exception as exc:
            errors.append(
                f"{spec.strategy_id}: {exc}"
            )

        if spec.strategy_id in seen_ids:
            errors.append(
                f"Duplicate discovered strategy_id: "
                f"{spec.strategy_id}"
            )

        seen_ids.add(spec.strategy_id)

    report = self.discovery_report()

    for strategy_id in report[
        "missing_from_registry"
    ]:
        errors.append(
            f"Discovered strategy not registered: "
            f"{strategy_id}"
        )

    for mismatch in report["mismatches"]:
        errors.append(
            f"Registered/discovered mismatch: "
            f"{mismatch['strategy_id']}"
        )

    return {
        "healthy": not errors,
        "error_count": len(errors),
        "errors": errors,
        "discovered_count": len(discovered),
    }


StrategyRegistry.spec_consistency_check = (
    _strategy_spec_consistency_check
)


# ============================================================
# 4.12 DISCOVERY AUDIT
# ============================================================

def _strategy_discovery_audit(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Full declarative discovery audit.

    Combines:
        - specification validation
        - discovery consistency
        - registry consistency
        - dependency validation
    """

    spec_report = self.spec_consistency_check()
    registry_report = self.consistency_check()
    dependency_report = self.validate_all_dependencies()

    healthy = (
        spec_report["healthy"]
        and registry_report["healthy"]
        and dependency_report["healthy"]
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "spec_consistency": spec_report,
        "registry_consistency": registry_report,
        "dependency_validation": dependency_report,
    }


StrategyRegistry.discovery_audit = (
    _strategy_discovery_audit
)


# ============================================================
# 4.13 DISCOVERY HEALTH ASSERTION
# ============================================================

def _strategy_assert_discovery_healthy(
    self: StrategyRegistry,
) -> None:
    """
    Raise an exception when strategy discovery is unhealthy.
    """

    audit = self.discovery_audit()

    if not audit["healthy"]:
        raise StrategyBootstrapError(
            "Strategy discovery audit failed: "
            f"{audit}"
        )


StrategyRegistry.assert_discovery_healthy = (
    _strategy_assert_discovery_healthy
)


# ============================================================
# END OF STRATEGY REGISTRY — PART 4
# ============================================================
# ============================================================
# STRATEGY REGISTRY — PART 5
# Canonical Catalog / Freeze / Atomic Governance / Final Install
# ============================================================


# ============================================================
# 5.1 FREEZE / MUTATION EXCEPTIONS
# ============================================================

class StrategyRegistryFrozenError(StrategyRegistryError):
    """Raised when a mutation is attempted on a frozen registry."""


class StrategyAtomicInstallError(StrategyRegistryError):
    """Raised when atomic strategy installation fails."""


class StrategyCanonicalCatalogError(StrategyRegistryError):
    """Raised when the canonical strategy catalog is invalid."""


# ============================================================
# 5.2 FREEZE STATE
# ============================================================

StrategyRegistry._frozen = False


def _strategy_assert_mutable(
    self: StrategyRegistry,
) -> None:
    """
    Ensure the registry is mutable.
    """

    if getattr(self, "_frozen", False):
        raise StrategyRegistryFrozenError(
            "Strategy registry is frozen. "
            "Unfreeze before performing mutations."
        )


def _strategy_freeze(
    self: StrategyRegistry,
) -> None:
    """
    Freeze the registry against normal mutations.
    """

    self._frozen = True


def _strategy_unfreeze(
    self: StrategyRegistry,
) -> None:
    """
    Unfreeze the registry.
    """

    self._frozen = False


def _strategy_is_frozen(
    self: StrategyRegistry,
) -> bool:
    """
    Return current freeze state.
    """

    return bool(
        getattr(self, "_frozen", False)
    )


StrategyRegistry.assert_mutable = _strategy_assert_mutable
StrategyRegistry.freeze = _strategy_freeze
StrategyRegistry.unfreeze = _strategy_unfreeze
StrategyRegistry.is_frozen = _strategy_is_frozen


# ============================================================
# 5.3 PROTECTED MUTATION WRAPPERS
# ============================================================

_strategy_original_register = StrategyRegistry.register
_strategy_original_register_many = StrategyRegistry.register_many
_strategy_original_replace = StrategyRegistry.replace
_strategy_original_unregister = StrategyRegistry.unregister
_strategy_original_set_status = StrategyRegistry.set_status


def _strategy_guarded_register(
    self: StrategyRegistry,
    definition: StrategyDefinition,
) -> StrategyDefinition:

    self.assert_mutable()

    return _strategy_original_register(
        self,
        definition,
    )


def _strategy_guarded_register_many(
    self: StrategyRegistry,
    definitions: Iterable[StrategyDefinition],
) -> list[StrategyDefinition]:

    self.assert_mutable()

    return _strategy_original_register_many(
        self,
        definitions,
    )


def _strategy_guarded_replace(
    self: StrategyRegistry,
    definition: StrategyDefinition,
) -> StrategyDefinition:

    self.assert_mutable()

    return _strategy_original_replace(
        self,
        definition,
    )


def _strategy_guarded_unregister(
    self: StrategyRegistry,
    strategy_id: str,
    *,
    force: bool = False,
) -> StrategyDefinition:

    self.assert_mutable()

    return _strategy_original_unregister(
        self,
        strategy_id,
        force=force,
    )


def _strategy_guarded_set_status(
    self: StrategyRegistry,
    strategy_id: str,
    status: str,
) -> StrategyDefinition:

    self.assert_mutable()

    return _strategy_original_set_status(
        self,
        strategy_id,
        status,
    )


StrategyRegistry.register = _strategy_guarded_register
StrategyRegistry.register_many = _strategy_guarded_register_many
StrategyRegistry.replace = _strategy_guarded_replace
StrategyRegistry.unregister = _strategy_guarded_unregister
StrategyRegistry.set_status = _strategy_guarded_set_status


# ============================================================
# 5.4 CLONE
# ============================================================

def _strategy_clone(
    self: StrategyRegistry,
) -> StrategyRegistry:
    """
    Create an independent registry clone.
    """

    cloned = StrategyRegistry()

    cloned._strategies = deepcopy(
        self._strategies
    )

    cloned._frozen = getattr(
        self,
        "_frozen",
        False,
    )

    return cloned


StrategyRegistry.clone = _strategy_clone


# ============================================================
# 5.5 ATOMIC REGISTRATION
# ============================================================

def _strategy_atomic_register(
    self: StrategyRegistry,
    definition: StrategyDefinition,
) -> StrategyDefinition:
    """
    Register one strategy atomically.

    If registration fails, the original registry remains
    unchanged.
    """

    self.assert_mutable()

    snapshot = self.snapshot()

    try:
        return self.register(definition)

    except Exception as exc:

        try:
            self.restore_snapshot(
                snapshot,
                replace_existing=True,
            )
        except Exception as restore_exc:
            raise StrategyAtomicInstallError(
                "Strategy registration failed and "
                "rollback also failed."
            ) from restore_exc

        raise StrategyAtomicInstallError(
            f"Atomic strategy registration failed: {exc}"
        ) from exc


StrategyRegistry.atomic_register = (
    _strategy_atomic_register
)


# ============================================================
# 5.6 ATOMIC SPEC REGISTRATION
# ============================================================

def _strategy_atomic_register_specs(
    self: StrategyRegistry,
    specs: Iterable[StrategyRegistrationSpec],
    *,
    replace_existing: bool = False,
) -> list[StrategyDefinition]:
    """
    Register multiple strategy specifications atomically.
    """

    self.assert_mutable()

    normalized_specs = list(specs)

    snapshot = self.snapshot()

    try:
        return self.register_specs(
            normalized_specs,
            replace_existing=replace_existing,
        )

    except Exception as exc:

        try:
            self.restore_snapshot(
                snapshot,
                replace_existing=True,
            )
        except Exception as restore_exc:
            raise StrategyAtomicInstallError(
                "Atomic strategy-spec registration failed "
                "and rollback also failed."
            ) from restore_exc

        raise StrategyAtomicInstallError(
            f"Atomic strategy-spec registration failed: {exc}"
        ) from exc


StrategyRegistry.atomic_register_specs = (
    _strategy_atomic_register_specs
)


# ============================================================
# 5.7 CANONICAL ROBOMLM STRATEGY DOMAINS
# ============================================================

STRATEGY_DOMAIN_MARKET = "market"
STRATEGY_DOMAIN_EQUITY = "equity"
STRATEGY_DOMAIN_CRYPTO = "crypto"
STRATEGY_DOMAIN_FOREX = "forex"
STRATEGY_DOMAIN_COMMODITY = "commodity"
STRATEGY_DOMAIN_INDEX = "index"
STRATEGY_DOMAIN_MULTI_ASSET = "multi_asset"


# ============================================================
# 5.8 CANONICAL STRATEGY LAYERS
# ============================================================

STRATEGY_LAYER_ANALYSIS = "analysis"
STRATEGY_LAYER_SCANNING = "scanning"
STRATEGY_LAYER_OPPORTUNITY = "opportunity"
STRATEGY_LAYER_DECISION = "decision"


# ============================================================
# 5.9 CANONICAL STRATEGY BUILDER
# ============================================================

def _canonical_strategy(
    *,
    strategy_id: str,
    name: str,
    version: str = "1.0.0",
    domain: str,
    layer: str,
    description: str,
    dependencies: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    metadata: Optional[dict[str, Any]] = None,
) -> StrategyRegistrationSpec:
    """
    Build one canonical ROBOMLM strategy specification.

    Canonical strategies are registry metadata only.
    """

    return StrategyRegistrationSpec(
        strategy_id=strategy_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        status="active",
        owner="ROBOMLM",
        dependencies=dependencies,
        tags=tags,
        metadata=deepcopy(
            metadata or {}
        ),
    )


# ============================================================
# 5.10 CANONICAL ROBOMLM STRATEGY CATALOG
# ============================================================

ROBOMLM_CANONICAL_STRATEGY_SPECS = (

    _canonical_strategy(
        strategy_id="market_context_strategy",
        name="Market Context Strategy",
        domain=STRATEGY_DOMAIN_MARKET,
        layer=STRATEGY_LAYER_ANALYSIS,
        description=(
            "Consumes governed market context metadata "
            "for strategy classification."
        ),
        tags=(
            "market_context",
            "analysis",
        ),
    ),

    _canonical_strategy(
        strategy_id="structure_breakout_strategy",
        name="Structure Breakout Strategy",
        domain=STRATEGY_DOMAIN_EQUITY,
        layer=STRATEGY_LAYER_SCANNING,
        description=(
            "Declarative strategy definition for "
            "structure and breakout opportunity analysis."
        ),
        dependencies=(
            "market_context_strategy",
        ),
        tags=(
            "structure",
            "breakout",
            "equity",
        ),
    ),

    _canonical_strategy(
        strategy_id="accumulation_distribution_strategy",
        name="Accumulation Distribution Strategy",
        domain=STRATEGY_DOMAIN_EQUITY,
        layer=STRATEGY_LAYER_SCANNING,
        description=(
            "Declarative strategy definition for "
            "accumulation and distribution analysis."
        ),
        dependencies=(
            "market_context_strategy",
        ),
        tags=(
            "accumulation",
            "distribution",
            "equity",
        ),
    ),

    _canonical_strategy(
        strategy_id="breakout_confirmation_strategy",
        name="Breakout Confirmation Strategy",
        domain=STRATEGY_DOMAIN_EQUITY,
        layer=STRATEGY_LAYER_OPPORTUNITY,
        description=(
            "Declarative strategy definition for "
            "confirmed breakout opportunity classification."
        ),
        dependencies=(
            "structure_breakout_strategy",
        ),
        tags=(
            "breakout",
            "confirmation",
            "opportunity",
        ),
    ),

    _canonical_strategy(
        strategy_id="multi_asset_opportunity_strategy",
        name="Multi Asset Opportunity Strategy",
        domain=STRATEGY_DOMAIN_MULTI_ASSET,
        layer=STRATEGY_LAYER_OPPORTUNITY,
        description=(
            "Declarative strategy definition for "
            "cross-market opportunity classification."
        ),
        dependencies=(
            "market_context_strategy",
        ),
        tags=(
            "multi_asset",
            "opportunity",
            "global_scan",
        ),
    ),

    _canonical_strategy(
        strategy_id="risk_aware_decision_strategy",
        name="Risk Aware Decision Strategy",
        domain=STRATEGY_DOMAIN_MARKET,
        layer=STRATEGY_LAYER_DECISION,
        description=(
            "Declarative strategy definition for "
            "risk-aware decision classification."
        ),
        dependencies=(
            "multi_asset_opportunity_strategy",
        ),
        tags=(
            "decision",
            "risk",
        ),
    ),

)


# ============================================================
# 5.11 CANONICAL CATALOG VALIDATION
# ============================================================

def validate_canonical_strategy_catalog() -> dict[str, Any]:
    """
    Validate the canonical strategy catalog.
    """

    errors: list[str] = []
    ids: list[str] = []

    for spec in ROBOMLM_CANONICAL_STRATEGY_SPECS:

        try:
            _validate_strategy_spec(spec)
        except Exception as exc:
            errors.append(str(exc))

        if spec.strategy_id in ids:
            errors.append(
                "Duplicate canonical strategy_id: "
                f"{spec.strategy_id}"
            )

        ids.append(spec.strategy_id)

    known_ids = set(ids)

    for spec in ROBOMLM_CANONICAL_STRATEGY_SPECS:

        for dependency in spec.dependencies:

            if dependency not in known_ids:
                errors.append(
                    f"Canonical strategy "
                    f"'{spec.strategy_id}' depends on "
                    f"unknown canonical strategy "
                    f"'{dependency}'."
                )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "catalog_name": (
            "ROBOMLM_CANONICAL_STRATEGY_SPECS"
        ),
        "count": len(
            ROBOMLM_CANONICAL_STRATEGY_SPECS
        ),
        "strategy_ids": sorted(ids),
        "errors": errors,
        "healthy": not errors,
    }


# ============================================================
# 5.12 CANONICAL CATALOG REGISTRATION
# ============================================================

def register_canonical_strategies(
    registry: Optional[StrategyRegistry] = None,
    *,
    replace_existing: bool = False,
) -> list[StrategyDefinition]:
    """
    Register the canonical ROBOMLM strategy catalog.
    """

    target = (
        registry
        if registry is not None
        else strategy_registry
    )

    validation = (
        validate_canonical_strategy_catalog()
    )

    if not validation["healthy"]:
        raise StrategyCanonicalCatalogError(
            f"Canonical strategy catalog is invalid: "
            f"{validation['errors']}"
        )

    return target.atomic_register_specs(
        ROBOMLM_CANONICAL_STRATEGY_SPECS,
        replace_existing=replace_existing,
    )


# ============================================================
# 5.13 CANONICAL STRATEGY IDS
# ============================================================

def canonical_strategy_ids() -> tuple[str, ...]:
    """
    Return canonical strategy identifiers.
    """

    return tuple(
        spec.strategy_id
        for spec in ROBOMLM_CANONICAL_STRATEGY_SPECS
    )


# ============================================================
# 5.14 CANONICAL STRATEGY REPORT
# ============================================================

def canonical_strategy_report(
    registry: Optional[StrategyRegistry] = None,
) -> dict[str, Any]:
    """
    Report canonical catalog coverage inside a registry.
    """

    target = (
        registry
        if registry is not None
        else strategy_registry
    )

    canonical_ids = set(
        canonical_strategy_ids()
    )

    registered_ids = set(
        target.strategy_ids()
    )

    missing = sorted(
        canonical_ids - registered_ids
    )

    present = sorted(
        canonical_ids & registered_ids
    )

    return {
        "canonical_count": len(canonical_ids),
        "registered_canonical_count": len(present),
        "missing": missing,
        "present": present,
        "complete": not missing,
    }


# ============================================================
# 5.15 CANONICAL AUDIT
# ============================================================

def canonical_strategy_audit(
    registry: Optional[StrategyRegistry] = None,
) -> dict[str, Any]:
    """
    Perform canonical strategy catalog audit.
    """

    target = (
        registry
        if registry is not None
        else strategy_registry
    )

    catalog = (
        validate_canonical_strategy_catalog()
    )

    coverage = canonical_strategy_report(
        target
    )

    dependency_report = (
        target.validate_all_dependencies()
    )

    healthy = (
        catalog["healthy"]
        and coverage["complete"]
        and dependency_report["healthy"]
    )

    return {
        "healthy": healthy,
        "catalog": catalog,
        "coverage": coverage,
        "dependency_validation": dependency_report,
    }


# ============================================================
# 5.16 FULL REGISTRY AUDIT
# ============================================================

def strategy_full_governance_audit(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Full governance audit for the strategy registry.
    """

    consistency = self.consistency_check()
    discovery = self.discovery_audit()

    canonical = canonical_strategy_audit(
        self
    )

    healthy = (
        consistency["healthy"]
        and discovery["healthy"]
        and canonical["healthy"]
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "frozen": self.is_frozen(),
        "consistency": consistency,
        "discovery": discovery,
        "canonical": canonical,
    }


StrategyRegistry.full_governance_audit = (
    strategy_full_governance_audit
)


# ============================================================
# 5.17 FULL HEALTH ASSERTION
# ============================================================

def strategy_assert_full_health(
    self: StrategyRegistry,
) -> None:
    """
    Raise when complete strategy registry governance
    validation fails.
    """

    audit = self.full_governance_audit()

    if not audit["healthy"]:
        raise StrategyRegistryError(
            "Strategy registry full governance audit failed: "
            f"{audit}"
        )


StrategyRegistry.assert_full_health = (
    strategy_assert_full_health
)


# ============================================================
# 5.18 FREEZE ONLY AFTER HEALTH CHECK
# ============================================================

def freeze_strategy_registry_if_healthy(
    self: StrategyRegistry,
) -> None:
    """
    Validate the complete registry before freezing it.
    """

    self.assert_full_health()

    self.freeze()


StrategyRegistry.freeze_if_healthy = (
    freeze_strategy_registry_if_healthy
)


# ============================================================
# 5.19 FINAL EXPORT
# ============================================================

def strategy_final_export(
    self: StrategyRegistry,
) -> dict[str, Any]:
    """
    Export final strategy registry state.
    """

    audit = self.full_governance_audit()

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "frozen": self.is_frozen(),
        "healthy": audit["healthy"],
        "strategy_count": self.count(),
        "strategies": self.export_metadata(),
        "canonical": canonical_strategy_report(
            self
        ),
        "audit": audit,
    }


StrategyRegistry.final_export = (
    strategy_final_export
)


# ============================================================
# 5.20 COMPLETE STRATEGY REGISTRY INSTALLATION
# ============================================================

def install_strategy_registry(
    *,
    include_discovered: bool = True,
    freeze_after_install: bool = False,
    reset_first: bool = False,
) -> dict[str, Any]:
    """
    Install the complete ROBOMLM strategy registry.

    Installation order:

        1. Optional reset
        2. Canonical catalog validation
        3. Canonical strategy installation
        4. Discovered strategy installation
        5. Full governance audit
        6. Optional freeze
        7. Final export
    """

    registry = strategy_registry

    if reset_first:
        reset_strategy_registry_for_testing()

    registry.assert_mutable()

    snapshot = registry.snapshot()

    try:

        # ----------------------------------------------------
        # STEP 1 — Canonical catalog
        # ----------------------------------------------------

        register_canonical_strategies(
            registry,
            replace_existing=False,
        )

        # ----------------------------------------------------
        # STEP 2 — Discovered specifications
        # ----------------------------------------------------

        if include_discovered:

            discovered = discover_strategy_specs()

            if discovered:

                registry.atomic_register_specs(
                    discovered,
                    replace_existing=False,
                )

        # ----------------------------------------------------
        # STEP 3 — Full audit
        # ----------------------------------------------------

        registry.assert_full_health()

        # ----------------------------------------------------
        # STEP 4 — Optional freeze
        # ----------------------------------------------------

        if freeze_after_install:
            registry.freeze()

        # ----------------------------------------------------
        # STEP 5 — Final export
        # ----------------------------------------------------

        return registry.final_export()

    except Exception as exc:

        try:
            registry.restore_snapshot(
                snapshot,
                replace_existing=True,
            )
        except Exception as restore_exc:
            raise StrategyAtomicInstallError(
                "Complete strategy registry installation "
                "failed and rollback also failed."
            ) from restore_exc

        raise StrategyAtomicInstallError(
            f"Complete strategy registry installation "
            f"failed: {exc}"
        ) from exc


# ============================================================
# 5.21 TEST RESET
# ============================================================

def reset_strategy_registry_for_testing() -> None:
    """
    Reset the global strategy registry.

    Intended for development/testing only.
    """

    strategy_registry.unfreeze()

    strategy_registry._strategies.clear()

    if hasattr(strategy_registry, "_domain_index"):
        strategy_registry._domain_index.clear()

    if hasattr(strategy_registry, "_layer_index"):
        strategy_registry._layer_index.clear()

    if hasattr(strategy_registry, "_status_index"):
        strategy_registry._status_index.clear()

    if hasattr(strategy_registry, "_tag_index"):
        strategy_registry._tag_index.clear()


# ============================================================
# 5.22 CANONICAL SUMMARY
# ============================================================

def canonical_strategy_summary() -> dict[str, Any]:
    """
    Return a compact canonical strategy summary.
    """

    validation = (
        validate_canonical_strategy_catalog()
    )

    return {
        "catalog": (
            "ROBOMLM_CANONICAL_STRATEGY_SPECS"
        ),
        "count": validation["count"],
        "healthy": validation["healthy"],
        "strategy_ids": validation[
            "strategy_ids"
        ],
    }


# ============================================================
# END OF STRATEGY REGISTRY — PART 5
# ============================================================