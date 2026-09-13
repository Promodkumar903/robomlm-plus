# ============================================================
# VISION REGISTRY — PART 1
# Foundation / Definition / Basic Registration
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Optional


# ============================================================
# 1.1 REGISTRY IDENTITY
# ============================================================

REGISTRY_NAME = "vision_registry"
REGISTRY_VERSION = "1.0.0"


# ============================================================
# 1.2 VALID VISION STATUSES
# ============================================================

VALID_VISION_STATUSES = {
    "registered",
    "active",
    "disabled",
    "deprecated",
}


# ============================================================
# 1.3 REGISTRY EXCEPTIONS
# ============================================================

class VisionRegistryError(Exception):
    """Base exception for Vision Registry."""


class VisionAlreadyRegisteredError(VisionRegistryError):
    """Raised when a vision is already registered."""


class VisionNotFoundError(VisionRegistryError):
    """Raised when a requested vision does not exist."""


class InvalidVisionDefinitionError(VisionRegistryError):
    """Raised when a vision definition is invalid."""


class VisionStateError(VisionRegistryError):
    """Raised when an invalid vision state transition occurs."""


# ============================================================
# 1.4 VISION DEFINITION
# ============================================================

@dataclass(frozen=True)
class VisionDefinition:
    """
    Declarative definition of a ROBOMLM Vision.

    This defines WHAT a vision is.

    It does NOT:
        - generate predictions
        - calculate formulas
        - generate trading signals
        - make trading decisions
        - calculate entries/exits
        - calculate position size
        - execute orders
        - authorize users
        - enforce subscriptions
        - perform CAS decisions
    """

    vision_id: str
    name: str
    version: str

    domain: str
    layer: str

    description: str = ""

    status: str = "registered"

    owner: str = ""

    dependencies: tuple[str, ...] = field(
        default_factory=tuple
    )

    tags: tuple[str, ...] = field(
        default_factory=tuple
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


# ============================================================
# 1.5 VISION REGISTRY
# ============================================================

class VisionRegistry:
    """
    Central registry for ROBOMLM Vision definitions.

    Responsibility:
        - register visions
        - retrieve visions
        - discover basic metadata
        - validate definitions
        - list/filter visions

    Non-responsibility:
        - vision intelligence
        - prediction
        - formulas
        - signals
        - trading decisions
        - execution
        - authorization
        - subscription entitlement
        - risk decisions
        - CAS enforcement
    """

    def __init__(self) -> None:

        self._visions: dict[
            str,
            VisionDefinition
        ] = {}


    # ========================================================
    # 1.5.1 REGISTER
    # ========================================================

    def register(
        self,
        definition: VisionDefinition,
    ) -> VisionDefinition:
        """
        Register one vision definition.
        """

        self._validate_definition(
            definition
        )

        vision_id = self._normalize_vision_id(
            definition.vision_id
        )

        if vision_id in self._visions:
            raise VisionAlreadyRegisteredError(
                f"Vision '{vision_id}' is already "
                "registered."
            )

        normalized_definition = VisionDefinition(
            vision_id=vision_id,
            name=self._normalize_text(
                definition.name
            ),
            version=self._normalize_text(
                definition.version
            ),
            domain=self._normalize_text(
                definition.domain
            ),
            layer=self._normalize_text(
                definition.layer
            ),
            description=definition.description.strip(),
            status=definition.status,
            owner=definition.owner.strip(),
            dependencies=tuple(
                self._normalize_vision_id(dep)
                for dep in definition.dependencies
            ),
            tags=tuple(
                self._normalize_text(tag)
                for tag in definition.tags
            ),
            metadata=dict(
                definition.metadata
            ),
            registered_at=definition.registered_at,
        )

        self._visions[
            vision_id
        ] = normalized_definition

        return normalized_definition


    # ========================================================
    # 1.5.2 REGISTER MANY
    # ========================================================

    def register_many(
        self,
        definitions: Iterable[
            VisionDefinition
        ],
    ) -> list[VisionDefinition]:
        """
        Register multiple vision definitions.
        """

        definitions = list(definitions)

        if not definitions:
            return []

        registered: list[
            VisionDefinition
        ] = []

        for definition in definitions:
            registered.append(
                self.register(definition)
            )

        return registered


    # ========================================================
    # 1.5.3 GET
    # ========================================================

    def get(
        self,
        vision_id: str,
    ) -> VisionDefinition:
        """
        Retrieve a registered vision.
        """

        normalized_id = (
            self._normalize_vision_id(
                vision_id
            )
        )

        try:
            return self._visions[
                normalized_id
            ]

        except KeyError as exc:
            raise VisionNotFoundError(
                f"Vision '{vision_id}' was not found."
            ) from exc


    # ========================================================
    # 1.5.4 EXISTS
    # ========================================================

    def exists(
        self,
        vision_id: str,
    ) -> bool:
        """
        Check whether a vision exists.
        """

        normalized_id = (
            self._normalize_vision_id(
                vision_id
            )
        )

        return normalized_id in self._visions


    # ========================================================
    # 1.5.5 COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return total registered visions.
        """

        return len(self._visions)


    # ========================================================
    # 1.5.6 LIST ALL
    # ========================================================

    def list_all(
        self,
    ) -> list[VisionDefinition]:
        """
        Return all registered visions.
        """

        return list(
            self._visions.values()
        )


    # ========================================================
    # 1.5.7 LIST BY DOMAIN
    # ========================================================

    def list_by_domain(
        self,
        domain: str,
    ) -> list[VisionDefinition]:
        """
        Return visions belonging to a domain.
        """

        normalized_domain = (
            self._normalize_text(domain)
        )

        return [
            vision
            for vision in self._visions.values()
            if vision.domain == normalized_domain
        ]


    # ========================================================
    # 1.5.8 LIST BY LAYER
    # ========================================================

    def list_by_layer(
        self,
        layer: str,
    ) -> list[VisionDefinition]:
        """
        Return visions belonging to a layer.
        """

        normalized_layer = (
            self._normalize_text(layer)
        )

        return [
            vision
            for vision in self._visions.values()
            if vision.layer == normalized_layer
        ]


    # ========================================================
    # 1.5.9 LIST BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> list[VisionDefinition]:
        """
        Return visions with a specific status.
        """

        normalized_status = (
            self._normalize_text(status)
        )

        return [
            vision
            for vision in self._visions.values()
            if vision.status == normalized_status
        ]


    # ========================================================
    # 1.5.10 LIST BY TAG
    # ========================================================

    def list_by_tag(
        self,
        tag: str,
    ) -> list[VisionDefinition]:
        """
        Return visions containing a tag.
        """

        normalized_tag = (
            self._normalize_text(tag)
        )

        return [
            vision
            for vision in self._visions.values()
            if normalized_tag in vision.tags
        ]


    # ========================================================
    # 1.5.11 VALIDATE DEFINITION
    # ========================================================

    def _validate_definition(
        self,
        definition: VisionDefinition,
    ) -> None:
        """
        Validate one vision definition.
        """

        if not isinstance(
            definition,
            VisionDefinition,
        ):
            raise InvalidVisionDefinitionError(
                "Definition must be a "
                "VisionDefinition instance."
            )

        if not definition.vision_id:
            raise InvalidVisionDefinitionError(
                "Vision requires vision_id."
            )

        if not definition.name:
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "requires name."
            )

        if not definition.version:
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "requires version."
            )

        if not definition.domain:
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "requires domain."
            )

        if not definition.layer:
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "requires layer."
            )

        if definition.status not in (
            VALID_VISION_STATUSES
        ):
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                f"has invalid status "
                f"'{definition.status}'."
            )

        if not isinstance(
            definition.dependencies,
            tuple,
        ):
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "dependencies must be a tuple."
            )

        if not isinstance(
            definition.tags,
            tuple,
        ):
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "tags must be a tuple."
            )

        if not isinstance(
            definition.metadata,
            dict,
        ):
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "metadata must be a dictionary."
            )

        if definition.vision_id in (
            definition.dependencies
        ):
            raise InvalidVisionDefinitionError(
                f"Vision '{definition.vision_id}' "
                "cannot depend on itself."
            )


    # ========================================================
    # 1.5.12 NORMALIZE VISION ID
    # ========================================================

    @staticmethod
    def _normalize_vision_id(
        vision_id: str,
    ) -> str:
        """
        Normalize a vision identifier.
        """

        if not isinstance(
            vision_id,
            str,
        ):
            raise InvalidVisionDefinitionError(
                "vision_id must be a string."
            )

        normalized = (
            vision_id.strip().lower()
        )

        if not normalized:
            raise InvalidVisionDefinitionError(
                "vision_id cannot be empty."
            )

        return normalized


    # ========================================================
    # 1.5.13 NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        """
        Normalize textual registry values.
        """

        if not isinstance(
            value,
            str,
        ):
            raise InvalidVisionDefinitionError(
                "Registry text fields must be strings."
            )

        normalized = value.strip()

        if not normalized:
            raise InvalidVisionDefinitionError(
                "Registry text field cannot be empty."
            )

        return normalized


# ============================================================
# 1.6 GLOBAL VISION REGISTRY
# ============================================================

vision_registry = VisionRegistry()


# ============================================================
# 1.7 CONVENIENCE REGISTRATION HELPER
# ============================================================

def register_vision(
    *,
    vision_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    dependencies: Iterable[str] = (),
    tags: Iterable[str] = (),
    metadata: Optional[
        dict[str, Any]
    ] = None,
) -> VisionDefinition:
    """
    Convenience helper for registering a vision.
    """

    definition = VisionDefinition(
        vision_id=vision_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        status=status,
        owner=owner,
        dependencies=tuple(
            dependencies
        ),
        tags=tuple(
            tags
        ),
        metadata=dict(
            metadata or {}
        ),
    )

    return vision_registry.register(
        definition
    )


# ============================================================
# END OF VISION REGISTRY — PART 1
# ============================================================# ============================================================
# VISION REGISTRY — PART 2
# Lifecycle / Dependencies / Conflicts / Indexes / Health
# ============================================================


# ============================================================
# 2.1 PART 2 EXCEPTIONS
# ============================================================

class VisionRegistrationConflictError(
    VisionRegistryError
):
    """Raised when a vision registration conflicts with
    an existing definition."""


class VisionUnregisterError(
    VisionRegistryError
):
    """Raised when a vision cannot be safely unregistered."""


class VisionDependencyError(
    VisionRegistryError
):
    """Raised when a vision dependency is invalid or missing."""


class VisionVersionError(
    VisionRegistryError
):
    """Raised when a vision version is invalid."""


# ============================================================
# 2.2 LIFECYCLE MANAGEMENT
# ============================================================

def _vision_set_status(
    self: VisionRegistry,
    vision_id: str,
    status: str,
) -> VisionDefinition:
    """
    Change the lifecycle status of a registered vision.
    """

    if status not in VALID_VISION_STATUSES:
        raise VisionStateError(
            f"Invalid vision status '{status}'."
        )

    vision = self.get(vision_id)

    updated = VisionDefinition(
        vision_id=vision.vision_id,
        name=vision.name,
        version=vision.version,
        domain=vision.domain,
        layer=vision.layer,
        description=vision.description,
        status=status,
        owner=vision.owner,
        dependencies=vision.dependencies,
        tags=vision.tags,
        metadata=deepcopy(vision.metadata),
        registered_at=vision.registered_at,
    )

    self._visions[
        vision.vision_id
    ] = updated

    return updated


VisionRegistry.set_status = _vision_set_status


def _vision_activate(
    self: VisionRegistry,
    vision_id: str,
) -> VisionDefinition:
    """Activate a registered vision."""

    return self.set_status(
        vision_id,
        "active",
    )


VisionRegistry.activate = _vision_activate


def _vision_disable(
    self: VisionRegistry,
    vision_id: str,
) -> VisionDefinition:
    """Disable a registered vision."""

    return self.set_status(
        vision_id,
        "disabled",
    )


VisionRegistry.disable = _vision_disable


def _vision_deprecate(
    self: VisionRegistry,
    vision_id: str,
) -> VisionDefinition:
    """Deprecate a registered vision."""

    return self.set_status(
        vision_id,
        "deprecated",
    )


VisionRegistry.deprecate = _vision_deprecate


# ============================================================
# 2.3 CONFLICT DETECTION
# ============================================================

def _vision_check_conflict(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> bool:
    """
    Return True when the definition conflicts with
    an existing vision.
    """

    self._validate_definition(
        definition
    )

    vision_id = self._normalize_vision_id(
        definition.vision_id
    )

    if not self.exists(vision_id):
        return False

    existing = self.get(vision_id)

    return (
        existing.name != definition.name
        or existing.version != definition.version
        or existing.domain != definition.domain
        or existing.layer != definition.layer
        or existing.description != definition.description
        or existing.status != definition.status
        or existing.owner != definition.owner
        or existing.dependencies
        != tuple(definition.dependencies)
        or existing.tags
        != tuple(definition.tags)
        or existing.metadata
        != definition.metadata
    )


VisionRegistry.check_conflict = (
    _vision_check_conflict
)


# ============================================================
# 2.4 SAFE REGISTRATION
# ============================================================

def _vision_register_safe(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:
    """
    Register only when there is no conflicting definition.
    """

    self._validate_definition(
        definition
    )

    if not self.exists(
        definition.vision_id
    ):
        return self.register(
            definition
        )

    if self.check_conflict(
        definition
    ):
        raise VisionRegistrationConflictError(
            f"Conflicting definition already exists "
            f"for vision '{definition.vision_id}'."
        )

    return self.get(
        definition.vision_id
    )


VisionRegistry.register_safe = (
    _vision_register_safe
)


# ============================================================
# 2.5 REPLACE VISION
# ============================================================

def _vision_replace(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:
    """
    Replace an existing vision definition.
    """

    self._validate_definition(
        definition
    )

    vision_id = self._normalize_vision_id(
        definition.vision_id
    )

    if not self.exists(vision_id):
        raise VisionNotFoundError(
            f"Cannot replace unknown vision "
            f"'{vision_id}'."
        )

    normalized_definition = VisionDefinition(
        vision_id=vision_id,
        name=self._normalize_text(
            definition.name
        ),
        version=self._normalize_text(
            definition.version
        ),
        domain=self._normalize_text(
            definition.domain
        ),
        layer=self._normalize_text(
            definition.layer
        ),
        description=definition.description.strip(),
        status=definition.status,
        owner=definition.owner.strip(),
        dependencies=tuple(
            self._normalize_vision_id(dep)
            for dep in definition.dependencies
        ),
        tags=tuple(
            self._normalize_text(tag)
            for tag in definition.tags
        ),
        metadata=deepcopy(
            definition.metadata
        ),
        registered_at=definition.registered_at,
    )

    self._visions[
        vision_id
    ] = normalized_definition

    return normalized_definition


VisionRegistry.replace = _vision_replace


# ============================================================
# 2.6 VISION IDS
# ============================================================

def _vision_ids(
    self: VisionRegistry,
) -> tuple[str, ...]:
    """Return all registered vision IDs."""

    return tuple(
        self._visions.keys()
    )


VisionRegistry.vision_ids = _vision_ids


# ============================================================
# 2.7 ACTIVE VISIONS
# ============================================================

def _active_visions(
    self: VisionRegistry,
) -> list[VisionDefinition]:
    """Return active visions only."""

    return self.list_by_status(
        "active"
    )


VisionRegistry.active_visions = _active_visions


# ============================================================
# 2.8 INTERNAL INDEXES
# ============================================================

VisionRegistry._domain_index = {}
VisionRegistry._layer_index = {}
VisionRegistry._status_index = {}
VisionRegistry._tag_index = {}


# ============================================================
# 2.9 REBUILD INDEXES
# ============================================================

def _vision_rebuild_indexes(
    self: VisionRegistry,
) -> None:
    """
    Rebuild all registry indexes from the source-of-truth
    _visions dictionary.
    """

    self._domain_index = {}
    self._layer_index = {}
    self._status_index = {}
    self._tag_index = {}

    for vision in self._visions.values():

        self._domain_index.setdefault(
            vision.domain,
            set(),
        ).add(
            vision.vision_id
        )

        self._layer_index.setdefault(
            vision.layer,
            set(),
        ).add(
            vision.vision_id
        )

        self._status_index.setdefault(
            vision.status,
            set(),
        ).add(
            vision.vision_id
        )

        for tag in vision.tags:
            self._tag_index.setdefault(
                tag,
                set(),
            ).add(
                vision.vision_id
            )


VisionRegistry.rebuild_indexes = (
    _vision_rebuild_indexes
)


# ============================================================
# 2.10 INDEXED DOMAIN LOOKUP
# ============================================================

def _vision_index_by_domain(
    self: VisionRegistry,
    domain: str,
) -> list[VisionDefinition]:
    """Lookup visions using domain index."""

    normalized = self._normalize_text(
        domain
    )

    ids = self._domain_index.get(
        normalized,
        set(),
    )

    return [
        self._visions[vision_id]
        for vision_id in ids
        if vision_id in self._visions
    ]


VisionRegistry.index_by_domain = (
    _vision_index_by_domain
)


# ============================================================
# 2.11 INDEXED LAYER LOOKUP
# ============================================================

def _vision_index_by_layer(
    self: VisionRegistry,
    layer: str,
) -> list[VisionDefinition]:
    """Lookup visions using layer index."""

    normalized = self._normalize_text(
        layer
    )

    ids = self._layer_index.get(
        normalized,
        set(),
    )

    return [
        self._visions[vision_id]
        for vision_id in ids
        if vision_id in self._visions
    ]


VisionRegistry.index_by_layer = (
    _vision_index_by_layer
)


# ============================================================
# 2.12 INDEXED STATUS LOOKUP
# ============================================================

def _vision_index_by_status(
    self: VisionRegistry,
    status: str,
) -> list[VisionDefinition]:
    """Lookup visions using status index."""

    normalized = self._normalize_text(
        status
    )

    ids = self._status_index.get(
        normalized,
        set(),
    )

    return [
        self._visions[vision_id]
        for vision_id in ids
        if vision_id in self._visions
    ]


VisionRegistry.index_by_status = (
    _vision_index_by_status
)


# ============================================================
# 2.13 INDEXED TAG LOOKUP
# ============================================================

def _vision_index_by_tag(
    self: VisionRegistry,
    tag: str,
) -> list[VisionDefinition]:
    """Lookup visions using tag index."""

    normalized = self._normalize_text(
        tag
    )

    ids = self._tag_index.get(
        normalized,
        set(),
    )

    return [
        self._visions[vision_id]
        for vision_id in ids
        if vision_id in self._visions
    ]


VisionRegistry.index_by_tag = (
    _vision_index_by_tag
)


# ============================================================
# 2.14 DEPENDENCY EXTRACTION
# ============================================================

def _vision_dependencies(
    self: VisionRegistry,
    vision_id: str,
) -> tuple[str, ...]:
    """
    Return declared dependencies of a vision.
    """

    vision = self.get(
        vision_id
    )

    return tuple(
        vision.dependencies
    )


VisionRegistry.dependencies = (
    _vision_dependencies
)


# ============================================================
# 2.15 DEPENDENTS
# ============================================================

def _vision_dependents(
    self: VisionRegistry,
    vision_id: str,
) -> list[str]:
    """
    Return visions that depend on the given vision.
    """

    normalized_id = (
        self._normalize_vision_id(
            vision_id
        )
    )

    if not self.exists(
        normalized_id
    ):
        raise VisionNotFoundError(
            f"Vision '{vision_id}' was not found."
        )

    return sorted(
        vision.vision_id
        for vision in self._visions.values()
        if normalized_id in vision.dependencies
    )


VisionRegistry.dependents = (
    _vision_dependents
)


# ============================================================
# 2.16 DEPENDENCY GRAPH
# ============================================================

def _vision_dependency_graph(
    self: VisionRegistry,
) -> dict[str, tuple[str, ...]]:
    """
    Return the complete declared dependency graph.
    """

    return {
        vision_id: tuple(
            vision.dependencies
        )
        for vision_id, vision
        in self._visions.items()
    }


VisionRegistry.dependency_graph = (
    _vision_dependency_graph
)


# ============================================================
# 2.17 DEPENDENCY VALIDATION
# ============================================================

def _vision_validate_dependencies(
    self: VisionRegistry,
    vision_id: str,
) -> dict[str, Any]:
    """
    Validate dependencies for one vision.
    """

    vision = self.get(
        vision_id
    )

    missing: list[str] = []
    self_dependencies: list[str] = []

    for dependency in vision.dependencies:

        normalized_dependency = (
            self._normalize_vision_id(
                dependency
            )
        )

        if normalized_dependency == vision.vision_id:
            self_dependencies.append(
                normalized_dependency
            )
            continue

        if not self.exists(
            normalized_dependency
        ):
            missing.append(
                normalized_dependency
            )

    healthy = (
        not missing
        and not self_dependencies
    )

    return {
        "vision_id": vision.vision_id,
        "dependencies": list(
            vision.dependencies
        ),
        "missing": sorted(
            missing
        ),
        "self_dependencies": sorted(
            self_dependencies
        ),
        "healthy": healthy,
    }


VisionRegistry.validate_dependencies = (
    _vision_validate_dependencies
)


# ============================================================
# 2.18 ALL DEPENDENCY VALIDATION
# ============================================================

def _vision_validate_all_dependencies(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Validate dependencies across the complete registry.
    """

    results = [
        self.validate_dependencies(
            vision_id
        )
        for vision_id in self.vision_ids()
    ]

    invalid = [
        result
        for result in results
        if not result["healthy"]
    ]

    return {
        "vision_count": self.count(),
        "checked_count": len(results),
        "invalid_count": len(invalid),
        "invalid": invalid,
        "healthy": not invalid,
    }


VisionRegistry.validate_all_dependencies = (
    _vision_validate_all_dependencies
)


# ============================================================
# 2.19 CYCLE DETECTION
# ============================================================

def _vision_detect_cycles(
    self: VisionRegistry,
) -> list[list[str]]:
    """
    Detect dependency cycles using DFS.
    """

    graph = self.dependency_graph()

    visited: set[str] = set()
    active: set[str] = set()

    cycles: list[list[str]] = []

    def dfs(
        node: str,
        path: list[str],
    ) -> None:

        if node in active:

            if node in path:
                index = path.index(node)

                cycle = (
                    path[index:]
                    + [node]
                )

                if cycle not in cycles:
                    cycles.append(
                        cycle
                    )

            return

        if node in visited:
            return

        visited.add(node)
        active.add(node)

        for dependency in graph.get(
            node,
            (),
        ):

            if dependency in graph:
                dfs(
                    dependency,
                    path + [node],
                )

        active.remove(node)

    for node in graph:
        dfs(
            node,
            [],
        )

    return cycles


VisionRegistry.detect_cycles = (
    _vision_detect_cycles
)


# ============================================================
# 2.20 ASSERT NO CYCLES
# ============================================================

def _vision_assert_no_cycles(
    self: VisionRegistry,
) -> None:
    """
    Raise when dependency cycles exist.
    """

    cycles = self.detect_cycles()

    if cycles:
        raise VisionDependencyError(
            "Vision dependency cycle detected: "
            f"{cycles}"
        )


VisionRegistry.assert_no_cycles = (
    _vision_assert_no_cycles
)


# ============================================================
# 2.21 REGISTER WITH DEPENDENCIES
# ============================================================

def _vision_register_with_dependencies(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:
    """
    Register a vision only when all declared dependencies
    already exist.
    """

    self._validate_definition(
        definition
    )

    vision_id = self._normalize_vision_id(
        definition.vision_id
    )

    if vision_id in definition.dependencies:
        raise VisionDependencyError(
            f"Vision '{vision_id}' cannot depend "
            "on itself."
        )

    missing = [
        dependency
        for dependency in definition.dependencies
        if not self.exists(
            dependency
        )
    ]

    if missing:
        raise VisionDependencyError(
            f"Vision '{vision_id}' has missing "
            f"dependencies: {missing}"
        )

    registered = self.register_safe(
        definition
    )

    self.assert_no_cycles()

    return registered


VisionRegistry.register_with_dependencies = (
    _vision_register_with_dependencies
)


# ============================================================
# 2.22 UNREGISTER
# ============================================================

def _vision_unregister(
    self: VisionRegistry,
    vision_id: str,
    *,
    force: bool = False,
) -> VisionDefinition:
    """
    Remove a vision safely.

    A vision with active dependents cannot be removed
    unless force=True.
    """

    vision = self.get(
        vision_id
    )

    dependents = self.dependents(
        vision.vision_id
    )

    if dependents and not force:
        raise VisionUnregisterError(
            f"Cannot unregister vision "
            f"'{vision.vision_id}'. "
            f"Dependent visions exist: "
            f"{dependents}"
        )

    removed = self._visions.pop(
        vision.vision_id
    )

    self.rebuild_indexes()

    return removed


VisionRegistry.unregister = _vision_unregister


# ============================================================
# 2.23 SUMMARY
# ============================================================

def _vision_summary(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Return a compact registry summary.
    """

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": self.count(),
        "active_count": len(
            self.active_visions()
        ),
        "domains": sorted(
            self._domain_index.keys()
        ),
        "layers": sorted(
            self._layer_index.keys()
        ),
        "statuses": sorted(
            self._status_index.keys()
        ),
        "tags": sorted(
            self._tag_index.keys()
        ),
    }


VisionRegistry.summary = _vision_summary


# ============================================================
# 2.24 HEALTH CHECK
# ============================================================

def _vision_health(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Perform registry health validation.
    """

    definition_errors: list[str] = []

    for vision in self.list_all():

        try:
            self._validate_definition(
                vision
            )
        except Exception as exc:
            definition_errors.append(
                f"{vision.vision_id}: {exc}"
            )

    dependency_report = (
        self.validate_all_dependencies()
    )

    cycles = self.detect_cycles()

    healthy = (
        not definition_errors
        and dependency_report["healthy"]
        and not cycles
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "vision_count": self.count(),
        "definition_errors": definition_errors,
        "dependency_validation": dependency_report,
        "cycles": cycles,
    }


VisionRegistry.health = _vision_health


# ============================================================
# 2.25 INITIAL INDEX BUILD
# ============================================================

strategy_registry  # intentional no-op boundary marker removed


# Build indexes for the current global registry.
vision_registry.rebuild_indexes()


# ============================================================
# END OF VISION REGISTRY — PART 2
# ============================================================
# ============================================================
# VISION REGISTRY — PART 3
# Search / Bootstrap / Snapshot / Restore / Audit / State
# ============================================================


# ============================================================
# 3.1 PART 3 EXCEPTIONS
# ============================================================

class VisionBootstrapError(
    VisionRegistryError
):
    """Raised when vision bootstrap fails."""


class VisionSnapshotError(
    VisionRegistryError
):
    """Raised when vision snapshot operations fail."""


# ============================================================
# 3.2 GENERAL SEARCH
# ============================================================

def _vision_find(
    self: VisionRegistry,
    *,
    domain: Optional[str] = None,
    layer: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    owner: Optional[str] = None,
) -> list[VisionDefinition]:
    """
    Search registered visions using optional filters.
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
        self._normalize_text(status)
        if status is not None
        else None
    )

    normalized_tag = (
        self._normalize_text(tag)
        if tag is not None
        else None
    )

    normalized_owner = (
        self._normalize_text(owner)
        if owner is not None
        else None
    )

    results: list[VisionDefinition] = []

    for vision in self._visions.values():

        if (
            normalized_domain is not None
            and vision.domain != normalized_domain
        ):
            continue

        if (
            normalized_layer is not None
            and vision.layer != normalized_layer
        ):
            continue

        if (
            normalized_status is not None
            and vision.status != normalized_status
        ):
            continue

        if (
            normalized_tag is not None
            and normalized_tag not in vision.tags
        ):
            continue

        if (
            normalized_owner is not None
            and vision.owner != normalized_owner
        ):
            continue

        results.append(vision)

    return results


VisionRegistry.find = _vision_find


# ============================================================
# 3.3 PREFIX SEARCH
# ============================================================

def _vision_find_by_prefix(
    self: VisionRegistry,
    prefix: str,
) -> list[VisionDefinition]:
    """
    Find visions whose IDs start with the supplied prefix.
    """

    normalized_prefix = (
        self._normalize_vision_id(prefix)
    )

    return [
        vision
        for vision in self._visions.values()
        if vision.vision_id.startswith(
            normalized_prefix
        )
    ]


VisionRegistry.find_by_prefix = (
    _vision_find_by_prefix
)


# ============================================================
# 3.4 DOMAIN SEARCH
# ============================================================

def _vision_find_by_domain(
    self: VisionRegistry,
    domain: str,
) -> list[VisionDefinition]:
    """Find visions by domain."""

    return self.find(
        domain=domain
    )


VisionRegistry.find_by_domain = (
    _vision_find_by_domain
)


# ============================================================
# 3.5 LAYER SEARCH
# ============================================================

def _vision_find_by_layer(
    self: VisionRegistry,
    layer: str,
) -> list[VisionDefinition]:
    """Find visions by layer."""

    return self.find(
        layer=layer
    )


VisionRegistry.find_by_layer = (
    _vision_find_by_layer
)


# ============================================================
# 3.6 STATUS SEARCH
# ============================================================

def _vision_find_by_status(
    self: VisionRegistry,
    status: str,
) -> list[VisionDefinition]:
    """Find visions by lifecycle status."""

    return self.find(
        status=status
    )


VisionRegistry.find_by_status = (
    _vision_find_by_status
)


# ============================================================
# 3.7 TAG SEARCH
# ============================================================

def _vision_find_by_tag(
    self: VisionRegistry,
    tag: str,
) -> list[VisionDefinition]:
    """Find visions by tag."""

    return self.find(
        tag=tag
    )


VisionRegistry.find_by_tag = (
    _vision_find_by_tag
)


# ============================================================
# 3.8 BOOTSTRAP VALIDATION
# ============================================================

def _vision_validate_bootstrap(
    self: VisionRegistry,
    definitions: Iterable[
        VisionDefinition
    ],
) -> dict[str, Any]:
    """
    Validate a collection of vision definitions before
    bootstrap installation.
    """

    definitions = list(definitions)

    errors: list[str] = []
    ids: set[str] = set()

    for definition in definitions:

        try:
            self._validate_definition(
                definition
            )
        except Exception as exc:
            errors.append(
                str(exc)
            )
            continue

        normalized_id = (
            self._normalize_vision_id(
                definition.vision_id
            )
        )

        if normalized_id in ids:
            errors.append(
                f"Duplicate vision ID in bootstrap: "
                f"{normalized_id}"
            )

        ids.add(normalized_id)

    batch_ids = set(ids)

    for definition in definitions:

        normalized_id = (
            self._normalize_vision_id(
                definition.vision_id
            )
        )

        for dependency in definition.dependencies:

            normalized_dependency = (
                self._normalize_vision_id(
                    dependency
                )
            )

            if (
                normalized_dependency
                == normalized_id
            ):
                errors.append(
                    f"Vision '{normalized_id}' "
                    "cannot depend on itself."
                )
                continue

            if (
                normalized_dependency
                not in batch_ids
                and not self.exists(
                    normalized_dependency
                )
            ):
                errors.append(
                    f"Vision '{normalized_id}' "
                    f"has unresolved dependency "
                    f"'{normalized_dependency}'."
                )

    return {
        "count": len(definitions),
        "ids": sorted(ids),
        "errors": errors,
        "healthy": not errors,
    }


VisionRegistry.validate_bootstrap = (
    _vision_validate_bootstrap
)


# ============================================================
# 3.9 DEPENDENCY-AWARE BOOTSTRAP
# ============================================================

def _vision_bootstrap(
    self: VisionRegistry,
    definitions: Iterable[
        VisionDefinition
    ],
    *,
    replace_existing: bool = False,
) -> list[VisionDefinition]:
    """
    Bootstrap visions while respecting dependencies.

    A definition can be installed when all of its dependencies
    are already registered or have been installed earlier in
    the same bootstrap operation.
    """

    definitions = list(definitions)

    validation = self.validate_bootstrap(
        definitions
    )

    if not validation["healthy"]:
        raise VisionBootstrapError(
            "Vision bootstrap validation failed: "
            f"{validation['errors']}"
        )

    pending: dict[
        str,
        VisionDefinition
    ] = {
        self._normalize_vision_id(
            definition.vision_id
        ): definition
        for definition in definitions
    }

    registered: list[
        VisionDefinition
    ] = []

    progress = True

    while pending and progress:

        progress = False

        for vision_id, definition in list(
            pending.items()
        ):

            dependencies_ready = all(
                self.exists(
                    dependency
                )
                or (
                    self._normalize_vision_id(
                        dependency
                    )
                    not in pending
                )
                for dependency
                in definition.dependencies
            )

            if not dependencies_ready:
                continue

            if replace_existing and self.exists(
                vision_id
            ):
                result = self.replace(
                    definition
                )
            else:
                result = self.register_safe(
                    definition
                )

            registered.append(result)

            del pending[
                vision_id
            ]

            progress = True

    if pending:
        unresolved = {
            vision_id: list(
                definition.dependencies
            )
            for vision_id, definition
            in pending.items()
        }

        raise VisionBootstrapError(
            "Unable to resolve vision bootstrap "
            f"dependencies: {unresolved}"
        )

    self.rebuild_indexes()

    self.assert_no_cycles()

    return registered


VisionRegistry.bootstrap = _vision_bootstrap


# ============================================================
# 3.10 SNAPSHOT
# ============================================================

def _vision_snapshot(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Create a serializable snapshot of the registry.
    """

    try:

        return {
            "registry": REGISTRY_NAME,
            "registry_version": REGISTRY_VERSION,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat(),
            "vision_count": self.count(),
            "visions": [
                {
                    "vision_id": vision.vision_id,
                    "name": vision.name,
                    "version": vision.version,
                    "domain": vision.domain,
                    "layer": vision.layer,
                    "description": vision.description,
                    "status": vision.status,
                    "owner": vision.owner,
                    "dependencies": list(
                        vision.dependencies
                    ),
                    "tags": list(
                        vision.tags
                    ),
                    "metadata": deepcopy(
                        vision.metadata
                    ),
                    "registered_at": (
                        vision.registered_at.isoformat()
                        if isinstance(
                            vision.registered_at,
                            datetime,
                        )
                        else str(
                            vision.registered_at
                        )
                    ),
                }
                for vision
                in self._visions.values()
            ],
        }

    except Exception as exc:
        raise VisionSnapshotError(
            "Unable to create vision registry snapshot."
        ) from exc


VisionRegistry.snapshot = _vision_snapshot


# ============================================================
# 3.11 RESTORE SNAPSHOT
# ============================================================

def _vision_restore_snapshot(
    self: VisionRegistry,
    snapshot: dict[str, Any],
    *,
    replace_existing: bool = False,
) -> list[VisionDefinition]:
    """
    Restore registry state from a snapshot.

    Existing registry state is preserved and restored on
    failure.
    """

    if not isinstance(
        snapshot,
        dict,
    ):
        raise VisionSnapshotError(
            "Snapshot must be a dictionary."
        )

    if snapshot.get(
        "registry"
    ) != REGISTRY_NAME:
        raise VisionSnapshotError(
            "Snapshot belongs to a different registry."
        )

    raw_visions = snapshot.get(
        "visions"
    )

    if not isinstance(
        raw_visions,
        list,
    ):
        raise VisionSnapshotError(
            "Snapshot 'visions' must be a list."
        )

    definitions: list[
        VisionDefinition
    ] = []

    for item in raw_visions:

        if not isinstance(
            item,
            dict,
        ):
            raise VisionSnapshotError(
                "Invalid vision entry in snapshot."
            )

        registered_at_raw = item.get(
            "registered_at"
        )

        registered_at = (
            datetime.fromisoformat(
                registered_at_raw
            )
            if isinstance(
                registered_at_raw,
                str,
            )
            else datetime.now(
                timezone.utc
            )
        )

        definitions.append(
            VisionDefinition(
                vision_id=item["vision_id"],
                name=item["name"],
                version=item["version"],
                domain=item["domain"],
                layer=item["layer"],
                description=item.get(
                    "description",
                    "",
                ),
                status=item.get(
                    "status",
                    "registered",
                ),
                owner=item.get(
                    "owner",
                    "",
                ),
                dependencies=tuple(
                    item.get(
                        "dependencies",
                        [],
                    )
                ),
                tags=tuple(
                    item.get(
                        "tags",
                        [],
                    )
                ),
                metadata=deepcopy(
                    item.get(
                        "metadata",
                        {},
                    )
                ),
                registered_at=registered_at,
            )
        )

    previous_snapshot = self.snapshot()

    try:

        if replace_existing:

            self._visions.clear()

            for definition in definitions:
                self.register(
                    definition
                )

        else:

            self.bootstrap(
                definitions,
                replace_existing=False,
            )

        self.rebuild_indexes()
        self.assert_no_cycles()

        return self.list_all()

    except Exception as exc:

        try:
            self._visions.clear()

            self._restore_snapshot_internal(
                previous_snapshot
            )

            self.rebuild_indexes()

        except Exception as restore_exc:

            raise VisionSnapshotError(
                "Snapshot restore failed and rollback "
                "also failed."
            ) from restore_exc

        raise VisionSnapshotError(
            f"Vision snapshot restore failed: {exc}"
        ) from exc


VisionRegistry.restore_snapshot = (
    _vision_restore_snapshot
)


# ============================================================
# 3.12 INTERNAL SNAPSHOT RESTORER
# ============================================================

def _vision_restore_snapshot_internal(
    self: VisionRegistry,
    snapshot: dict[str, Any],
) -> None:
    """
    Internal snapshot restoration helper.

    This bypasses public bootstrap semantics because it is
    used for rollback.
    """

    raw_visions = snapshot.get(
        "visions",
        [],
    )

    self._visions.clear()

    for item in raw_visions:

        registered_at_raw = item.get(
            "registered_at"
        )

        registered_at = (
            datetime.fromisoformat(
                registered_at_raw
            )
            if isinstance(
                registered_at_raw,
                str,
            )
            else datetime.now(
                timezone.utc
            )
        )

        definition = VisionDefinition(
            vision_id=item["vision_id"],
            name=item["name"],
            version=item["version"],
            domain=item["domain"],
            layer=item["layer"],
            description=item.get(
                "description",
                "",
            ),
            status=item.get(
                "status",
                "registered",
            ),
            owner=item.get(
                "owner",
                "",
            ),
            dependencies=tuple(
                item.get(
                    "dependencies",
                    [],
                )
            ),
            tags=tuple(
                item.get(
                    "tags",
                    [],
                )
            ),
            metadata=deepcopy(
                item.get(
                    "metadata",
                    {},
                )
            ),
            registered_at=registered_at,
        )

        self._visions[
            self._normalize_vision_id(
                definition.vision_id
            )
        ] = definition


VisionRegistry._restore_snapshot_internal = (
    _vision_restore_snapshot_internal
)


# ============================================================
# 3.13 METADATA EXPORT
# ============================================================

def _vision_export_metadata(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Export registry metadata without executable logic.
    """

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": self.count(),
        "visions": [
            {
                "vision_id": vision.vision_id,
                "name": vision.name,
                "version": vision.version,
                "domain": vision.domain,
                "layer": vision.layer,
                "description": vision.description,
                "status": vision.status,
                "owner": vision.owner,
                "dependencies": list(
                    vision.dependencies
                ),
                "tags": list(
                    vision.tags
                ),
                "metadata": deepcopy(
                    vision.metadata
                ),
            }
            for vision
            in self._visions.values()
        ],
    }


VisionRegistry.export_metadata = (
    _vision_export_metadata
)


# ============================================================
# 3.14 CONSISTENCY CHECK
# ============================================================

def _vision_consistency_check(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Check registry definitions, duplicate IDs,
    dependencies and cycles.
    """

    errors: list[str] = []

    seen_ids: set[str] = set()

    for vision in self._visions.values():

        try:
            self._validate_definition(
                vision
            )
        except Exception as exc:
            errors.append(
                f"{vision.vision_id}: {exc}"
            )

        if vision.vision_id in seen_ids:
            errors.append(
                f"Duplicate vision ID: "
                f"{vision.vision_id}"
            )

        seen_ids.add(
            vision.vision_id
        )

        for dependency in vision.dependencies:

            normalized_dependency = (
                self._normalize_vision_id(
                    dependency
                )
            )

            if (
                normalized_dependency
                not in self._visions
            ):
                errors.append(
                    f"Vision '{vision.vision_id}' "
                    f"references missing dependency "
                    f"'{normalized_dependency}'."
                )

    cycles = self.detect_cycles()

    if cycles:
        errors.append(
            f"Dependency cycles detected: {cycles}"
        )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "vision_count": self.count(),
        "errors": errors,
        "cycles": cycles,
        "healthy": not errors,
    }


VisionRegistry.consistency_check = (
    _vision_consistency_check
)


# ============================================================
# 3.15 FULL AUDIT
# ============================================================

def _vision_full_audit(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Full Vision Registry audit.
    """

    consistency = (
        self.consistency_check()
    )

    dependency_validation = (
        self.validate_all_dependencies()
    )

    health = self.health()

    healthy = (
        consistency["healthy"]
        and dependency_validation["healthy"]
        and health["healthy"]
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "consistency": consistency,
        "dependency_validation": (
            dependency_validation
        ),
        "health": health,
    }


VisionRegistry.full_audit = (
    _vision_full_audit
)


# ============================================================
# 3.16 ASSERT HEALTHY
# ============================================================

def _vision_assert_healthy(
    self: VisionRegistry,
) -> None:
    """
    Raise an exception when registry health validation fails.
    """

    audit = self.full_audit()

    if not audit["healthy"]:
        raise VisionRegistryError(
            "Vision Registry health check failed: "
            f"{audit}"
        )


VisionRegistry.assert_healthy = (
    _vision_assert_healthy
)


# ============================================================
# 3.17 REGISTRY STATE
# ============================================================

def _vision_state(
    self: VisionRegistry,
) -> dict[str, Any]:
    """
    Return current registry state.
    """

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": self.count(),
        "vision_ids": sorted(
            self.vision_ids()
        ),
        "active_ids": sorted(
            vision.vision_id
            for vision
            in self.active_visions()
        ),
        "frozen": getattr(
            self,
            "_frozen",
            False,
        ),
    }


VisionRegistry.state = _vision_state


# ============================================================
# 3.18 REBUILD GLOBAL INDEXES
# ============================================================

vision_registry.rebuild_indexes()


# ============================================================
# END OF VISION REGISTRY — PART 3
# ============================================================
# ============================================================
# VISION REGISTRY — PART 4
# Declarative Specs, Decorator Registration & Discovery
# ============================================================

from copy import deepcopy


# ============================================================
# PART 4 — EXCEPTIONS
# ============================================================

class VisionSpecError(VisionRegistryError):
    """Base exception for invalid vision registration specifications."""


class VisionSpecConflictError(VisionSpecError):
    """Raised when two vision specifications conflict."""


class VisionDiscoveryError(VisionSpecError):
    """Raised when vision specification discovery fails."""


# ============================================================
# PART 4 — REGISTRATION SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class VisionRegistrationSpec:
    """
    Declarative registration specification for a ROBOMLM vision.

    IMPORTANT:
        This object stores metadata only.

    It MUST NOT contain:
        - prediction formulas
        - signal generation
        - trading decisions
        - entry/exit logic
        - position sizing
        - execution logic
        - CAS authorization
    """

    vision_id: str
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

    def to_definition(self) -> VisionDefinition:
        """Convert declarative spec into immutable VisionDefinition."""

        return VisionDefinition(
            vision_id=self.vision_id,
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
# PART 4 — SPEC VALIDATION
# ============================================================

def _validate_vision_spec(spec: VisionRegistrationSpec) -> None:
    """Validate a vision registration specification."""

    if not isinstance(spec, VisionRegistrationSpec):
        raise VisionSpecError(
            "Expected VisionRegistrationSpec, "
            f"got {type(spec).__name__}"
        )

    if not isinstance(spec.vision_id, str) or not spec.vision_id.strip():
        raise VisionSpecError("vision_id must be a non-empty string")

    if not isinstance(spec.name, str) or not spec.name.strip():
        raise VisionSpecError("name must be a non-empty string")

    if not isinstance(spec.version, str) or not spec.version.strip():
        raise VisionSpecError("version must be a non-empty string")

    if not isinstance(spec.domain, str) or not spec.domain.strip():
        raise VisionSpecError("domain must be a non-empty string")

    if not isinstance(spec.layer, str) or not spec.layer.strip():
        raise VisionSpecError("layer must be a non-empty string")

    if spec.status not in VALID_VISION_STATUSES:
        raise VisionSpecError(
            f"Invalid vision status: {spec.status}"
        )

    if not isinstance(spec.dependencies, tuple):
        raise VisionSpecError(
            "dependencies must be a tuple"
        )

    if not isinstance(spec.tags, tuple):
        raise VisionSpecError(
            "tags must be a tuple"
        )

    if not isinstance(spec.metadata, dict):
        raise VisionSpecError(
            "metadata must be a dictionary"
        )

    normalized_id = spec.vision_id.strip().lower()

    if not normalized_id:
        raise VisionSpecError(
            "vision_id becomes empty after normalization"
        )

    for dependency in spec.dependencies:
        if not isinstance(dependency, str) or not dependency.strip():
            raise VisionSpecError(
                f"Invalid dependency in vision '{spec.vision_id}'"
            )

    for tag in spec.tags:
        if not isinstance(tag, str) or not tag.strip():
            raise VisionSpecError(
                f"Invalid tag in vision '{spec.vision_id}'"
            )


# ============================================================
# PART 4 — REGISTRY SPEC REGISTRATION
# ============================================================

def _vision_register_spec(
    self: VisionRegistry,
    spec: VisionRegistrationSpec,
) -> VisionDefinition:
    """Register one validated vision specification."""

    _validate_vision_spec(spec)

    definition = spec.to_definition()

    return self.register(definition)


VisionRegistry.register_spec = _vision_register_spec


def _vision_register_specs(
    self: VisionRegistry,
    specs: Iterable[VisionRegistrationSpec],
) -> list[VisionDefinition]:
    """Register multiple vision specifications."""

    specs = list(specs)

    for spec in specs:
        _validate_vision_spec(spec)

    definitions = [
        spec.to_definition()
        for spec in specs
    ]

    return self.register_many(definitions)


VisionRegistry.register_specs = _vision_register_specs


# ============================================================
# PART 4 — GLOBAL DISCOVERED SPEC STORE
# ============================================================

_VISION_REGISTRATION_SPECS: dict[
    str,
    VisionRegistrationSpec
] = {}


# ============================================================
# PART 4 — SPEC DECORATOR
# ============================================================

def vision_spec(
    vision_id: str,
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
    Declarative decorator for registering a ROBOMLM vision specification.

    The decorator DOES NOT execute intelligence logic.

    It only records metadata describing the vision.
    """

    spec = VisionRegistrationSpec(
        vision_id=vision_id,
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

    _validate_vision_spec(spec)

    normalized_id = vision_id.strip().lower()

    if normalized_id in _VISION_REGISTRATION_SPECS:
        existing = _VISION_REGISTRATION_SPECS[normalized_id]

        if existing != spec:
            raise VisionSpecConflictError(
                f"Vision specification already exists with "
                f"different definition: {vision_id}"
            )

    _VISION_REGISTRATION_SPECS[normalized_id] = spec

    def decorator(target):
        setattr(
            target,
            "__robomlm_vision_spec__",
            spec,
        )
        return target

    return decorator


# ============================================================
# PART 4 — DISCOVERY
# ============================================================

def discover_vision_specs() -> list[VisionRegistrationSpec]:
    """
    Return all discovered declarative vision specifications.
    """

    return [
        deepcopy(spec)
        for spec in _VISION_REGISTRATION_SPECS.values()
    ]


def get_vision_spec(
    vision_id: str,
) -> VisionRegistrationSpec:
    """Return a discovered vision specification."""

    normalized_id = vision_id.strip().lower()

    try:
        return deepcopy(
            _VISION_REGISTRATION_SPECS[normalized_id]
        )
    except KeyError as exc:
        raise VisionSpecError(
            f"Vision specification not found: {vision_id}"
        ) from exc


# ============================================================
# PART 4 — REGISTER DISCOVERED SPECS
# ============================================================

def _vision_register_discovered(
    self: VisionRegistry,
    *,
    replace_existing: bool = False,
) -> list[VisionDefinition]:
    """
    Register all discovered vision specifications.

    Dependency resolution is delegated to the registry bootstrap
    mechanism from Part 3.
    """

    specs = discover_vision_specs()

    if not specs:
        return []

    definitions = [
        spec.to_definition()
        for spec in specs
    ]

    if replace_existing:
        snapshot = self.snapshot()

        try:
            for definition in definitions:
                if self.exists(definition.vision_id):
                    self.replace(definition)
                else:
                    self.register(definition)

            self.assert_no_cycles()

            return [
                self.get(definition.vision_id)
                for definition in definitions
            ]

        except Exception:
            self.restore_snapshot(
                snapshot,
                replace_existing=True,
            )
            raise

    return self.bootstrap(definitions)


VisionRegistry.register_discovered = _vision_register_discovered


# ============================================================
# PART 4 — DISCOVERY REPORT
# ============================================================

def _vision_discovery_report() -> dict[str, Any]:
    """Generate a metadata-only discovery report."""

    specs = discover_vision_specs()

    ids = [
        spec.vision_id
        for spec in specs
    ]

    duplicate_ids = [
        vision_id
        for vision_id in set(ids)
        if ids.count(vision_id) > 1
    ]

    invalid_specs = []

    for spec in specs:
        try:
            _validate_vision_spec(spec)
        except Exception as exc:
            invalid_specs.append(
                {
                    "vision_id": spec.vision_id,
                    "error": str(exc),
                }
            )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "discovered_count": len(specs),
        "vision_ids": sorted(ids),
        "duplicate_ids": sorted(set(duplicate_ids)),
        "invalid_specs": invalid_specs,
        "healthy": (
            not duplicate_ids
            and not invalid_specs
        ),
    }


VisionRegistry.discovery_report = staticmethod(
    _vision_discovery_report
)


# ============================================================
# PART 4 — DISCOVERED METADATA EXPORT
# ============================================================

def _vision_export_discovered_metadata() -> list[dict[str, Any]]:
    """Export discovered vision metadata."""

    exported = []

    for spec in discover_vision_specs():
        exported.append(
            {
                "vision_id": spec.vision_id,
                "name": spec.name,
                "version": spec.version,
                "domain": spec.domain,
                "layer": spec.layer,
                "description": spec.description,
                "status": spec.status,
                "owner": spec.owner,
                "dependencies": list(spec.dependencies),
                "tags": list(spec.tags),
                "metadata": deepcopy(spec.metadata),
            }
        )

    return exported


VisionRegistry.export_discovered_vision_metadata = staticmethod(
    _vision_export_discovered_metadata
)


# ============================================================
# PART 4 — SPEC CONSISTENCY CHECK
# ============================================================

def _vision_spec_consistency_check() -> dict[str, Any]:
    """
    Validate consistency between discovered specifications
    and the current registry.
    """

    specs = discover_vision_specs()

    errors: list[str] = []
    warnings: list[str] = []

    seen_ids: set[str] = set()

    for spec in specs:

        normalized_id = spec.vision_id.strip().lower()

        if normalized_id in seen_ids:
            errors.append(
                f"Duplicate discovered vision ID: "
                f"{spec.vision_id}"
            )

        seen_ids.add(normalized_id)

        try:
            _validate_vision_spec(spec)
        except Exception as exc:
            errors.append(
                f"{spec.vision_id}: {exc}"
            )

        if normalized_id in vision_registry._visions:
            registered = vision_registry._visions[
                normalized_id
            ]

            expected = spec.to_definition()

            if registered != expected:
                errors.append(
                    f"Registry mismatch for vision: "
                    f"{spec.vision_id}"
                )
        else:
            warnings.append(
                f"Discovered vision not registered: "
                f"{spec.vision_id}"
            )

    return {
        "registry": REGISTRY_NAME,
        "discovered_count": len(specs),
        "errors": errors,
        "warnings": warnings,
        "healthy": not errors,
    }


VisionRegistry.spec_consistency_check = staticmethod(
    _vision_spec_consistency_check
)


# ============================================================
# PART 4 — DISCOVERY AUDIT
# ============================================================

def _vision_discovery_audit() -> dict[str, Any]:
    """Run complete discovery-level audit."""

    report = _vision_discovery_report()
    consistency = _vision_spec_consistency_check()

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "discovery": report,
        "consistency": consistency,
        "healthy": (
            report["healthy"]
            and consistency["healthy"]
        ),
    }


VisionRegistry.discovery_audit = staticmethod(
    _vision_discovery_audit
)


# ============================================================
# PART 4 — DISCOVERY HEALTH ASSERTION
# ============================================================

def _vision_assert_discovery_healthy() -> bool:
    """Raise VisionDiscoveryError when discovery is unhealthy."""

    audit = _vision_discovery_audit()

    if not audit["healthy"]:
        raise VisionDiscoveryError(
            "Vision discovery audit failed: "
            f"{audit}"
        )

    return True


VisionRegistry.assert_discovery_healthy = staticmethod(
    _vision_assert_discovery_healthy
)


# ============================================================
# PART 4 — DISCOVERY SUMMARY
# ============================================================

def vision_discovery_summary() -> dict[str, Any]:
    """Public helper for discovery summary."""

    return vision_registry.discovery_report()


# ============================================================
# PART 4 — END
# ============================================================
# ============================================================
# VISION REGISTRY — PART 5
# Freeze, Atomic Governance, Canonical Catalog & Final Install
# ============================================================


# ============================================================
# PART 5 — EXCEPTIONS
# ============================================================

class VisionRegistryFrozenError(VisionRegistryError):
    """Raised when a mutation is attempted on a frozen registry."""


class VisionAtomicInstallError(VisionRegistryError):
    """Raised when an atomic vision installation fails."""


class VisionCanonicalCatalogError(VisionRegistryError):
    """Raised when the canonical vision catalog is invalid."""


# ============================================================
# PART 5 — FREEZE GOVERNANCE
# ============================================================

def _vision_assert_mutable(self: VisionRegistry) -> None:
    """Ensure that registry mutations are allowed."""

    if getattr(self, "_frozen", False):
        raise VisionRegistryFrozenError(
            "Vision registry is frozen"
        )


def _vision_freeze(self: VisionRegistry) -> bool:
    """Freeze the registry against normal mutations."""

    self._frozen = True
    return True


def _vision_unfreeze(self: VisionRegistry) -> bool:
    """Unfreeze the registry."""

    self._frozen = False
    return True


def _vision_is_frozen(self: VisionRegistry) -> bool:
    """Return current freeze state."""

    return bool(
        getattr(self, "_frozen", False)
    )


VisionRegistry.assert_mutable = _vision_assert_mutable
VisionRegistry.freeze = _vision_freeze
VisionRegistry.unfreeze = _vision_unfreeze
VisionRegistry.is_frozen = _vision_is_frozen


# ============================================================
# PART 5 — GUARDED MUTATION WRAPPERS
# ============================================================

_vision_original_register = VisionRegistry.register
_vision_original_register_many = VisionRegistry.register_many
_vision_original_replace = VisionRegistry.replace
_vision_original_unregister = VisionRegistry.unregister
_vision_original_set_status = VisionRegistry.set_status


def _vision_guarded_register(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:

    self.assert_mutable()

    return _vision_original_register(
        self,
        definition,
    )


def _vision_guarded_register_many(
    self: VisionRegistry,
    definitions: Iterable[VisionDefinition],
) -> list[VisionDefinition]:

    self.assert_mutable()

    return _vision_original_register_many(
        self,
        definitions,
    )


def _vision_guarded_replace(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:

    self.assert_mutable()

    return _vision_original_replace(
        self,
        definition,
    )


def _vision_guarded_unregister(
    self: VisionRegistry,
    vision_id: str,
    force: bool = False,
) -> VisionDefinition:

    self.assert_mutable()

    return _vision_original_unregister(
        self,
        vision_id,
        force=force,
    )


def _vision_guarded_set_status(
    self: VisionRegistry,
    vision_id: str,
    status: str,
) -> VisionDefinition:

    self.assert_mutable()

    return _vision_original_set_status(
        self,
        vision_id,
        status,
    )


VisionRegistry.register = _vision_guarded_register
VisionRegistry.register_many = _vision_guarded_register_many
VisionRegistry.replace = _vision_guarded_replace
VisionRegistry.unregister = _vision_guarded_unregister
VisionRegistry.set_status = _vision_guarded_set_status


# ============================================================
# PART 5 — CLONE
# ============================================================

def _vision_clone(
    self: VisionRegistry,
) -> VisionRegistry:
    """
    Create an isolated registry clone.

    The clone contains independent VisionDefinition objects
    and preserves freeze state.
    """

    clone = VisionRegistry()

    clone._visions = deepcopy(
        self._visions
    )

    clone._frozen = getattr(
        self,
        "_frozen",
        False,
    )

    if hasattr(clone, "rebuild_indexes"):
        clone.rebuild_indexes()

    return clone


VisionRegistry.clone = _vision_clone


# ============================================================
# PART 5 — ATOMIC REGISTER
# ============================================================

def _vision_atomic_register(
    self: VisionRegistry,
    definition: VisionDefinition,
) -> VisionDefinition:
    """
    Register one vision atomically.

    Registry state is restored if registration fails.
    """

    self.assert_mutable()

    snapshot = self.snapshot()

    try:
        result = _vision_original_register(
            self,
            definition,
        )

        self.rebuild_indexes()

        return result

    except Exception as exc:

        try:
            self._restore_snapshot_internal(
                snapshot
            )
        except Exception as restore_exc:
            raise VisionAtomicInstallError(
                "Vision registration failed and "
                "registry rollback also failed"
            ) from restore_exc

        raise VisionAtomicInstallError(
            f"Atomic vision registration failed: {exc}"
        ) from exc


VisionRegistry.atomic_register = _vision_atomic_register


# ============================================================
# PART 5 — ATOMIC SPEC INSTALL
# ============================================================

def _vision_atomic_register_specs(
    self: VisionRegistry,
    specs: Iterable[VisionRegistrationSpec],
) -> list[VisionDefinition]:
    """
    Atomically install multiple vision specifications.
    """

    self.assert_mutable()

    specs = list(specs)

    for spec in specs:
        _validate_vision_spec(spec)

    definitions = [
        spec.to_definition()
        for spec in specs
    ]

    snapshot = self.snapshot()

    try:
        result = self.bootstrap(
            definitions
        )

        self.rebuild_indexes()

        self.assert_no_cycles()

        return result

    except Exception as exc:

        try:
            self._restore_snapshot_internal(
                snapshot
            )
            self.rebuild_indexes()

        except Exception as restore_exc:

            raise VisionAtomicInstallError(
                "Atomic vision-spec installation failed "
                "and rollback failed"
            ) from restore_exc

        raise VisionAtomicInstallError(
            f"Atomic vision-spec installation failed: {exc}"
        ) from exc


VisionRegistry.atomic_register_specs = (
    _vision_atomic_register_specs
)


# ============================================================
# PART 5 — CANONICAL VISION DOMAINS
# ============================================================

VISION_DOMAIN_MARKET = "market"
VISION_DOMAIN_EQUITY = "equity"
VISION_DOMAIN_CRYPTO = "crypto"
VISION_DOMAIN_FOREX = "forex"
VISION_DOMAIN_COMMODITY = "commodity"
VISION_DOMAIN_INDEX = "index"
VISION_DOMAIN_MULTI_ASSET = "multi_asset"


# ============================================================
# PART 5 — CANONICAL VISION LAYERS
# ============================================================

VISION_LAYER_OBSERVATION = "observation"
VISION_LAYER_CONTEXT = "context"
VISION_LAYER_OPPORTUNITY = "opportunity"
VISION_LAYER_OUTLOOK = "outlook"


# ============================================================
# PART 5 — CANONICAL VISION BUILDER
# ============================================================

def _canonical_vision(
    vision_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str,
    dependencies: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    metadata: Optional[dict[str, Any]] = None,
) -> VisionRegistrationSpec:

    return VisionRegistrationSpec(
        vision_id=vision_id,
        name=name,
        version=version,
        domain=domain,
        layer=layer,
        description=description,
        status="active",
        owner="ROBOMLM",
        dependencies=dependencies,
        tags=tags,
        metadata=metadata or {},
    )


# ============================================================
# PART 5 — CANONICAL VISION CATALOG
# ============================================================
#
# NOTE:
# These are architecture-level declarative vision identities.
# They do NOT implement prediction formulas or intelligence.
#
# The exact canonical catalog must remain subject to
# blueprint audit before production freeze.
# ============================================================

ROBOMLM_CANONICAL_VISION_SPECS = (

    _canonical_vision(
        vision_id="market_observation_vision",
        name="Market Observation Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_MARKET,
        layer=VISION_LAYER_OBSERVATION,
        description=(
            "Unified market observation identity "
            "across connected instruments."
        ),
        tags=(
            "market",
            "observation",
            "multi_asset",
        ),
    ),

    _canonical_vision(
        vision_id="market_context_vision",
        name="Market Context Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_MARKET,
        layer=VISION_LAYER_CONTEXT,
        description=(
            "Declarative market-context intelligence "
            "identity derived from governed evidence."
        ),
        dependencies=(
            "market_observation_vision",
        ),
        tags=(
            "market",
            "context",
        ),
    ),

    _canonical_vision(
        vision_id="structure_breakout_vision",
        name="Structure Breakout Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_EQUITY,
        layer=VISION_LAYER_OPPORTUNITY,
        description=(
            "Declarative identity for structure and "
            "breakout-oriented market analysis."
        ),
        dependencies=(
            "market_context_vision",
        ),
        tags=(
            "equity",
            "structure",
            "breakout",
        ),
    ),

    _canonical_vision(
        vision_id="accumulation_distribution_vision",
        name="Accumulation Distribution Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_EQUITY,
        layer=VISION_LAYER_OPPORTUNITY,
        description=(
            "Declarative identity for accumulation and "
            "distribution analysis."
        ),
        dependencies=(
            "market_context_vision",
        ),
        tags=(
            "equity",
            "accumulation",
            "distribution",
        ),
    ),

    _canonical_vision(
        vision_id="breakout_confirmation_vision",
        name="Breakout Confirmation Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_EQUITY,
        layer=VISION_LAYER.OUTLOOK
        if False else VISION_LAYER_OPPORTUNITY,
        description=(
            "Declarative identity for breakout "
            "confirmation analysis."
        ),
        dependencies=(
            "structure_breakout_vision",
        ),
        tags=(
            "equity",
            "breakout",
            "confirmation",
        ),
    ),

    _canonical_vision(
        vision_id="multi_asset_opportunity_vision",
        name="Multi Asset Opportunity Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_MULTI_ASSET,
        layer=VISION_LAYER_OPPORTUNITY,
        description=(
            "Declarative identity for globally ranked "
            "multi-asset opportunity analysis."
        ),
        dependencies=(
            "market_context_vision",
        ),
        tags=(
            "multi_asset",
            "opportunity",
            "ranking",
        ),
    ),

    _canonical_vision(
        vision_id="decision_outlook_vision",
        name="Decision Outlook Vision",
        version="1.0.0",
        domain=VISION_DOMAIN_MARKET,
        layer=VISION_LAYER_OUTLOOK,
        description=(
            "Declarative identity for governed "
            "decision-outlook representation."
        ),
        dependencies=(
            "multi_asset_opportunity_vision",
        ),
        tags=(
            "decision",
            "outlook",
        ),
    ),
)


# ============================================================
# PART 5 — CANONICAL CATALOG VALIDATION
# ============================================================

def validate_canonical_vision_catalog() -> dict[str, Any]:
    """Validate canonical vision specifications."""

    errors: list[str] = []
    ids: list[str] = []

    for spec in ROBOMLM_CANONICAL_VISION_SPECS:

        try:
            _validate_vision_spec(spec)
        except Exception as exc:
            errors.append(
                f"{spec.vision_id}: {exc}"
            )

        normalized_id = (
            spec.vision_id.strip().lower()
        )

        if normalized_id in ids:
            errors.append(
                f"Duplicate canonical vision ID: "
                f"{spec.vision_id}"
            )

        ids.append(normalized_id)

    canonical_ids = set(ids)

    for spec in ROBOMLM_CANONICAL_VISION_SPECS:

        for dependency in spec.dependencies:

            normalized_dependency = (
                dependency.strip().lower()
            )

            if normalized_dependency not in canonical_ids:
                errors.append(
                    f"{spec.vision_id}: missing canonical "
                    f"dependency '{dependency}'"
                )

            if normalized_dependency == (
                spec.vision_id.strip().lower()
            ):
                errors.append(
                    f"{spec.vision_id}: self dependency"
                )

    return {
        "catalog": "ROBOMLM_CANONICAL_VISION_SPECS",
        "count": len(
            ROBOMLM_CANONICAL_VISION_SPECS
        ),
        "vision_ids": [
            spec.vision_id
            for spec in ROBOMLM_CANONICAL_VISION_SPECS
        ],
        "errors": errors,
        "healthy": not errors,
    }


# ============================================================
# PART 5 — REGISTER CANONICAL VISIONS
# ============================================================

def register_canonical_visions(
    registry: Optional[VisionRegistry] = None,
) -> list[VisionDefinition]:

    target = registry or vision_registry

    validation = (
        validate_canonical_vision_catalog()
    )

    if not validation["healthy"]:
        raise VisionCanonicalCatalogError(
            f"Invalid canonical vision catalog: "
            f"{validation['errors']}"
        )

    return target.atomic_register_specs(
        ROBOMLM_CANONICAL_VISION_SPECS
    )


# ============================================================
# PART 5 — CANONICAL IDS
# ============================================================

def canonical_vision_ids() -> tuple[str, ...]:
    """Return canonical vision identifiers."""

    return tuple(
        spec.vision_id
        for spec in ROBOMLM_CANONICAL_VISION_SPECS
    )


# ============================================================
# PART 5 — CANONICAL REPORT
# ============================================================

def canonical_vision_report() -> dict[str, Any]:
    """Return canonical vision catalog report."""

    validation = (
        validate_canonical_vision_catalog()
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "canonical_count": validation["count"],
        "canonical_ids": validation["vision_ids"],
        "errors": validation["errors"],
        "healthy": validation["healthy"],
    }


# ============================================================
# PART 5 — CANONICAL AUDIT
# ============================================================

def canonical_vision_audit(
    registry: Optional[VisionRegistry] = None,
) -> dict[str, Any]:

    target = registry or vision_registry

    catalog = (
        validate_canonical_vision_catalog()
    )

    registered_ids = set(
        target.vision_ids()
    )

    missing = [
        vision_id
        for vision_id in catalog["vision_ids"]
        if vision_id.strip().lower()
        not in registered_ids
    ]

    mismatched: list[str] = []

    for spec in ROBOMLM_CANONICAL_VISION_SPECS:

        normalized_id = (
            spec.vision_id.strip().lower()
        )

        if normalized_id not in target._visions:
            continue

        expected = spec.to_definition()
        actual = target._visions[
            normalized_id
        ]

        if actual != expected:
            mismatched.append(
                spec.vision_id
            )

    healthy = (
        catalog["healthy"]
        and not missing
        and not mismatched
    )

    return {
        "catalog": catalog,
        "missing": missing,
        "mismatched": mismatched,
        "healthy": healthy,
    }


# ============================================================
# PART 5 — FULL GOVERNANCE AUDIT
# ============================================================

def vision_full_governance_audit(
    registry: Optional[VisionRegistry] = None,
) -> dict[str, Any]:

    target = registry or vision_registry

    definition_audit = target.full_audit()

    discovery_audit = (
        target.discovery_audit()
    )

    canonical_audit = (
        canonical_vision_audit(target)
    )

    healthy = (
        definition_audit["healthy"]
        and discovery_audit["healthy"]
        and canonical_audit["healthy"]
    )

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "definition_audit": definition_audit,
        "discovery_audit": discovery_audit,
        "canonical_audit": canonical_audit,
        "healthy": healthy,
    }


# ============================================================
# PART 5 — FULL HEALTH ASSERTION
# ============================================================

def vision_assert_full_health(
    registry: Optional[VisionRegistry] = None,
) -> bool:

    audit = vision_full_governance_audit(
        registry
    )

    if not audit["healthy"]:
        raise VisionRegistryError(
            f"Vision registry governance audit failed: "
            f"{audit}"
        )

    return True


# ============================================================
# PART 5 — FREEZE ONLY WHEN HEALTHY
# ============================================================

def freeze_vision_registry_if_healthy(
    registry: Optional[VisionRegistry] = None,
) -> bool:

    target = registry or vision_registry

    vision_assert_full_health(
        target
    )

    target.freeze()

    return target.is_frozen()


# ============================================================
# PART 5 — FINAL EXPORT
# ============================================================

def vision_final_export(
    registry: Optional[VisionRegistry] = None,
) -> dict[str, Any]:

    target = registry or vision_registry

    return {
        "registry": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "frozen": target.is_frozen(),
        "state": target.state(),
        "metadata": target.export_metadata(),
        "canonical": canonical_vision_report(),
        "discovery": target.discovery_report(),
        "governance": vision_full_governance_audit(
            target
        ),
    }


# ============================================================
# PART 5 — COMPLETE INSTALL
# ============================================================

def install_vision_registry(
    *,
    include_discovered: bool = True,
    freeze_after_install: bool = False,
    reset_first: bool = False,
) -> dict[str, Any]:
    """
    Complete Vision Registry installation.

    Order:
        1. Validate canonical catalog
        2. Optionally reset
        3. Install canonical visions
        4. Install discovered specifications
        5. Rebuild indexes
        6. Run full governance audit
        7. Optionally freeze
    """

    target = vision_registry

    if reset_first:
        reset_vision_registry_for_testing()

    target.assert_mutable()

    outer_snapshot = target.snapshot()

    try:

        # ----------------------------------------------------
        # Canonical validation
        # ----------------------------------------------------

        canonical_validation = (
            validate_canonical_vision_catalog()
        )

        if not canonical_validation["healthy"]:
            raise VisionCanonicalCatalogError(
                canonical_validation["errors"]
            )

        # ----------------------------------------------------
        # Canonical installation
        # ----------------------------------------------------

        if ROBOMLM_CANONICAL_VISION_SPECS:

            target.atomic_register_specs(
                ROBOMLM_CANONICAL_VISION_SPECS
            )

        # ----------------------------------------------------
        # Discovered installation
        # ----------------------------------------------------

        if include_discovered:

            discovered = (
                discover_vision_specs()
            )

            canonical_ids = {
                spec.vision_id.strip().lower()
                for spec
                in ROBOMLM_CANONICAL_VISION_SPECS
            }

            non_canonical = [
                spec
                for spec in discovered
                if spec.vision_id.strip().lower()
                not in canonical_ids
            ]

            if non_canonical:
                target.atomic_register_specs(
                    non_canonical
                )

        # ----------------------------------------------------
        # Rebuild indexes
        # ----------------------------------------------------

        target.rebuild_indexes()

        # ----------------------------------------------------
        # Full audit
        # ----------------------------------------------------

        audit = vision_full_governance_audit(
            target
        )

        if not audit["healthy"]:
            raise VisionAtomicInstallError(
                f"Vision installation audit failed: "
                f"{audit}"
            )

        # ----------------------------------------------------
        # Optional freeze
        # ----------------------------------------------------

        if freeze_after_install:
            target.freeze()

        return vision_final_export(
            target
        )

    except Exception as exc:

        try:
            target._restore_snapshot_internal(
                outer_snapshot
            )
            target.rebuild_indexes()

        except Exception as restore_exc:

            raise VisionAtomicInstallError(
                "Vision installation failed and "
                "outer rollback failed"
            ) from restore_exc

        raise VisionAtomicInstallError(
            f"Complete vision registry installation failed: "
            f"{exc}"
        ) from exc


# ============================================================
# PART 5 — TEST RESET
# ============================================================

def reset_vision_registry_for_testing() -> None:
    """
    Reset the global vision registry.

    Intended for controlled testing/bootstrap environments.
    """

    vision_registry._frozen = False
    vision_registry._visions.clear()

    if hasattr(
        vision_registry,
        "rebuild_indexes",
    ):
        vision_registry.rebuild_indexes()


# ============================================================
# PART 5 — CANONICAL SUMMARY
# ============================================================

def canonical_vision_summary() -> dict[str, Any]:
    """Compact canonical vision summary."""

    return {
        "count": len(
            ROBOMLM_CANONICAL_VISION_SPECS
        ),
        "vision_ids": canonical_vision_ids(),
        "domains": sorted(
            {
                spec.domain
                for spec
                in ROBOMLM_CANONICAL_VISION_SPECS
            }
        ),
        "layers": sorted(
            {
                spec.layer
                for spec
                in ROBOMLM_CANONICAL_VISION_SPECS
            }
        ),
        "healthy": (
            validate_canonical_vision_catalog()
            ["healthy"]
        ),
    }


# ============================================================
# PART 5 — END
# ============================================================