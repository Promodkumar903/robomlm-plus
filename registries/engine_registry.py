"""
ROBOMLM_PLUS
Engine Registry
Part 1 — Registry Foundation

Purpose:
    Central registration and controlled lookup of ROBOMLM engines.

Architecture rule:
    Registry DISCOVERS and REGISTERS engines.
    Registry does NOT execute intelligence.
    Registry does NOT calculate formulas.
    Registry does NOT make trading decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, Mapping, Optional


# ============================================================
# CONSTANTS
# ============================================================

REGISTRY_NAME = "engine_registry"
REGISTRY_VERSION = "1.0.0"

VALID_ENGINE_STATUSES = frozenset(
    {
        "registered",
        "active",
        "disabled",
        "deprecated",
    }
)


# ============================================================
# EXCEPTIONS
# ============================================================


class EngineRegistryError(Exception):
    """Base exception for engine registry failures."""


class EngineAlreadyRegisteredError(EngineRegistryError):
    """Raised when an engine ID is registered more than once."""


class EngineNotFoundError(EngineRegistryError):
    """Raised when a requested engine does not exist."""


class InvalidEngineDefinitionError(EngineRegistryError):
    """Raised when an engine definition violates registry rules."""


class EngineStateError(EngineRegistryError):
    """Raised when an invalid engine state transition is requested."""


# ============================================================
# ENGINE DEFINITION
# ============================================================


@dataclass(frozen=True)
class EngineDefinition:
    """
    Immutable metadata contract for one ROBOMLM engine.

    This object describes an engine.

    It does NOT contain:
        - trading formulas
        - market calculations
        - decision authority
        - execution logic
        - risk decisions
    """

    engine_id: str
    name: str
    version: str

    domain: str
    layer: str

    description: str = ""

    dependencies: tuple[str, ...] = field(default_factory=tuple)

    status: str = "registered"

    owner: str = "ROBOMLM"

    tags: tuple[str, ...] = field(default_factory=tuple)

    metadata: Mapping[str, Any] = field(default_factory=dict)

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# ENGINE REGISTRY
# ============================================================


class EngineRegistry:
    """
    Central registry for ROBOMLM engine definitions.

    Responsibilities:
        1. Register engines.
        2. Validate engine metadata.
        3. Lookup engines.
        4. Check engine existence.
        5. List registered engines.
        6. Filter engines by domain/layer/status.
        7. Control basic registry state.

    Non-responsibilities:
        - Engine execution
        - Formula execution
        - Intelligence calculation
        - Trading decision
        - Order execution
        - Risk calculation
    """

    def __init__(self) -> None:
        self._engines: Dict[str, EngineDefinition] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        engine: EngineDefinition,
    ) -> EngineDefinition:
        """
        Register a new engine definition.
        """

        self._validate_definition(engine)

        if engine.engine_id in self._engines:
            raise EngineAlreadyRegisteredError(
                f"Engine already registered: {engine.engine_id}"
            )

        self._engines[engine.engine_id] = engine

        return engine

    # ========================================================
    # REGISTER MANY
    # ========================================================

    def register_many(
        self,
        engines: Iterable[EngineDefinition],
    ) -> tuple[EngineDefinition, ...]:
        """
        Register multiple engines.

        Validation is performed before insertion so that a bad
        definition does not silently enter the registry.
        """

        definitions = tuple(engines)

        for engine in definitions:
            self._validate_definition(engine)

            if engine.engine_id in self._engines:
                raise EngineAlreadyRegisteredError(
                    f"Engine already registered: {engine.engine_id}"
                )

        for engine in definitions:
            self._engines[engine.engine_id] = engine

        return definitions

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        engine_id: str,
    ) -> EngineDefinition:
        """
        Return one registered engine.
        """

        normalized_id = self._normalize_engine_id(engine_id)

        try:
            return self._engines[normalized_id]
        except KeyError as exc:
            raise EngineNotFoundError(
                f"Engine not found: {normalized_id}"
            ) from exc

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        engine_id: str,
    ) -> bool:
        """
        Check whether an engine is registered.
        """

        normalized_id = self._normalize_engine_id(engine_id)

        return normalized_id in self._engines

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return total number of registered engines.
        """

        return len(self._engines)

    # ========================================================
    # LIST ALL
    # ========================================================

    def list_all(self) -> tuple[EngineDefinition, ...]:
        """
        Return all registered engines.
        """

        return tuple(self._engines.values())

    # ========================================================
    # FILTER BY DOMAIN
    # ========================================================

    def list_by_domain(
        self,
        domain: str,
    ) -> tuple[EngineDefinition, ...]:
        """
        Return engines belonging to a specific domain.
        """

        normalized_domain = self._normalize_text(domain, "domain")

        return tuple(
            engine
            for engine in self._engines.values()
            if engine.domain == normalized_domain
        )

    # ========================================================
    # FILTER BY LAYER
    # ========================================================

    def list_by_layer(
        self,
        layer: str,
    ) -> tuple[EngineDefinition, ...]:
        """
        Return engines belonging to a specific architecture layer.
        """

        normalized_layer = self._normalize_text(layer, "layer")

        return tuple(
            engine
            for engine in self._engines.values()
            if engine.layer == normalized_layer
        )

    # ========================================================
    # FILTER BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> tuple[EngineDefinition, ...]:
        """
        Return engines matching a registry status.
        """

        normalized_status = self._normalize_text(status, "status")

        if normalized_status not in VALID_ENGINE_STATUSES:
            raise InvalidEngineDefinitionError(
                f"Invalid engine status: {normalized_status}"
            )

        return tuple(
            engine
            for engine in self._engines.values()
            if engine.status == normalized_status
        )

    # ========================================================
    # INTERNAL VALIDATION
    # ========================================================

    @staticmethod
    def _validate_definition(
        engine: EngineDefinition,
    ) -> None:
        """
        Validate the structural integrity of an engine definition.
        """

        if not isinstance(engine, EngineDefinition):
            raise InvalidEngineDefinitionError(
                "Engine must be an EngineDefinition instance."
            )

        EngineRegistry._normalize_engine_id(engine.engine_id)

        EngineRegistry._normalize_text(
            engine.name,
            "name",
        )

        EngineRegistry._normalize_text(
            engine.version,
            "version",
        )

        EngineRegistry._normalize_text(
            engine.domain,
            "domain",
        )

        EngineRegistry._normalize_text(
            engine.layer,
            "layer",
        )

        if engine.status not in VALID_ENGINE_STATUSES:
            raise InvalidEngineDefinitionError(
                f"Invalid engine status: {engine.status}"
            )

        if not isinstance(engine.dependencies, tuple):
            raise InvalidEngineDefinitionError(
                "Engine dependencies must be a tuple."
            )

        if len(set(engine.dependencies)) != len(engine.dependencies):
            raise InvalidEngineDefinitionError(
                f"Duplicate dependencies found for engine: "
                f"{engine.engine_id}"
            )

        for dependency in engine.dependencies:
            EngineRegistry._normalize_engine_id(dependency)

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize_engine_id(
        engine_id: str,
    ) -> str:
        """
        Normalize and validate an engine identifier.
        """

        if not isinstance(engine_id, str):
            raise InvalidEngineDefinitionError(
                "engine_id must be a string."
            )

        normalized = engine_id.strip()

        if not normalized:
            raise InvalidEngineDefinitionError(
                "engine_id cannot be empty."
            )

        return normalized

    @staticmethod
    def _normalize_text(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normalize required text fields.
        """

        if not isinstance(value, str):
            raise InvalidEngineDefinitionError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise InvalidEngineDefinitionError(
                f"{field_name} cannot be empty."
            )

        return normalized


# ============================================================
# DEFAULT REGISTRY INSTANCE
# ============================================================

engine_registry = EngineRegistry()


# ============================================================
# OPTIONAL REGISTRATION HELPER
# ============================================================


def register_engine(
    engine_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    dependencies: Optional[Iterable[str]] = None,
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: Optional[Iterable[str]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> EngineDefinition:
    """
    Convenience helper for creating and registering an engine.

    This helper only creates metadata and registers it.
    It does not instantiate or execute an engine.
    """

    definition = EngineDefinition(
        engine_id=engine_id.strip(),
        name=name.strip(),
        version=version.strip(),
        domain=domain.strip(),
        layer=layer.strip(),
        description=description.strip(),
        dependencies=tuple(
            dependency.strip()
            for dependency in (dependencies or ())
        ),
        status=status,
        owner=owner.strip(),
        tags=tuple(
            tag.strip()
            for tag in (tags or ())
        ),
        metadata=dict(metadata or {}),
    )

    return engine_registry.register(definition)
# ============================================================
# PART 2 — DEPENDENCY / LIFECYCLE / VERSION / SNAPSHOT
# ============================================================


class EngineDependencyError(EngineRegistryError):
    """Raised when engine dependency integrity fails."""


class EngineVersionError(EngineRegistryError):
    """Raised when an invalid engine version operation is requested."""


class EngineSnapshotError(EngineRegistryError):
    """Raised when registry snapshot generation fails."""


# ============================================================
# ENGINE REGISTRY — PART 2 METHODS
# ============================================================

# IMPORTANT:
# These methods are intentionally attached to EngineRegistry
# after the class definition from Part 1.
#
# They do NOT execute engines.
# They only manage registry metadata and lifecycle state.


def _registry_set_status(
    self: EngineRegistry,
    engine_id: str,
    status: str,
) -> EngineDefinition:
    """
    Change the lifecycle status of a registered engine.

    Allowed states:
        registered
        active
        disabled
        deprecated
    """

    normalized_id = self._normalize_engine_id(engine_id)
    normalized_status = self._normalize_text(status, "status")

    if normalized_status not in VALID_ENGINE_STATUSES:
        raise EngineStateError(
            f"Invalid engine status: {normalized_status}"
        )

    engine = self.get(normalized_id)

    updated = EngineDefinition(
        engine_id=engine.engine_id,
        name=engine.name,
        version=engine.version,
        domain=engine.domain,
        layer=engine.layer,
        description=engine.description,
        dependencies=engine.dependencies,
        status=normalized_status,
        owner=engine.owner,
        tags=engine.tags,
        metadata=dict(engine.metadata),
        registered_at=engine.registered_at,
    )

    self._engines[normalized_id] = updated

    return updated


def _registry_activate(
    self: EngineRegistry,
    engine_id: str,
) -> EngineDefinition:
    """
    Activate a registered engine after dependency validation.
    """

    engine = self.get(engine_id)

    if engine.status == "deprecated":
        raise EngineStateError(
            f"Deprecated engine cannot be activated: "
            f"{engine.engine_id}"
        )

    self.validate_dependencies(engine.engine_id)

    return self.set_status(
        engine.engine_id,
        "active",
    )


def _registry_disable(
    self: EngineRegistry,
    engine_id: str,
) -> EngineDefinition:
    """
    Disable an engine without deleting its registration.
    """

    engine = self.get(engine_id)

    return self.set_status(
        engine.engine_id,
        "disabled",
    )


def _registry_deprecate(
    self: EngineRegistry,
    engine_id: str,
) -> EngineDefinition:
    """
    Mark an engine as deprecated.

    Deprecated engines remain visible for audit/reference
    but cannot be activated.
    """

    engine = self.get(engine_id)

    return self.set_status(
        engine.engine_id,
        "deprecated",
    )


# ============================================================
# DEPENDENCY VALIDATION
# ============================================================


def _registry_validate_dependencies(
    self: EngineRegistry,
    engine_id: str,
) -> bool:
    """
    Validate that all declared dependencies exist.

    This checks registration integrity only.

    It does NOT execute dependencies.
    """

    engine = self.get(engine_id)

    missing = [
        dependency
        for dependency in engine.dependencies
        if dependency not in self._engines
    ]

    if missing:
        raise EngineDependencyError(
            f"Missing dependencies for "
            f"{engine.engine_id}: {missing}"
        )

    return True


def _registry_validate_all_dependencies(
    self: EngineRegistry,
) -> dict[str, list[str]]:
    """
    Validate dependencies for every registered engine.

    Returns:

        {
            "valid": [...],
            "invalid": [...]
        }

    Invalid entries contain engine IDs whose dependencies
    cannot be resolved.
    """

    valid: list[str] = []
    invalid: list[str] = []

    for engine in self._engines.values():
        try:
            self.validate_dependencies(engine.engine_id)
            valid.append(engine.engine_id)
        except EngineDependencyError:
            invalid.append(engine.engine_id)

    return {
        "valid": valid,
        "invalid": invalid,
    }


# ============================================================
# DEPENDENCY GRAPH
# ============================================================


def _registry_dependency_graph(
    self: EngineRegistry,
) -> dict[str, tuple[str, ...]]:
    """
    Return the declared dependency graph.

    Example:

        {
            "decision_engine": ("evidence_engine",),
            "evidence_engine": ()
        }
    """

    return {
        engine.engine_id: tuple(engine.dependencies)
        for engine in self._engines.values()
    }


# ============================================================
# DEPENDENT ENGINES
# ============================================================


def _registry_dependents(
    self: EngineRegistry,
    engine_id: str,
) -> tuple[str, ...]:
    """
    Find engines that directly depend on the supplied engine.
    """

    normalized_id = self._normalize_engine_id(engine_id)

    # Ensure requested engine exists.
    self.get(normalized_id)

    return tuple(
        engine.engine_id
        for engine in self._engines.values()
        if normalized_id in engine.dependencies
    )


# ============================================================
# CIRCULAR DEPENDENCY DETECTION
# ============================================================


def _registry_detect_cycles(
    self: EngineRegistry,
) -> tuple[tuple[str, ...], ...]:
    """
    Detect circular dependencies in the registry.

    Returns a tuple of detected dependency cycles.

    Example:

        (
            ("engine_a", "engine_b", "engine_a"),
        )
    """

    graph = self.dependency_graph()

    cycles: list[tuple[str, ...]] = []

    visited: set[str] = set()
    active_path: list[str] = []
    active_set: set[str] = set()

    def visit(node: str) -> None:
        if node in active_set:
            start = active_path.index(node)
            cycle = tuple(active_path[start:] + [node])

            if cycle not in cycles:
                cycles.append(cycle)

            return

        if node in visited:
            return

        visited.add(node)
        active_set.add(node)
        active_path.append(node)

        for dependency in graph.get(node, ()):
            if dependency in graph:
                visit(dependency)

        active_path.pop()
        active_set.remove(node)

    for node in graph:
        visit(node)

    return tuple(cycles)


def _registry_assert_no_cycles(
    self: EngineRegistry,
) -> bool:
    """
    Fail if circular engine dependencies exist.
    """

    cycles = self.detect_cycles()

    if cycles:
        raise EngineDependencyError(
            f"Circular engine dependencies detected: {cycles}"
        )

    return True


# ============================================================
# VERSION REPLACEMENT
# ============================================================


def _registry_replace(
    self: EngineRegistry,
    engine: EngineDefinition,
) -> EngineDefinition:
    """
    Replace an existing engine registration with a new definition.

    This operation changes registry metadata only.

    It does NOT migrate runtime state.
    It does NOT execute the new engine.
    """

    self._validate_definition(engine)

    if engine.engine_id not in self._engines:
        raise EngineNotFoundError(
            f"Cannot replace unregistered engine: "
            f"{engine.engine_id}"
        )

    existing = self._engines[engine.engine_id]

    if engine.version == existing.version:
        raise EngineVersionError(
            f"Replacement version is unchanged for "
            f"{engine.engine_id}: {engine.version}"
        )

    self._engines[engine.engine_id] = engine

    return engine


# ============================================================
# SNAPSHOT
# ============================================================


def _registry_snapshot(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Produce a serializable registry snapshot.

    Snapshot is intended for:
        - audit
        - diagnostics
        - testing
        - deployment inspection
        - registry verification
    """

    engines = []

    for engine in self._engines.values():
        engines.append(
            {
                "engine_id": engine.engine_id,
                "name": engine.name,
                "version": engine.version,
                "domain": engine.domain,
                "layer": engine.layer,
                "description": engine.description,
                "dependencies": list(engine.dependencies),
                "status": engine.status,
                "owner": engine.owner,
                "tags": list(engine.tags),
                "metadata": dict(engine.metadata),
                "registered_at": engine.registered_at.isoformat(),
            }
        )

    dependency_check = self.validate_all_dependencies()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "engine_count": len(engines),
        "engines": engines,
        "dependency_validation": dependency_check,
        "cycles": [
            list(cycle)
            for cycle in self.detect_cycles()
        ],
    }


# ============================================================
# REGISTRY HEALTH
# ============================================================


def _registry_health(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Return structural health information for the registry.

    This is registry health, NOT market health.
    """

    dependency_validation = self.validate_all_dependencies()
    cycles = self.detect_cycles()

    active_count = len(
        self.list_by_status("active")
    )

    disabled_count = len(
        self.list_by_status("disabled")
    )

    deprecated_count = len(
        self.list_by_status("deprecated")
    )

    registered_count = len(
        self.list_by_status("registered")
    )

    healthy = (
        len(dependency_validation["invalid"]) == 0
        and len(cycles) == 0
    )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "engine_count": self.count(),
        "active_count": active_count,
        "registered_count": registered_count,
        "disabled_count": disabled_count,
        "deprecated_count": deprecated_count,
        "dependency_validation": dependency_validation,
        "cycle_count": len(cycles),
    }


# ============================================================
# BIND PART 2 METHODS TO ENGINE REGISTRY
# ============================================================

EngineRegistry.set_status = _registry_set_status
EngineRegistry.activate = _registry_activate
EngineRegistry.disable = _registry_disable
EngineRegistry.deprecate = _registry_deprecate

EngineRegistry.validate_dependencies = (
    _registry_validate_dependencies
)

EngineRegistry.validate_all_dependencies = (
    _registry_validate_all_dependencies
)

EngineRegistry.dependency_graph = (
    _registry_dependency_graph
)

EngineRegistry.dependents = (
    _registry_dependents
)

EngineRegistry.detect_cycles = (
    _registry_detect_cycles
)

EngineRegistry.assert_no_cycles = (
    _registry_assert_no_cycles
)

EngineRegistry.replace = (
    _registry_replace
)

EngineRegistry.snapshot = (
    _registry_snapshot
)

EngineRegistry.health = (
    _registry_health
)
# ============================================================
# PART 3 — BOOTSTRAP / CONTROLLED DISCOVERY / REGISTRY CONTROL
# ============================================================


class EngineRegistrationConflictError(EngineRegistryError):
    """Raised when an engine registration conflicts with an
    existing registry definition."""


class EngineUnregisterError(EngineRegistryError):
    """Raised when an engine cannot safely be unregistered."""


class EngineBootstrapError(EngineRegistryError):
    """Raised when registry bootstrap fails."""


# ============================================================
# REGISTRATION CONFLICT CHECK
# ============================================================


def _registry_check_conflict(
    self: EngineRegistry,
    engine: EngineDefinition,
) -> bool:
    """
    Check whether an engine definition conflicts with an
    already registered engine.

    Returns:
        True  -> no conflict
        False -> engine does not currently exist

    Raises:
        EngineRegistrationConflictError
    """

    self._validate_definition(engine)

    existing = self._engines.get(engine.engine_id)

    if existing is None:
        return False

    # Same engine ID + same version + materially different
    # definition = hard conflict.
    if existing.version == engine.version:

        if (
            existing.name != engine.name
            or existing.domain != engine.domain
            or existing.layer != engine.layer
            or existing.dependencies != engine.dependencies
            or existing.status != engine.status
        ):
            raise EngineRegistrationConflictError(
                "Conflicting engine definition detected for "
                f"{engine.engine_id} version {engine.version}."
            )

        # Exact same definition is idempotent.
        return True

    return True


# ============================================================
# SAFE REGISTER
# ============================================================


def _registry_register_safe(
    self: EngineRegistry,
    engine: EngineDefinition,
) -> EngineDefinition:
    """
    Register an engine using conflict protection.

    If the exact same definition already exists, the existing
    definition is returned.

    A conflicting definition raises an exception.
    """

    existing = self._engines.get(engine.engine_id)

    if existing is None:
        return self.register(engine)

    self.check_conflict(engine)

    return existing


# ============================================================
# DEPENDENCY-SAFE REGISTER
# ============================================================


def _registry_register_with_dependencies(
    self: EngineRegistry,
    engine: EngineDefinition,
) -> EngineDefinition:
    """
    Register an engine while verifying dependency references.

    Important:
        Dependencies must already be registered.

    This prevents the registry from silently accepting an
    unresolved dependency graph.
    """

    self._validate_definition(engine)

    existing = self._engines.get(engine.engine_id)

    if existing is not None:
        self.check_conflict(engine)
        return existing

    missing = [
        dependency
        for dependency in engine.dependencies
        if dependency not in self._engines
    ]

    if missing:
        raise EngineDependencyError(
            "Cannot register engine because dependencies are "
            f"not registered: {engine.engine_id} -> {missing}"
        )

    return self.register(engine)


# ============================================================
# CONTROLLED DISCOVERY
# ============================================================


def _registry_find(
    self: EngineRegistry,
    *,
    domain: Optional[str] = None,
    layer: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
) -> tuple[EngineDefinition, ...]:
    """
    Controlled metadata discovery.

    This method only searches registry metadata.

    It does NOT inspect or execute engine intelligence.
    """

    results = list(self._engines.values())

    if domain is not None:
        normalized_domain = self._normalize_text(
            domain,
            "domain",
        )

        results = [
            engine
            for engine in results
            if engine.domain == normalized_domain
        ]

    if layer is not None:
        normalized_layer = self._normalize_text(
            layer,
            "layer",
        )

        results = [
            engine
            for engine in results
            if engine.layer == normalized_layer
        ]

    if status is not None:
        normalized_status = self._normalize_text(
            status,
            "status",
        )

        if normalized_status not in VALID_ENGINE_STATUSES:
            raise InvalidEngineDefinitionError(
                f"Invalid engine status: {normalized_status}"
            )

        results = [
            engine
            for engine in results
            if engine.status == normalized_status
        ]

    if tag is not None:
        normalized_tag = self._normalize_text(
            tag,
            "tag",
        )

        results = [
            engine
            for engine in results
            if normalized_tag in engine.tags
        ]

    return tuple(results)


# ============================================================
# FIND BY ID PREFIX
# ============================================================


def _registry_find_by_prefix(
    self: EngineRegistry,
    prefix: str,
) -> tuple[EngineDefinition, ...]:
    """
    Find engines by engine ID prefix.

    Useful for controlled architectural grouping.
    """

    normalized_prefix = self._normalize_text(
        prefix,
        "prefix",
    )

    return tuple(
        engine
        for engine in self._engines.values()
        if engine.engine_id.startswith(normalized_prefix)
    )


# ============================================================
# ENGINE IDS
# ============================================================


def _registry_engine_ids(
    self: EngineRegistry,
) -> tuple[str, ...]:
    """
    Return registered engine IDs in deterministic order.
    """

    return tuple(
        sorted(self._engines.keys())
    )


# ============================================================
# UNREGISTER
# ============================================================


def _registry_unregister(
    self: EngineRegistry,
    engine_id: str,
    *,
    force: bool = False,
) -> EngineDefinition:
    """
    Remove an engine from the registry.

    Safety rule:
        An engine cannot be removed while another registered
        engine depends on it unless force=True.

    This only changes registry metadata.
    """

    normalized_id = self._normalize_engine_id(
        engine_id
    )

    engine = self.get(normalized_id)

    dependents = self.dependents(normalized_id)

    if dependents and not force:
        raise EngineUnregisterError(
            f"Cannot unregister {normalized_id}; "
            f"dependent engines exist: {dependents}"
        )

    del self._engines[normalized_id]

    return engine


# ============================================================
# CLEAR REGISTRY
# ============================================================


def _registry_clear(
    self: EngineRegistry,
    *,
    force: bool = False,
) -> int:
    """
    Clear registry contents.

    Normally intended for:
        - isolated tests
        - controlled bootstrap
        - development reset

    Production callers should not clear a live registry
    without explicit force=True.
    """

    if self.count() == 0:
        return 0

    if not force:
        raise EngineRegistryError(
            "Registry clear requires force=True."
        )

    count = self.count()

    self._engines.clear()

    return count


# ============================================================
# BOOTSTRAP VALIDATION
# ============================================================


def _registry_validate_bootstrap(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Validate whether the registry is structurally ready.

    Checks:
        1. Dependency resolution
        2. Circular dependencies
        3. Duplicate IDs
        4. Invalid statuses
    """

    errors: list[str] = []

    # --------------------------------------------------------
    # Dependency validation
    # --------------------------------------------------------

    dependency_result = self.validate_all_dependencies()

    if dependency_result["invalid"]:
        errors.append(
            "Unresolved dependencies: "
            + ", ".join(
                dependency_result["invalid"]
            )
        )

    # --------------------------------------------------------
    # Circular dependency validation
    # --------------------------------------------------------

    cycles = self.detect_cycles()

    if cycles:
        errors.append(
            f"Circular dependencies detected: {cycles}"
        )

    # --------------------------------------------------------
    # Status validation
    # --------------------------------------------------------

    invalid_status_engines = [
        engine.engine_id
        for engine in self._engines.values()
        if engine.status not in VALID_ENGINE_STATUSES
    ]

    if invalid_status_engines:
        errors.append(
            "Invalid engine statuses: "
            + ", ".join(invalid_status_engines)
        )

    return {
        "ready": len(errors) == 0,
        "engine_count": self.count(),
        "errors": errors,
        "dependency_validation": dependency_result,
        "cycles": [
            list(cycle)
            for cycle in cycles
        ],
    }


# ============================================================
# BOOTSTRAP
# ============================================================


def _registry_bootstrap(
    self: EngineRegistry,
    engines: Iterable[EngineDefinition],
    *,
    activate: bool = False,
) -> dict[str, Any]:
    """
    Controlled registry bootstrap.

    Registration order must respect dependencies.

    Example:

        evidence_engine
            ↓
        context_engine
            ↓
        decision_engine

    The registry does not instantiate or execute these engines.
    """

    definitions = tuple(engines)

    # --------------------------------------------------------
    # Phase 1 — Validate all definitions before mutation
    # --------------------------------------------------------

    seen_ids: set[str] = set()

    for engine in definitions:

        self._validate_definition(engine)

        if engine.engine_id in seen_ids:
            raise EngineBootstrapError(
                "Duplicate engine ID in bootstrap batch: "
                f"{engine.engine_id}"
            )

        seen_ids.add(engine.engine_id)

    # --------------------------------------------------------
    # Phase 2 — Register dependency-safe
    # --------------------------------------------------------

    registered: list[str] = []
    pending = list(definitions)

    while pending:

        progress = False
        unresolved: list[EngineDefinition] = []

        for engine in pending:

            missing = [
                dependency
                for dependency in engine.dependencies
                if dependency not in self._engines
                and dependency not in seen_ids
            ]

            # Dependency exists outside this bootstrap batch.
            if not missing:
                try:
                    self.register_safe(engine)

                    registered.append(
                        engine.engine_id
                    )

                    progress = True

                except EngineRegistrationConflictError:
                    raise

            else:
                unresolved.append(engine)

        # ----------------------------------------------------
        # No progress means dependency graph cannot resolve.
        # ----------------------------------------------------

        if unresolved and not progress:

            unresolved_map = {
                engine.engine_id: [
                    dependency
                    for dependency in engine.dependencies
                    if dependency not in self._engines
                ]
                for engine in unresolved
            }

            raise EngineBootstrapError(
                "Unable to resolve bootstrap dependency order: "
                f"{unresolved_map}"
            )

        pending = unresolved

    # --------------------------------------------------------
    # Phase 3 — Validate complete graph
    # --------------------------------------------------------

    validation = self.validate_bootstrap()

    if not validation["ready"]:
        raise EngineBootstrapError(
            "Registry bootstrap validation failed: "
            f"{validation['errors']}"
        )

    # --------------------------------------------------------
    # Phase 4 — Optional activation
    # --------------------------------------------------------

    activated: list[str] = []

    if activate:

        for engine_id in registered:

            engine = self.get(engine_id)

            if engine.status == "registered":

                self.activate(engine_id)

                activated.append(engine_id)

    return {
        "success": True,
        "registered": registered,
        "activated": activated,
        "engine_count": self.count(),
        "validation": self.validate_bootstrap(),
    }


# ============================================================
# ACTIVE ENGINE DISCOVERY
# ============================================================


def _registry_active_engines(
    self: EngineRegistry,
) -> tuple[EngineDefinition, ...]:
    """
    Return only currently active engines.
    """

    return self.list_by_status("active")


# ============================================================
# REGISTRATION SUMMARY
# ============================================================


def _registry_summary(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Return a compact registry summary.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "engine_count": self.count(),
        "engine_ids": self.engine_ids(),
        "active": len(
            self.list_by_status("active")
        ),
        "registered": len(
            self.list_by_status("registered")
        ),
        "disabled": len(
            self.list_by_status("disabled")
        ),
        "deprecated": len(
            self.list_by_status("deprecated")
        ),
    }


# ============================================================
# BIND PART 3 METHODS
# ============================================================

EngineRegistry.check_conflict = (
    _registry_check_conflict
)

EngineRegistry.register_safe = (
    _registry_register_safe
)

EngineRegistry.register_with_dependencies = (
    _registry_register_with_dependencies
)

EngineRegistry.find = (
    _registry_find
)

EngineRegistry.find_by_prefix = (
    _registry_find_by_prefix
)

EngineRegistry.engine_ids = (
    _registry_engine_ids
)

EngineRegistry.unregister = (
    _registry_unregister
)

EngineRegistry.clear = (
    _registry_clear
)

EngineRegistry.validate_bootstrap = (
    _registry_validate_bootstrap
)

EngineRegistry.bootstrap = (
    _registry_bootstrap
)

EngineRegistry.active_engines = (
    _registry_active_engines
)

EngineRegistry.summary = (
    _registry_summary
)
# ============================================================
# PART 4 — CANONICAL REGISTRATION SPECIFICATION
#           + CONTROLLED REGISTRATION DECORATOR
#           + REGISTRATION DISCOVERY
# ============================================================

from dataclasses import asdict
from functools import wraps
from typing import Type


# ============================================================
# REGISTRATION METADATA
# ============================================================


@dataclass(frozen=True)
class EngineRegistrationSpec:
    """
    Declarative registration specification.

    This describes HOW an engine should be registered.

    It does not execute the engine and does not contain
    intelligence or trading calculations.
    """

    engine_id: str
    name: str
    version: str
    domain: str
    layer: str

    description: str = ""

    dependencies: tuple[str, ...] = field(
        default_factory=tuple
    )

    status: str = "registered"

    owner: str = "ROBOMLM"

    tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# SPEC VALIDATION
# ============================================================


def _validate_registration_spec(
    spec: EngineRegistrationSpec,
) -> None:
    """
    Validate registration specification before conversion
    into an EngineDefinition.
    """

    if not isinstance(
        spec,
        EngineRegistrationSpec,
    ):
        raise InvalidEngineDefinitionError(
            "Registration spec must be "
            "EngineRegistrationSpec."
        )

    EngineRegistry._normalize_engine_id(
        spec.engine_id
    )

    EngineRegistry._normalize_text(
        spec.name,
        "name",
    )

    EngineRegistry._normalize_text(
        spec.version,
        "version",
    )

    EngineRegistry._normalize_text(
        spec.domain,
        "domain",
    )

    EngineRegistry._normalize_text(
        spec.layer,
        "layer",
    )

    if spec.status not in VALID_ENGINE_STATUSES:
        raise InvalidEngineDefinitionError(
            f"Invalid registration status: "
            f"{spec.status}"
        )

    dependency_ids = tuple(spec.dependencies)

    if len(set(dependency_ids)) != len(dependency_ids):
        raise InvalidEngineDefinitionError(
            f"Duplicate dependencies in registration spec: "
            f"{spec.engine_id}"
        )

    for dependency in dependency_ids:
        EngineRegistry._normalize_engine_id(
            dependency
        )


# ============================================================
# SPEC → ENGINE DEFINITION
# ============================================================


def _spec_to_definition(
    spec: EngineRegistrationSpec,
) -> EngineDefinition:
    """
    Convert a declarative registration specification into
    the registry's immutable EngineDefinition.
    """

    _validate_registration_spec(spec)

    return EngineDefinition(
        engine_id=spec.engine_id.strip(),
        name=spec.name.strip(),
        version=spec.version.strip(),
        domain=spec.domain.strip(),
        layer=spec.layer.strip(),
        description=spec.description.strip(),
        dependencies=tuple(
            dependency.strip()
            for dependency in spec.dependencies
        ),
        status=spec.status,
        owner=spec.owner.strip(),
        tags=tuple(
            tag.strip()
            for tag in spec.tags
        ),
        metadata=dict(spec.metadata),
    )


# ============================================================
# SPEC REGISTRATION
# ============================================================


def _registry_register_spec(
    self: EngineRegistry,
    spec: EngineRegistrationSpec,
) -> EngineDefinition:
    """
    Register an EngineRegistrationSpec safely.
    """

    definition = _spec_to_definition(spec)

    return self.register_safe(definition)


# ============================================================
# SPEC BATCH REGISTRATION
# ============================================================


def _registry_register_specs(
    self: EngineRegistry,
    specs: Iterable[EngineRegistrationSpec],
) -> tuple[EngineDefinition, ...]:
    """
    Register multiple specifications.

    Existing identical definitions are accepted.
    Conflicts are rejected.
    """

    definitions = tuple(
        _spec_to_definition(spec)
        for spec in specs
    )

    registered: list[EngineDefinition] = []

    for definition in definitions:

        result = self.register_safe(
            definition
        )

        registered.append(result)

    return tuple(registered)


# ============================================================
# DECORATOR REGISTRATION
# ============================================================


_ENGINE_REGISTRATION_SPECS: dict[
    str,
    EngineRegistrationSpec,
] = {}


def engine_spec(
    *,
    engine_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    dependencies: Iterable[str] = (),
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: Iterable[str] = (),
    metadata: Optional[Mapping[str, Any]] = None,
) -> Callable:

    """
    Declarative engine registration decorator.

    Example:

        @engine_spec(
            engine_id="example_engine",
            name="Example Engine",
            version="1.0.0",
            domain="example",
            layer="intelligence",
        )
        class ExampleEngine:
            ...

    The decorator ONLY records metadata.

    It does NOT:
        - instantiate the class
        - execute the class
        - run formulas
        - generate signals
        - make decisions
    """

    spec = EngineRegistrationSpec(
        engine_id=engine_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        dependencies=tuple(dependencies),
        status=status,
        owner=owner,
        tags=tuple(tags),
        metadata=dict(metadata or {}),
    )

    _validate_registration_spec(spec)

    def decorator(
        engine_class: Type[Any],
    ) -> Type[Any]:

        existing = _ENGINE_REGISTRATION_SPECS.get(
            spec.engine_id
        )

        if existing is not None:
            if existing != spec:
                raise EngineRegistrationConflictError(
                    "Conflicting decorator registration "
                    f"for engine: {spec.engine_id}"
                )

        _ENGINE_REGISTRATION_SPECS[
            spec.engine_id
        ] = spec

        # Attach metadata only.
        setattr(
            engine_class,
            "__robomlm_engine_spec__",
            spec,
        )

        return engine_class

    return decorator


# ============================================================
# DISCOVER DECLARED SPECS
# ============================================================


def discover_engine_specs() -> tuple[
    EngineRegistrationSpec,
    ...,
]:
    """
    Return all declaratively registered engine specs.

    Deterministic ordering is used for reproducibility.
    """

    return tuple(
        _ENGINE_REGISTRATION_SPECS[
            engine_id
        ]
        for engine_id in sorted(
            _ENGINE_REGISTRATION_SPECS
        )
    )


# ============================================================
# DISCOVER ONE SPEC
# ============================================================


def get_engine_spec(
    engine_id: str,
) -> EngineRegistrationSpec:
    """
    Retrieve one declaratively registered specification.
    """

    normalized_id = EngineRegistry._normalize_engine_id(
        engine_id
    )

    try:
        return _ENGINE_REGISTRATION_SPECS[
            normalized_id
        ]
    except KeyError as exc:
        raise EngineNotFoundError(
            "Engine registration specification not found: "
            f"{normalized_id}"
        ) from exc


# ============================================================
# REGISTER DISCOVERED SPECS
# ============================================================


def _registry_register_discovered(
    self: EngineRegistry,
) -> tuple[EngineDefinition, ...]:
    """
    Register all engine specifications declared through
    @engine_spec.

    The registry remains responsible for validation and
    conflict protection.
    """

    specs = discover_engine_specs()

    if not specs:
        return ()

    return self.register_specs(specs)


# ============================================================
# DISCOVERY REPORT
# ============================================================


def _registry_discovery_report(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Return a controlled report comparing:

        Declared specifications
                  vs
        Registry registrations
    """

    declared_ids = {
        spec.engine_id
        for spec in discover_engine_specs()
    }

    registered_ids = set(
        self.engine_ids()
    )

    declared_but_not_registered = sorted(
        declared_ids - registered_ids
    )

    registered_but_not_declared = sorted(
        registered_ids - declared_ids
    )

    return {
        "declared_count": len(
            declared_ids
        ),
        "registered_count": len(
            registered_ids
        ),
        "declared_but_not_registered":
            declared_but_not_registered,
        "registered_but_not_declared":
            registered_but_not_declared,
        "consistent": (
            not declared_but_not_registered
            and not registered_but_not_declared
        ),
    }


# ============================================================
# ENGINE METADATA EXPORT
# ============================================================


def _registry_export_metadata(
    self: EngineRegistry,
) -> tuple[dict[str, Any], ...]:
    """
    Return deterministic metadata records for every
    registered engine.
    """

    records: list[dict[str, Any]] = []

    for engine_id in self.engine_ids():

        engine = self.get(engine_id)

        record = {
            "engine_id": engine.engine_id,
            "name": engine.name,
            "version": engine.version,
            "domain": engine.domain,
            "layer": engine.layer,
            "description": engine.description,
            "dependencies": list(
                engine.dependencies
            ),
            "status": engine.status,
            "owner": engine.owner,
            "tags": list(engine.tags),
            "metadata": dict(
                engine.metadata
            ),
            "registered_at":
                engine.registered_at.isoformat(),
        }

        records.append(record)

    return tuple(records)


# ============================================================
# REGISTRY CONSISTENCY CHECK
# ============================================================


def _registry_consistency_check(
    self: EngineRegistry,
) -> dict[str, Any]:
    """
    Perform a structural consistency audit.

    Checks:

        1. Registry definitions
        2. Dependency references
        3. Dependency cycles
        4. Declarative discovery
    """

    bootstrap = self.validate_bootstrap()
    discovery = self.discovery_report()

    errors: list[str] = []

    if not bootstrap["ready"]:
        errors.extend(
            bootstrap["errors"]
        )

    if not discovery["consistent"]:
        errors.append(
            "Declarative registration and registry "
            "registration are inconsistent."
        )

    return {
        "consistent": len(errors) == 0,
        "errors": errors,
        "bootstrap": bootstrap,
        "discovery": discovery,
    }


# ============================================================
# BIND PART 4 METHODS
# ============================================================


EngineRegistry.register_spec = (
    _registry_register_spec
)

EngineRegistry.register_specs = (
    _registry_register_specs
)

EngineRegistry.register_discovered = (
    _registry_register_discovered
)

EngineRegistry.discovery_report = (
    _registry_discovery_report
)

EngineRegistry.export_metadata = (
    _registry_export_metadata
)

EngineRegistry.consistency_check = (
    _registry_consistency_check
)
# ============================================================
# PART 5 — ROBOMLM PLUS CANONICAL ENGINE CATALOG
# ============================================================
#
# IMPORTANT ARCHITECTURE RULE
#
# This section registers CANONICAL ENGINE METADATA only.
#
# It intentionally does NOT:
#   - import engine implementation classes
#   - instantiate engines
#   - execute engines
#   - calculate formulas
#   - generate trading signals
#   - make decisions
#   - execute trades
#
# Implementation modules remain responsible for their own logic.
# The registry only provides controlled identity and discovery.
# ============================================================


# ============================================================
# CANONICAL DOMAINS
# ============================================================

ENGINE_DOMAIN_CORE = "core"
ENGINE_DOMAIN_EVIDENCE = "evidence"
ENGINE_DOMAIN_CONTEXT = "context"
ENGINE_DOMAIN_DECISION = "decision"
ENGINE_DOMAIN_RISK = "risk"
ENGINE_DOMAIN_CAS = "cas"
ENGINE_DOMAIN_MEMORY = "memory"
ENGINE_DOMAIN_OPPORTUNITY = "opportunity"
ENGINE_DOMAIN_RESEARCH = "research"
ENGINE_DOMAIN_AUTOMATION = "automation"
ENGINE_DOMAIN_INTELLIGENCE = "intelligence"
ENGINE_DOMAIN_METRICS = "metrics"


# ============================================================
# CANONICAL ARCHITECTURE LAYERS
# ============================================================

ENGINE_LAYER_FOUNDATION = "foundation"
ENGINE_LAYER_EVIDENCE = "evidence"
ENGINE_LAYER_CONTEXT = "context"
ENGINE_LAYER_DECISION = "decision"
ENGINE_LAYER_RISK = "risk"
ENGINE_LAYER_CONTROL = "control"
ENGINE_LAYER_MEMORY = "memory"
ENGINE_LAYER_OPPORTUNITY = "opportunity"
ENGINE_LAYER_RESEARCH = "research"
ENGINE_LAYER_AUTOMATION = "automation"
ENGINE_LAYER_METRICS = "metrics"
ENGINE_LAYER_ORCHESTRATION = "orchestration"


# ============================================================
# CANONICAL ENGINE CATALOG
# ============================================================
#
# NOTE:
# Dependencies here represent ARCHITECTURAL dependencies only.
# They are registry references, not Python imports.
# ============================================================


ROBOMLM_CANONICAL_ENGINE_SPECS = (
    # --------------------------------------------------------
    # CORE INTELLIGENCE ORCHESTRATION
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="intelligence_orchestrator",
        name="Intelligence Orchestrator",
        version="1.0.0",
        domain=ENGINE_DOMAIN_INTELLIGENCE,
        layer=ENGINE_LAYER_ORCHESTRATION,
        description=(
            "Coordinates the intelligence processing flow "
            "across the ROBOMLM intelligence architecture."
        ),
        dependencies=(
            "evidence_orchestrator",
            "decision_orchestrator",
        ),
        tags=(
            "orchestrator",
            "intelligence",
            "core",
        ),
    ),

    EngineRegistrationSpec(
        engine_id="evidence_orchestrator",
        name="Evidence Orchestrator",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_ORCHESTRATION,
        description=(
            "Coordinates evidence generation, normalization, "
            "conflict handling and evidence packaging."
        ),
        dependencies=(
            "evidence_normalizer",
            "evidence_conflict",
            "evidence_confidence",
        ),
        tags=(
            "orchestrator",
            "evidence",
        ),
    ),

    EngineRegistrationSpec(
        engine_id="decision_orchestrator",
        name="Decision Orchestrator",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_ORCHESTRATION,
        description=(
            "Coordinates the Decision Cortex processing chain."
        ),
        dependencies=(
            "decision_readiness",
            "decision_condition",
            "decision_confidence",
            "decision_structure",
            "decision_flow",
            "decision_market_state",
            "decision_transition",
            "decision_future_scenario",
            "decision_decision",
            "decision_validation",
            "decision_learning",
            "decision_intelligence",
        ),
        tags=(
            "orchestrator",
            "decision",
            "decision-cortex",
        ),
    ),

    # --------------------------------------------------------
    # EVIDENCE CORTEX
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="ned",
        name="NED Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="NED evidence processing engine.",
        tags=("evidence", "ned"),
    ),

    EngineRegistrationSpec(
        engine_id="dar",
        name="DAR Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="DAR evidence processing engine.",
        dependencies=("ned",),
        tags=("evidence", "dar"),
    ),

    EngineRegistrationSpec(
        engine_id="tv",
        name="TV Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="TV evidence processing engine.",
        dependencies=("dar",),
        tags=("evidence", "tv"),
    ),

    EngineRegistrationSpec(
        engine_id="oxe",
        name="OXE Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="OXE evidence processing engine.",
        dependencies=("tv",),
        tags=("evidence", "oxe"),
    ),

    EngineRegistrationSpec(
        engine_id="mbc",
        name="MBC Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="MBC evidence processing engine.",
        dependencies=("oxe",),
        tags=("evidence", "mbc"),
    ),

    EngineRegistrationSpec(
        engine_id="mkn",
        name="MKN Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="MKN evidence processing engine.",
        dependencies=("mbc",),
        tags=("evidence", "mkn"),
    ),

    EngineRegistrationSpec(
        engine_id="ace",
        name="ACE Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="ACE evidence processing engine.",
        dependencies=("mkn",),
        tags=("evidence", "ace"),
    ),

    EngineRegistrationSpec(
        engine_id="msdl",
        name="MSDL Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="MSDL evidence processing engine.",
        dependencies=("ace",),
        tags=("evidence", "msdl"),
    ),

    EngineRegistrationSpec(
        engine_id="dcs",
        name="DCS Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="DCS evidence processing engine.",
        dependencies=("msdl",),
        tags=("evidence", "dcs"),
    ),

    EngineRegistrationSpec(
        engine_id="mdil",
        name="MDIL Evidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="MDIL evidence processing engine.",
        dependencies=("dcs",),
        tags=("evidence", "mdil"),
    ),

    EngineRegistrationSpec(
        engine_id="source_reliability",
        name="Source Reliability Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description=(
            "Evaluates reliability metadata associated "
            "with evidence sources."
        ),
        dependencies=("mdil",),
        tags=(
            "evidence",
            "reliability",
        ),
    ),

    EngineRegistrationSpec(
        engine_id="evidence_normalizer",
        name="Evidence Normalizer",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="Normalizes evidence into a common representation.",
        dependencies=("source_reliability",),
        tags=("evidence", "normalization"),
    ),

    EngineRegistrationSpec(
        engine_id="evidence_conflict",
        name="Evidence Conflict Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="Handles conflicting evidence states.",
        dependencies=("evidence_normalizer",),
        tags=("evidence", "conflict"),
    ),

    EngineRegistrationSpec(
        engine_id="evidence_confidence",
        name="Evidence Confidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_EVIDENCE,
        layer=ENGINE_LAYER_EVIDENCE,
        description="Determines evidence confidence metadata.",
        dependencies=("evidence_conflict",),
        tags=("evidence", "confidence"),
    ),

    # --------------------------------------------------------
    # MARKET CONTEXT
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="market_context",
        name="Market Context Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CONTEXT,
        layer=ENGINE_LAYER_CONTEXT,
        description=(
            "Builds structured market context from validated "
            "evidence."
        ),
        dependencies=(
            "evidence_orchestrator",
        ),
        tags=(
            "context",
            "market-context",
        ),
    ),

    EngineRegistrationSpec(
        engine_id="regime_intelligence",
        name="Regime Intelligence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CONTEXT,
        layer=ENGINE_LAYER_CONTEXT,
        description="Market regime intelligence.",
        dependencies=("market_context",),
        tags=("context", "regime"),
    ),

    EngineRegistrationSpec(
        engine_id="relationship_intelligence",
        name="Relationship Intelligence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CONTEXT,
        layer=ENGINE_LAYER_CONTEXT,
        description="Cross-market and instrument relationship intelligence.",
        dependencies=("market_context",),
        tags=("context", "relationship"),
    ),

    EngineRegistrationSpec(
        engine_id="timing_intelligence",
        name="Timing Intelligence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CONTEXT,
        layer=ENGINE_LAYER_CONTEXT,
        description="Market timing intelligence.",
        dependencies=("market_context",),
        tags=("context", "timing"),
    ),

    # --------------------------------------------------------
    # OPPORTUNITY INTELLIGENCE
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="opportunity_intelligence",
        name="Opportunity Intelligence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_OPPORTUNITY,
        layer=ENGINE_LAYER_OPPORTUNITY,
        description=(
            "Transforms validated market context into "
            "candidate opportunity intelligence."
        ),
        dependencies=(
            "market_context",
            "regime_intelligence",
            "relationship_intelligence",
            "timing_intelligence",
        ),
        tags=(
            "opportunity",
            "intelligence",
        ),
    ),

    EngineRegistrationSpec(
        engine_id="magnitude_engine",
        name="Magnitude Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_INTELLIGENCE,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates opportunity magnitude.",
        dependencies=(
            "opportunity_intelligence",
        ),
        tags=("intelligence", "magnitude"),
    ),

    # --------------------------------------------------------
    # DECISION CORTEX
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="decision_readiness",
        name="Decision Readiness Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates whether sufficient conditions exist for decision processing.",
        dependencies=("market_context",),
        tags=("decision", "readiness"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_condition",
        name="Decision Condition Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates decision conditions.",
        dependencies=("decision_readiness",),
        tags=("decision", "condition"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_confidence",
        name="Decision Confidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates decision confidence.",
        dependencies=("decision_condition",),
        tags=("decision", "confidence"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_relationships",
        name="Decision Relationships Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates decision-level relationships.",
        dependencies=("decision_confidence",),
        tags=("decision", "relationships"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_structure",
        name="Decision Structure Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates market structure for decision processing.",
        dependencies=("decision_relationships",),
        tags=("decision", "structure"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_flow",
        name="Decision Flow Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates decision flow and state progression.",
        dependencies=("decision_structure",),
        tags=("decision", "flow"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_market_state",
        name="Decision Market State Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Determines decision-relevant market state.",
        dependencies=("decision_flow",),
        tags=("decision", "market-state"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_transition",
        name="Decision Transition Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates transitions between decision states.",
        dependencies=("decision_market_state",),
        tags=("decision", "transition"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_future_scenario",
        name="Decision Future Scenario Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates future decision scenarios.",
        dependencies=("decision_transition",),
        tags=("decision", "future-scenario"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_decision",
        name="Decision Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description=(
            "Produces the structured decision output after "
            "upstream decision processing."
        ),
        dependencies=("decision_future_scenario",),
        tags=("decision", "final-decision"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_validation",
        name="Decision Validation Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Validates decision integrity.",
        dependencies=("decision_decision",),
        tags=("decision", "validation"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_learning",
        name="Decision Learning Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Feeds validated decision outcomes into learning.",
        dependencies=("decision_validation",),
        tags=("decision", "learning"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_intelligence",
        name="Decision Intelligence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_DECISION,
        layer=ENGINE_LAYER_DECISION,
        description="Aggregates decision intelligence for downstream consumers.",
        dependencies=("decision_learning",),
        tags=("decision", "intelligence"),
    ),

    # --------------------------------------------------------
    # VERDICT / COMMITMENT / CONFIDENCE
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="verdict_engine",
        name="Verdict Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_INTELLIGENCE,
        layer=ENGINE_LAYER_DECISION,
        description="Produces structured market verdict information.",
        dependencies=(
            "decision_intelligence",
            "magnitude_engine",
        ),
        tags=("verdict", "intelligence"),
    ),

    EngineRegistrationSpec(
        engine_id="confidence_engine",
        name="Confidence Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_INTELLIGENCE,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates consolidated confidence.",
        dependencies=("verdict_engine",),
        tags=("confidence", "intelligence"),
    ),

    EngineRegistrationSpec(
        engine_id="commitment_engine",
        name="Commitment Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_INTELLIGENCE,
        layer=ENGINE_LAYER_DECISION,
        description="Evaluates commitment strength and stability.",
        dependencies=("confidence_engine",),
        tags=("commitment", "intelligence"),
    ),

    # --------------------------------------------------------
    # CAS
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="cas_orchestrator",
        name="CAS Orchestrator",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description=(
            "Coordinates the Constraint and Safety control "
            "architecture."
        ),
        dependencies=(
            "compliance_gate",
            "execution_safety_gate",
            "exposure_gate",
            "position_gate",
            "risk_gate",
            "suitability_gate",
            "restriction_engine",
        ),
        tags=("cas", "orchestrator", "safety"),
    ),

    EngineRegistrationSpec(
        engine_id="compliance_gate",
        name="CAS Compliance Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Compliance control gate.",
        tags=("cas", "compliance"),
    ),

    EngineRegistrationSpec(
        engine_id="execution_safety_gate",
        name="CAS Execution Safety Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Execution safety control gate.",
        dependencies=("compliance_gate",),
        tags=("cas", "execution-safety"),
    ),

    EngineRegistrationSpec(
        engine_id="exposure_gate",
        name="CAS Exposure Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Exposure control gate.",
        dependencies=("execution_safety_gate",),
        tags=("cas", "exposure"),
    ),

    EngineRegistrationSpec(
        engine_id="position_gate",
        name="CAS Position Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Position control gate.",
        dependencies=("exposure_gate",),
        tags=("cas", "position"),
    ),

    EngineRegistrationSpec(
        engine_id="restriction_engine",
        name="CAS Restriction Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Restriction evaluation engine.",
        dependencies=("position_gate",),
        tags=("cas", "restriction"),
    ),

    EngineRegistrationSpec(
        engine_id="risk_gate",
        name="CAS Risk Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Risk control gate.",
        dependencies=("restriction_engine",),
        tags=("cas", "risk"),
    ),

    EngineRegistrationSpec(
        engine_id="suitability_gate",
        name="CAS Suitability Gate",
        version="1.0.0",
        domain=ENGINE_DOMAIN_CAS,
        layer=ENGINE_LAYER_CONTROL,
        description="Suitability control gate.",
        dependencies=("risk_gate",),
        tags=("cas", "suitability"),
    ),

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    EngineRegistrationSpec(
        engine_id="market_memory",
        name="Market Memory Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Stores and retrieves market memory.",
        dependencies=("market_context",),
        tags=("memory", "market"),
    ),

    EngineRegistrationSpec(
        engine_id="evidence_memory",
        name="Evidence Memory Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Stores validated evidence history.",
        dependencies=("evidence_orchestrator",),
        tags=("memory", "evidence"),
    ),

    EngineRegistrationSpec(
        engine_id="decision_memory",
        name="Decision Memory Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Stores decision history and outcomes.",
        dependencies=("decision_validation",),
        tags=("memory", "decision"),
    ),

    EngineRegistrationSpec(
        engine_id="outcome_memory",
        name="Outcome Memory Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Stores validated outcomes.",
        dependencies=("decision_memory",),
        tags=("memory", "outcome"),
    ),

    EngineRegistrationSpec(
        engine_id="pattern_memory",
        name="Pattern Memory Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Stores validated market patterns.",
        dependencies=(
            "market_memory",
            "outcome_memory",
        ),
        tags=("memory", "pattern"),
    ),

    EngineRegistrationSpec(
        engine_id="memory_retrieval",
        name="Memory Retrieval Engine",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_MEMORY,
        description="Retrieves relevant historical memory.",
        dependencies=("pattern_memory",),
        tags=("memory", "retrieval"),
    ),

    EngineRegistrationSpec(
        engine_id="memory_service",
        name="Memory Service",
        version="1.0.0",
        domain=ENGINE_DOMAIN_MEMORY,
        layer=ENGINE_LAYER_ORCHESTRATION,
        description="Coordinates memory subsystem access.",
        dependencies=("memory_retrieval",),
        tags=("memory", "service"),
    ),
)


# ============================================================
# CATALOG VALIDATION
# ============================================================


def validate_canonical_engine_catalog() -> dict[str, Any]:
    """
    Validate the canonical engine catalog before it is inserted
    into the runtime registry.

    No engine implementation is imported or executed.
    """

    errors: list[str] = []
    engine_ids: set[str] = set()

    for spec in ROBOMLM_CANONICAL_ENGINE_SPECS:

        try:
            _validate_registration_spec(spec)
        except Exception as exc:
            errors.append(
                f"{spec.engine_id}: {exc}"
            )

        if spec.engine_id in engine_ids:
            errors.append(
                f"Duplicate canonical engine ID: "
                f"{spec.engine_id}"
            )

        engine_ids.add(spec.engine_id)

    # --------------------------------------------------------
    # Dependency references must exist in the catalog.
    # --------------------------------------------------------

    for spec in ROBOMLM_CANONICAL_ENGINE_SPECS:

        for dependency in spec.dependencies:

            if dependency not in engine_ids:

                errors.append(
                    f"{spec.engine_id}: missing canonical "
                    f"dependency '{dependency}'"
                )

    return {
        "valid": len(errors) == 0,
        "engine_count": len(engine_ids),
        "errors": errors,
    }


# ============================================================
# LOAD CANONICAL CATALOG
# ============================================================


def register_canonical_engines(
    registry: Optional[EngineRegistry] = None,
) -> dict[str, Any]:
    """
    Load the canonical ROBOMLM engine catalog into a registry.

    The operation is idempotent for identical definitions.

    It will reject conflicting definitions.

    Returns a registration report.
    """

    target = registry or engine_registry

    validation = validate_canonical_engine_catalog()

    if not validation["valid"]:
        raise EngineBootstrapError(
            "Canonical engine catalog validation failed: "
            f"{validation['errors']}"
        )

    registered: list[str] = []
    existing: list[str] = []

    for spec in ROBOMLM_CANONICAL_ENGINE_SPECS:

        definition = _spec_to_definition(spec)

        if target.exists(definition.engine_id):

            target.check_conflict(definition)

            existing.append(
                definition.engine_id
            )

        else:

            target.register(definition)

            registered.append(
                definition.engine_id
            )

    return {
        "success": True,
        "registry_name": REGISTRY_NAME,
        "canonical_engine_count": len(
            ROBOMLM_CANONICAL_ENGINE_SPECS
        ),
        "registered": registered,
        "already_registered": existing,
        "registry_total": target.count(),
    }


# ============================================================
# CANONICAL ENGINE LOOKUP
# ============================================================


def canonical_engine_ids() -> tuple[str, ...]:
    """
    Return canonical engine IDs in deterministic order.
    """

    return tuple(
        sorted(
            spec.engine_id
            for spec in ROBOMLM_CANONICAL_ENGINE_SPECS
        )
    )


def canonical_engine_spec(
    engine_id: str,
) -> EngineRegistrationSpec:
    """
    Return one canonical engine specification.
    """

    normalized_id = EngineRegistry._normalize_engine_id(
        engine_id
    )

    for spec in ROBOMLM_CANONICAL_ENGINE_SPECS:

        if spec.engine_id == normalized_id:
            return spec

    raise EngineNotFoundError(
        f"Canonical engine not found: {normalized_id}"
    )


# ============================================================
# CANONICAL DOMAIN REPORT
# ============================================================


def canonical_engine_domain_report() -> dict[str, int]:
    """
    Return number of canonical engines per domain.
    """

    report: dict[str, int] = {}

    for spec in ROBOMLM_CANONICAL_ENGINE_SPECS:

        report[spec.domain] = (
            report.get(spec.domain, 0) + 1
        )

    return dict(
        sorted(report.items())
    )


# ============================================================
# CANONICAL DEPENDENCY REPORT
# ============================================================


def canonical_dependency_report() -> dict[
    str,
    tuple[str, ...],
]:
    """
    Return the canonical architectural dependency graph.
    """

    return {
        spec.engine_id: tuple(
            spec.dependencies
        )
        for spec in ROBOMLM_CANONICAL_ENGINE_SPECS
    }


# ============================================================
# REGISTRY INSTALL HELPER
# ============================================================


def install_robomlm_engine_registry() -> dict[str, Any]:
    """
    Install the canonical ROBOMLM engine catalog into the
    module-level registry.

    This function is intentionally explicit.

    Importing this module does NOT automatically mutate the
    global registry.
    """

    result = register_canonical_engines(
        engine_registry
    )

    consistency = (
        engine_registry.consistency_check()
    )

    return {
        **result,
        "consistency": consistency,
        "summary": engine_registry.summary(),
    }