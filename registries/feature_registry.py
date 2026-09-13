"""
ROBOMLM_PLUS
Feature Registry
Part 1 — Registry Foundation

Purpose:
    Central registration and controlled lookup of ROBOMLM
    features.

Architecture rule:
    Registry describes and discovers FEATURES.
    Registry does NOT calculate feature values.
    Registry does NOT contain trading formulas.
    Registry does NOT make decisions.
    Registry does NOT execute trades.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping


# ============================================================
# CONSTANTS
# ============================================================

REGISTRY_NAME = "feature_registry"
REGISTRY_VERSION = "1.0.0"


VALID_FEATURE_STATUSES = frozenset(
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


class FeatureRegistryError(Exception):
    """Base exception for feature registry failures."""


class FeatureAlreadyRegisteredError(
    FeatureRegistryError
):
    """Raised when a feature is registered more than once."""


class FeatureNotFoundError(
    FeatureRegistryError
):
    """Raised when a requested feature does not exist."""


class InvalidFeatureDefinitionError(
    FeatureRegistryError
):
    """Raised when a feature definition is invalid."""


class FeatureStateError(
    FeatureRegistryError
):
    """Raised when an invalid feature lifecycle operation occurs."""


# ============================================================
# FEATURE DEFINITION
# ============================================================


@dataclass(frozen=True)
class FeatureDefinition:
    """
    Immutable metadata contract for one ROBOMLM feature.

    This describes a feature.

    It does NOT contain:
        - feature calculation
        - trading formulas
        - signal generation
        - decision authority
        - execution logic
    """

    feature_id: str
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

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ============================================================
# FEATURE REGISTRY
# ============================================================


class FeatureRegistry:
    """
    Central registry for ROBOMLM feature definitions.

    Responsibilities:
        1. Register features.
        2. Validate feature metadata.
        3. Lookup features.
        4. Check feature existence.
        5. List registered features.
        6. Filter features by domain/layer/status.

    Non-responsibilities:
        - Feature calculation
        - Formula execution
        - Market analysis
        - Trading decision
        - Order execution
    """

    def __init__(self) -> None:
        self._features: dict[
            str,
            FeatureDefinition,
        ] = {}

    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        feature: FeatureDefinition,
    ) -> FeatureDefinition:
        """
        Register a new feature definition.
        """

        self._validate_definition(feature)

        if feature.feature_id in self._features:
            raise FeatureAlreadyRegisteredError(
                f"Feature already registered: "
                f"{feature.feature_id}"
            )

        self._features[
            feature.feature_id
        ] = feature

        return feature

    # ========================================================
    # REGISTER MANY
    # ========================================================

    def register_many(
        self,
        features: Iterable[FeatureDefinition],
    ) -> tuple[FeatureDefinition, ...]:
        """
        Register multiple feature definitions.

        All definitions are validated before insertion.
        """

        definitions = tuple(features)

        seen_ids: set[str] = set()

        for feature in definitions:

            self._validate_definition(feature)

            if feature.feature_id in seen_ids:
                raise FeatureAlreadyRegisteredError(
                    "Duplicate feature ID in registration batch: "
                    f"{feature.feature_id}"
                )

            seen_ids.add(feature.feature_id)

            if feature.feature_id in self._features:
                raise FeatureAlreadyRegisteredError(
                    f"Feature already registered: "
                    f"{feature.feature_id}"
                )

        for feature in definitions:
            self._features[
                feature.feature_id
            ] = feature

        return definitions

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        feature_id: str,
    ) -> FeatureDefinition:
        """
        Return one registered feature.
        """

        normalized_id = self._normalize_feature_id(
            feature_id
        )

        try:
            return self._features[
                normalized_id
            ]

        except KeyError as exc:

            raise FeatureNotFoundError(
                f"Feature not found: "
                f"{normalized_id}"
            ) from exc

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        feature_id: str,
    ) -> bool:
        """
        Check whether a feature is registered.
        """

        normalized_id = self._normalize_feature_id(
            feature_id
        )

        return normalized_id in self._features

    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return total registered feature count.
        """

        return len(self._features)

    # ========================================================
    # LIST ALL
    # ========================================================

    def list_all(
        self,
    ) -> tuple[FeatureDefinition, ...]:
        """
        Return all registered features.
        """

        return tuple(
            self._features.values()
        )

    # ========================================================
    # LIST BY DOMAIN
    # ========================================================

    def list_by_domain(
        self,
        domain: str,
    ) -> tuple[FeatureDefinition, ...]:
        """
        Return features belonging to a domain.
        """

        normalized_domain = self._normalize_text(
            domain,
            "domain",
        )

        return tuple(
            feature
            for feature in self._features.values()
            if feature.domain == normalized_domain
        )

    # ========================================================
    # LIST BY LAYER
    # ========================================================

    def list_by_layer(
        self,
        layer: str,
    ) -> tuple[FeatureDefinition, ...]:
        """
        Return features belonging to an architecture layer.
        """

        normalized_layer = self._normalize_text(
            layer,
            "layer",
        )

        return tuple(
            feature
            for feature in self._features.values()
            if feature.layer == normalized_layer
        )

    # ========================================================
    # LIST BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> tuple[FeatureDefinition, ...]:
        """
        Return features matching lifecycle status.
        """

        normalized_status = self._normalize_text(
            status,
            "status",
        )

        if normalized_status not in VALID_FEATURE_STATUSES:
            raise InvalidFeatureDefinitionError(
                f"Invalid feature status: "
                f"{normalized_status}"
            )

        return tuple(
            feature
            for feature in self._features.values()
            if feature.status == normalized_status
        )

    # ========================================================
    # TAG SEARCH
    # ========================================================

    def list_by_tag(
        self,
        tag: str,
    ) -> tuple[FeatureDefinition, ...]:
        """
        Return features containing a specific tag.
        """

        normalized_tag = self._normalize_text(
            tag,
            "tag",
        )

        return tuple(
            feature
            for feature in self._features.values()
            if normalized_tag in feature.tags
        )

    # ========================================================
    # INTERNAL VALIDATION
    # ========================================================

    @staticmethod
    def _validate_definition(
        feature: FeatureDefinition,
    ) -> None:
        """
        Validate structural integrity of a feature definition.
        """

        if not isinstance(
            feature,
            FeatureDefinition,
        ):
            raise InvalidFeatureDefinitionError(
                "Feature must be a "
                "FeatureDefinition instance."
            )

        FeatureRegistry._normalize_feature_id(
            feature.feature_id
        )

        FeatureRegistry._normalize_text(
            feature.name,
            "name",
        )

        FeatureRegistry._normalize_text(
            feature.version,
            "version",
        )

        FeatureRegistry._normalize_text(
            feature.domain,
            "domain",
        )

        FeatureRegistry._normalize_text(
            feature.layer,
            "layer",
        )

        if feature.status not in VALID_FEATURE_STATUSES:
            raise InvalidFeatureDefinitionError(
                f"Invalid feature status: "
                f"{feature.status}"
            )

        if not isinstance(
            feature.dependencies,
            tuple,
        ):
            raise InvalidFeatureDefinitionError(
                "Feature dependencies must be "
                "a tuple."
            )

        if len(
            set(feature.dependencies)
        ) != len(feature.dependencies):

            raise InvalidFeatureDefinitionError(
                f"Duplicate dependencies found for "
                f"feature: {feature.feature_id}"
            )

        for dependency in feature.dependencies:

            FeatureRegistry._normalize_feature_id(
                dependency
            )

    # ========================================================
    # NORMALIZE FEATURE ID
    # ========================================================

    @staticmethod
    def _normalize_feature_id(
        feature_id: str,
    ) -> str:
        """
        Normalize and validate a feature identifier.
        """

        if not isinstance(
            feature_id,
            str,
        ):
            raise InvalidFeatureDefinitionError(
                "feature_id must be a string."
            )

        normalized = feature_id.strip()

        if not normalized:
            raise InvalidFeatureDefinitionError(
                "feature_id cannot be empty."
            )

        return normalized

    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def _normalize_text(
        value: str,
        field_name: str,
    ) -> str:
        """
        Normalize a required text field.
        """

        if not isinstance(
            value,
            str,
        ):
            raise InvalidFeatureDefinitionError(
                f"{field_name} must be a string."
            )

        normalized = value.strip()

        if not normalized:
            raise InvalidFeatureDefinitionError(
                f"{field_name} cannot be empty."
            )

        return normalized


# ============================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================

feature_registry = FeatureRegistry()


# ============================================================
# REGISTRATION HELPER
# ============================================================


def register_feature(
    feature_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    dependencies: Iterable[str] = (),
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: Iterable[str] = (),
    metadata: Mapping[str, Any] | None = None,
) -> FeatureDefinition:
    """
    Convenience helper for creating and registering a feature.

    This function creates metadata only.

    It does NOT calculate the feature.
    """

    definition = FeatureDefinition(
        feature_id=feature_id.strip(),
        name=name.strip(),
        version=version.strip(),
        domain=domain.strip(),
        layer=layer.strip(),
        description=description.strip(),
        dependencies=tuple(
            dependency.strip()
            for dependency in dependencies
        ),
        status=status,
        owner=owner.strip(),
        tags=tuple(
            tag.strip()
            for tag in tags
        ),
        metadata=dict(
            metadata or {}
        ),
    )

    return feature_registry.register(
        definition
    )
# ============================================================
# FEATURE REGISTRY — PART 2
# Dependency Validation + Lifecycle + Graph + Health
# ============================================================

from dataclasses import replace


# ============================================================
# ADDITIONAL EXCEPTIONS
# ============================================================

class FeatureDependencyError(FeatureRegistryError):
    """Raised when feature dependencies are invalid."""


class FeatureVersionError(FeatureRegistryError):
    """Raised when feature version validation fails."""


class FeatureRegistrationConflictError(FeatureRegistryError):
    """Raised when feature registration conflicts with existing state."""


class FeatureUnregisterError(FeatureRegistryError):
    """Raised when feature removal is not allowed."""


# ============================================================
# LIFECYCLE MANAGEMENT
# ============================================================

def _feature_set_status(
    self,
    feature_id: str,
    status: str,
) -> FeatureDefinition:

    feature_id = self._normalize_feature_id(feature_id)

    if status not in VALID_FEATURE_STATUSES:
        raise FeatureStateError(
            f"Invalid feature status: {status}"
        )

    feature = self.get(feature_id)

    updated = replace(
        feature,
        status=status,
    )

    self._engines[feature_id] = updated
    return updated


def _feature_activate(self, feature_id: str) -> FeatureDefinition:
    return self.set_status(feature_id, "active")


def _feature_disable(self, feature_id: str) -> FeatureDefinition:
    return self.set_status(feature_id, "disabled")


def _feature_deprecate(self, feature_id: str) -> FeatureDefinition:
    return self.set_status(feature_id, "deprecated")


FeatureRegistry.set_status = _feature_set_status
FeatureRegistry.activate = _feature_activate
FeatureRegistry.disable = _feature_disable
FeatureRegistry.deprecate = _feature_deprecate


# ============================================================
# DEPENDENCY VALIDATION
# ============================================================

def _feature_validate_dependencies(
    self,
    feature_id: str,
) -> bool:

    feature_id = self._normalize_feature_id(feature_id)

    feature = self.get(feature_id)

    missing = [
        dependency
        for dependency in feature.dependencies
        if dependency not in self._features
    ]

    if missing:
        raise FeatureDependencyError(
            f"Feature '{feature_id}' has missing dependencies: "
            f"{', '.join(missing)}"
        )

    return True


def _feature_validate_all_dependencies(self) -> bool:

    errors = {}

    for feature_id in self._features:
        try:
            self.validate_dependencies(feature_id)
        except FeatureDependencyError as exc:
            errors[feature_id] = str(exc)

    if errors:
        raise FeatureDependencyError(
            f"Feature dependency validation failed: {errors}"
        )

    return True


FeatureRegistry.validate_dependencies = _feature_validate_dependencies
FeatureRegistry.validate_all_dependencies = (
    _feature_validate_all_dependencies
)


# ============================================================
# DEPENDENCY GRAPH
# ============================================================

def _feature_dependency_graph(self) -> dict[str, tuple[str, ...]]:

    return {
        feature_id: tuple(feature.dependencies)
        for feature_id, feature in self._features.items()
    }


FeatureRegistry.dependency_graph = _feature_dependency_graph


# ============================================================
# DEPENDENTS
# ============================================================

def _feature_dependents(
    self,
    feature_id: str,
) -> tuple[str, ...]:

    feature_id = self._normalize_feature_id(feature_id)

    if feature_id not in self._features:
        raise FeatureNotFoundError(
            f"Feature not found: {feature_id}"
        )

    result = []

    for candidate_id, candidate in self._features.items():
        if feature_id in candidate.dependencies:
            result.append(candidate_id)

    return tuple(sorted(result))


FeatureRegistry.dependents = _feature_dependents


# ============================================================
# CYCLE DETECTION
# ============================================================

def _feature_detect_cycles(self) -> list[tuple[str, ...]]:

    graph = self.dependency_graph()

    cycles = []
    visited = set()

    def dfs(
        node: str,
        path: list[str],
        active: set[str],
    ) -> None:

        if node in active:
            start = path.index(node)
            cycle = tuple(path[start:] + [node])

            if cycle not in cycles:
                cycles.append(cycle)

            return

        if node in visited:
            return

        active.add(node)
        path.append(node)

        for dependency in graph.get(node, ()):
            if dependency in graph:
                dfs(
                    dependency,
                    path,
                    active,
                )

        path.pop()
        active.remove(node)
        visited.add(node)

    for feature_id in graph:
        if feature_id not in visited:
            dfs(
                feature_id,
                [],
                set(),
            )

    return cycles


FeatureRegistry.detect_cycles = _feature_detect_cycles


def _feature_assert_no_cycles(self) -> bool:

    cycles = self.detect_cycles()

    if cycles:
        formatted = "; ".join(
            " -> ".join(cycle)
            for cycle in cycles
        )

        raise FeatureDependencyError(
            f"Feature dependency cycle detected: {formatted}"
        )

    return True


FeatureRegistry.assert_no_cycles = _feature_assert_no_cycles


# ============================================================
# REPLACE EXISTING FEATURE
# ============================================================

def _feature_replace(
    self,
    definition: FeatureDefinition,
) -> FeatureDefinition:

    self._validate_definition(definition)

    feature_id = definition.feature_id

    if feature_id not in self._features:
        raise FeatureNotFoundError(
            f"Feature not found: {feature_id}"
        )

    self._features[feature_id] = definition

    return definition


FeatureRegistry.replace = _feature_replace


# ============================================================
# CONFLICT CHECK
# ============================================================

def _feature_check_conflict(
    self,
    definition: FeatureDefinition,
) -> bool:

    self._validate_definition(definition)

    existing = self._features.get(
        definition.feature_id
    )

    if existing is None:
        return False

    return existing != definition


FeatureRegistry.check_conflict = _feature_check_conflict


# ============================================================
# SAFE REGISTRATION
# ============================================================

def _feature_register_safe(
    self,
    definition: FeatureDefinition,
) -> FeatureDefinition:

    self._validate_definition(definition)

    existing = self._features.get(
        definition.feature_id
    )

    if existing is None:
        return self.register(definition)

    if existing == definition:
        return existing

    raise FeatureRegistrationConflictError(
        f"Feature '{definition.feature_id}' already exists "
        f"with a different definition."
    )


FeatureRegistry.register_safe = _feature_register_safe


# ============================================================
# REGISTRATION WITH DEPENDENCY VALIDATION
# ============================================================

def _feature_register_with_dependencies(
    self,
    definition: FeatureDefinition,
) -> FeatureDefinition:

    self._validate_definition(definition)

    for dependency in definition.dependencies:

        if dependency == definition.feature_id:
            raise FeatureDependencyError(
                f"Feature '{definition.feature_id}' "
                f"cannot depend on itself."
            )

        if dependency not in self._features:
            raise FeatureDependencyError(
                f"Cannot register feature "
                f"'{definition.feature_id}': "
                f"missing dependency '{dependency}'."
            )

    result = self.register_safe(definition)

    self.assert_no_cycles()

    return result


FeatureRegistry.register_with_dependencies = (
    _feature_register_with_dependencies
)


# ============================================================
# UNREGISTER
# ============================================================

def _feature_unregister(
    self,
    feature_id: str,
    force: bool = False,
) -> FeatureDefinition:

    feature_id = self._normalize_feature_id(feature_id)

    feature = self.get(feature_id)

    dependents = self.dependents(feature_id)

    if dependents and not force:
        raise FeatureUnregisterError(
            f"Cannot unregister feature '{feature_id}'. "
            f"Dependent features exist: "
            f"{', '.join(dependents)}"
        )

    del self._features[feature_id]

    return feature


FeatureRegistry.unregister = _feature_unregister


# ============================================================
# ACTIVE FEATURES
# ============================================================

def _feature_active_features(
    self,
) -> tuple[FeatureDefinition, ...]:

    return tuple(
        feature
        for feature in self._features.values()
        if feature.status == "active"
    )


FeatureRegistry.active_features = _feature_active_features


# ============================================================
# FEATURE IDS
# ============================================================

def _feature_ids(self) -> tuple[str, ...]:

    return tuple(
        sorted(self._features.keys())
    )


FeatureRegistry.feature_ids = _feature_ids


# ============================================================
# SUMMARY
# ============================================================

def _feature_summary(self) -> dict:

    status_counts = {
        status: 0
        for status in VALID_FEATURE_STATUSES
    }

    domain_counts = {}
    layer_counts = {}

    for feature in self._features.values():

        status_counts[feature.status] += 1

        domain_counts[feature.domain] = (
            domain_counts.get(feature.domain, 0) + 1
        )

        layer_counts[feature.layer] = (
            layer_counts.get(feature.layer, 0) + 1
        )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "total_features": len(self._features),
        "status_counts": status_counts,
        "domain_counts": dict(sorted(domain_counts.items())),
        "layer_counts": dict(sorted(layer_counts.items())),
    }


FeatureRegistry.summary = _feature_summary


# ============================================================
# HEALTH CHECK
# ============================================================

def _feature_health(self) -> dict:

    dependency_errors = []

    for feature_id in self._features:

        try:
            self.validate_dependencies(feature_id)

        except FeatureDependencyError as exc:
            dependency_errors.append(
                {
                    "feature_id": feature_id,
                    "error": str(exc),
                }
            )

    cycles = self.detect_cycles()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": (
            not dependency_errors
            and not cycles
        ),
        "feature_count": len(self._features),
        "dependency_errors": dependency_errors,
        "cycles": cycles,
    }


FeatureRegistry.health = _feature_health
# ============================================================
# FEATURE REGISTRY — PART 3
# Bootstrap + Discovery + Query + Snapshot
# ============================================================

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Iterable


# ============================================================
# ADDITIONAL EXCEPTIONS
# ============================================================

class FeatureBootstrapError(FeatureRegistryError):
    """Raised when registry bootstrap fails."""


class FeatureSnapshotError(FeatureRegistryError):
    """Raised when feature snapshot creation/restoration fails."""


# ============================================================
# FIND FEATURES
# ============================================================

def _feature_find(
    self,
    *,
    domain: str | None = None,
    layer: str | None = None,
    status: str | None = None,
    tag: str | None = None,
) -> tuple[FeatureDefinition, ...]:

    results = []

    for feature in self._features.values():

        if domain is not None and feature.domain != domain:
            continue

        if layer is not None and feature.layer != layer:
            continue

        if status is not None and feature.status != status:
            continue

        if tag is not None and tag not in feature.tags:
            continue

        results.append(feature)

    return tuple(
        sorted(
            results,
            key=lambda item: item.feature_id,
        )
    )


FeatureRegistry.find = _feature_find


# ============================================================
# PREFIX SEARCH
# ============================================================

def _feature_find_by_prefix(
    self,
    prefix: str,
) -> tuple[FeatureDefinition, ...]:

    if not isinstance(prefix, str):
        raise InvalidFeatureDefinitionError(
            "Feature prefix must be a string."
        )

    prefix = prefix.strip().lower()

    return tuple(
        sorted(
            (
                feature
                for feature in self._features.values()
                if feature.feature_id.startswith(prefix)
            ),
            key=lambda item: item.feature_id,
        )
    )


FeatureRegistry.find_by_prefix = _feature_find_by_prefix


# ============================================================
# TAG SEARCH
# ============================================================

def _feature_find_by_tag(
    self,
    tag: str,
) -> tuple[FeatureDefinition, ...]:

    if not isinstance(tag, str):
        raise InvalidFeatureDefinitionError(
            "Feature tag must be a string."
        )

    tag = tag.strip().lower()

    return tuple(
        sorted(
            (
                feature
                for feature in self._features.values()
                if tag in feature.tags
            ),
            key=lambda item: item.feature_id,
        )
    )


FeatureRegistry.find_by_tag = _feature_find_by_tag


# ============================================================
# DOMAIN SEARCH
# ============================================================

def _feature_find_by_domain(
    self,
    domain: str,
) -> tuple[FeatureDefinition, ...]:

    return self.find(domain=domain)


FeatureRegistry.find_by_domain = _feature_find_by_domain


# ============================================================
# LAYER SEARCH
# ============================================================

def _feature_find_by_layer(
    self,
    layer: str,
) -> tuple[FeatureDefinition, ...]:

    return self.find(layer=layer)


FeatureRegistry.find_by_layer = _feature_find_by_layer


# ============================================================
# BOOTSTRAP VALIDATION
# ============================================================

def _feature_validate_bootstrap(
    self,
    definitions: Iterable[FeatureDefinition],
) -> bool:

    definitions = tuple(definitions)

    incoming_ids = set()

    for definition in definitions:

        self._validate_definition(definition)

        if definition.feature_id in incoming_ids:
            raise FeatureBootstrapError(
                f"Duplicate feature in bootstrap batch: "
                f"{definition.feature_id}"
            )

        incoming_ids.add(definition.feature_id)

    available_ids = (
        set(self._features.keys())
        | incoming_ids
    )

    missing = {}

    for definition in definitions:

        unresolved = [
            dependency
            for dependency in definition.dependencies
            if dependency not in available_ids
        ]

        if unresolved:
            missing[definition.feature_id] = unresolved

    if missing:
        raise FeatureBootstrapError(
            f"Bootstrap has unresolved dependencies: {missing}"
        )

    # Build temporary dependency graph so cycles inside
    # the incoming bootstrap batch are detected.
    graph = {
        feature_id: tuple(feature.dependencies)
        for feature_id, feature in self._features.items()
    }

    for definition in definitions:
        graph[definition.feature_id] = definition.dependencies

    cycles = []

    def dfs(
        node: str,
        path: list[str],
        active: set[str],
    ) -> None:

        if node in active:
            start = path.index(node)
            cycle = tuple(path[start:] + [node])

            if cycle not in cycles:
                cycles.append(cycle)

            return

        active.add(node)
        path.append(node)

        for dependency in graph.get(node, ()):

            if dependency in graph:
                dfs(
                    dependency,
                    path,
                    active,
                )

        path.pop()
        active.remove(node)

    for feature_id in graph:
        dfs(
            feature_id,
            [],
            set(),
        )

    if cycles:
        raise FeatureBootstrapError(
            "Bootstrap dependency cycle detected: "
            + "; ".join(
                " -> ".join(cycle)
                for cycle in cycles
            )
        )

    return True


FeatureRegistry.validate_bootstrap = _feature_validate_bootstrap


# ============================================================
# BOOTSTRAP
# ============================================================

def _feature_bootstrap(
    self,
    definitions: Iterable[FeatureDefinition],
) -> tuple[FeatureDefinition, ...]:

    definitions = tuple(definitions)

    self.validate_bootstrap(definitions)

    # Register in dependency-resolved order.
    pending = {
        definition.feature_id: definition
        for definition in definitions
    }

    registered = []

    while pending:

        progress = False

        for feature_id, definition in tuple(pending.items()):

            dependencies_ready = all(
                dependency in self._features
                for dependency in definition.dependencies
            )

            if not dependencies_ready:
                continue

            result = self.register_safe(definition)

            registered.append(result)

            del pending[feature_id]

            progress = True

        if not progress:

            unresolved = {
                feature_id: definition.dependencies
                for feature_id, definition in pending.items()
            }

            raise FeatureBootstrapError(
                "Unable to resolve bootstrap order: "
                f"{unresolved}"
            )

    return tuple(registered)


FeatureRegistry.bootstrap = _feature_bootstrap


# ============================================================
# SNAPSHOT
# ============================================================

def _feature_snapshot(self) -> dict:

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "features": [
            asdict(feature)
            for feature in self.list_all()
        ],
    }


FeatureRegistry.snapshot = _feature_snapshot


# ============================================================
# SNAPSHOT RESTORE
# ============================================================

def _feature_restore_snapshot(
    self,
    snapshot: dict,
    *,
    replace_existing: bool = False,
) -> tuple[FeatureDefinition, ...]:

    if not isinstance(snapshot, dict):
        raise FeatureSnapshotError(
            "Snapshot must be a dictionary."
        )

    raw_features = snapshot.get("features")

    if not isinstance(raw_features, list):
        raise FeatureSnapshotError(
            "Snapshot does not contain a valid 'features' list."
        )

    definitions = []

    for raw in raw_features:

        if not isinstance(raw, dict):
            raise FeatureSnapshotError(
                "Invalid feature entry in snapshot."
            )

        try:
            definition = FeatureDefinition(
                feature_id=raw["feature_id"],
                name=raw["name"],
                version=raw["version"],
                domain=raw["domain"],
                layer=raw["layer"],
                description=raw["description"],
                dependencies=tuple(
                    raw.get("dependencies", ())
                ),
                status=raw.get(
                    "status",
                    "registered",
                ),
                owner=raw.get(
                    "owner",
                    "",
                ),
                tags=tuple(
                    raw.get("tags", ())
                ),
                metadata=dict(
                    raw.get("metadata", {})
                ),
                registered_at=raw.get(
                    "registered_at"
                ),
            )

        except (KeyError, TypeError, ValueError) as exc:

            raise FeatureSnapshotError(
                f"Invalid feature snapshot entry: {raw}"
            ) from exc

        definitions.append(definition)

    if not replace_existing:
        for definition in definitions:

            if self.exists(definition.feature_id):
                raise FeatureSnapshotError(
                    f"Feature already exists: "
                    f"{definition.feature_id}"
                )

    if replace_existing:
        for definition in definitions:

            if self.exists(definition.feature_id):
                self.replace(definition)

            else:
                self.register(definition)

        return tuple(definitions)

    return self.bootstrap(definitions)


FeatureRegistry.restore_snapshot = _feature_restore_snapshot


# ============================================================
# EXPORT METADATA
# ============================================================

def _feature_export_metadata(self) -> list[dict]:

    return [
        asdict(feature)
        for feature in self.list_all()
    ]


FeatureRegistry.export_metadata = _feature_export_metadata


# ============================================================
# CONSISTENCY CHECK
# ============================================================

def _feature_consistency_check(self) -> dict:

    duplicate_ids = []

    ids = list(self._features.keys())

    seen = set()

    for feature_id in ids:

        if feature_id in seen:
            duplicate_ids.append(feature_id)

        seen.add(feature_id)

    invalid_dependencies = {}

    for feature in self._features.values():

        missing = [
            dependency
            for dependency in feature.dependencies
            if dependency not in self._features
        ]

        if missing:
            invalid_dependencies[
                feature.feature_id
            ] = missing

    cycles = self.detect_cycles()

    return {
        "healthy": (
            not duplicate_ids
            and not invalid_dependencies
            and not cycles
        ),
        "duplicate_ids": duplicate_ids,
        "invalid_dependencies": invalid_dependencies,
        "cycles": cycles,
        "feature_count": len(self._features),
    }


FeatureRegistry.consistency_check = _feature_consistency_check


# ============================================================
# REGISTRY STATE
# ============================================================

def _feature_state(self) -> dict:

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "feature_count": self.count(),
        "active_count": len(
            self.active_features()
        ),
        "healthy": self.health()["healthy"],
    }


FeatureRegistry.state = _feature_state
# ============================================================
# FEATURE REGISTRY — PART 4
# Declarative Specifications + Discovery + Canonical Catalog
# ============================================================

from dataclasses import dataclass
from typing import Any, Callable


# ============================================================
# FEATURE REGISTRATION SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class FeatureRegistrationSpec:
    """
    Declarative specification for a ROBOMLM feature.

    This object describes a feature only.
    It does not execute feature logic.
    """

    feature_id: str
    name: str
    version: str
    domain: str
    layer: str
    description: str = ""
    dependencies: tuple[str, ...] = ()
    status: str = "registered"
    owner: str = "ROBOMLM"
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] | None = None

    def to_definition(self) -> FeatureDefinition:
        return FeatureDefinition(
            feature_id=self.feature_id,
            name=self.name,
            version=self.version,
            domain=self.domain,
            layer=self.layer,
            description=self.description,
            dependencies=self.dependencies,
            status=self.status,
            owner=self.owner,
            tags=self.tags,
            metadata=dict(self.metadata or {}),
        )


# ============================================================
# SPEC VALIDATION
# ============================================================

def _validate_feature_spec(
    spec: FeatureRegistrationSpec,
) -> None:

    if not isinstance(
        spec,
        FeatureRegistrationSpec,
    ):
        raise InvalidFeatureDefinitionError(
            "Expected FeatureRegistrationSpec."
        )

    if not spec.feature_id.strip():
        raise InvalidFeatureDefinitionError(
            "Feature specification requires feature_id."
        )

    if not spec.name.strip():
        raise InvalidFeatureDefinitionError(
            f"Feature '{spec.feature_id}' requires name."
        )

    if not spec.version.strip():
        raise InvalidFeatureDefinitionError(
            f"Feature '{spec.feature_id}' requires version."
        )

    if not spec.domain.strip():
        raise InvalidFeatureDefinitionError(
            f"Feature '{spec.feature_id}' requires domain."
        )

    if not spec.layer.strip():
        raise InvalidFeatureDefinitionError(
            f"Feature '{spec.feature_id}' requires layer."
        )

    if spec.status not in VALID_FEATURE_STATUSES:
        raise InvalidFeatureDefinitionError(
            f"Invalid status '{spec.status}' "
            f"for feature '{spec.feature_id}'."
        )

    if spec.feature_id in spec.dependencies:
        raise FeatureDependencyError(
            f"Feature '{spec.feature_id}' "
            f"cannot depend on itself."
        )


# ============================================================
# REGISTRY SPEC REGISTRATION
# ============================================================

def _feature_register_spec(
    self,
    spec: FeatureRegistrationSpec,
) -> FeatureDefinition:

    _validate_feature_spec(spec)

    definition = spec.to_definition()

    return self.register_safe(definition)


FeatureRegistry.register_spec = _feature_register_spec


# ============================================================
# BATCH SPEC REGISTRATION
# ============================================================

def _feature_register_specs(
    self,
    specs: tuple[FeatureRegistrationSpec, ...] | list[
        FeatureRegistrationSpec
    ],
) -> tuple[FeatureDefinition, ...]:

    normalized_specs = tuple(specs)

    for spec in normalized_specs:
        _validate_feature_spec(spec)

    definitions = tuple(
        spec.to_definition()
        for spec in normalized_specs
    )

    return self.bootstrap(definitions)


FeatureRegistry.register_specs = _feature_register_specs


# ============================================================
# DECLARATIVE DISCOVERY STORE
# ============================================================

_FEATURE_REGISTRATION_SPECS: dict[
    str,
    FeatureRegistrationSpec,
] = {}


# ============================================================
# FEATURE DECORATOR
# ============================================================

def feature_spec(
    *,
    feature_id: str,
    name: str,
    version: str,
    domain: str,
    layer: str,
    description: str = "",
    dependencies: tuple[str, ...] = (),
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> Callable:

    spec = FeatureRegistrationSpec(
        feature_id=feature_id,
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

    _validate_feature_spec(spec)

    def decorator(
        target: Any,
    ) -> Any:

        _FEATURE_REGISTRATION_SPECS[
            feature_id
        ] = spec

        setattr(
            target,
            "__robomlm_feature_spec__",
            spec,
        )

        return target

    return decorator


# ============================================================
# DISCOVER REGISTERED SPECS
# ============================================================

def discover_feature_specs() -> tuple[
    FeatureRegistrationSpec,
    ...,
]:

    return tuple(
        sorted(
            _FEATURE_REGISTRATION_SPECS.values(),
            key=lambda spec: spec.feature_id,
        )
    )


# ============================================================
# GET DISCOVERED SPEC
# ============================================================

def get_feature_spec(
    feature_id: str,
) -> FeatureRegistrationSpec:

    feature_id = feature_id.strip().lower()

    try:
        return _FEATURE_REGISTRATION_SPECS[
            feature_id
        ]

    except KeyError as exc:
        raise FeatureNotFoundError(
            f"Feature specification not found: "
            f"{feature_id}"
        ) from exc


# ============================================================
# REGISTER DISCOVERED FEATURES
# ============================================================

def _feature_register_discovered(
    self,
) -> tuple[FeatureDefinition, ...]:

    specs = discover_feature_specs()

    if not specs:
        return ()

    return self.register_specs(specs)


FeatureRegistry.register_discovered = (
    _feature_register_discovered
)


# ============================================================
# DISCOVERY REPORT
# ============================================================

def _feature_discovery_report(self) -> dict:

    specs = discover_feature_specs()

    discovered_ids = {
        spec.feature_id
        for spec in specs
    }

    registered_ids = set(
        self._features.keys()
    )

    return {
        "discovered_count": len(
            discovered_ids
        ),
        "registered_count": len(
            registered_ids
        ),
        "discovered_features": tuple(
            sorted(discovered_ids)
        ),
        "not_registered": tuple(
            sorted(
                discovered_ids
                - registered_ids
            )
        ),
        "registered_without_discovery": tuple(
            sorted(
                registered_ids
                - discovered_ids
            )
        ),
    }


FeatureRegistry.discovery_report = (
    _feature_discovery_report
)


# ============================================================
# EXPORT DISCOVERED METADATA
# ============================================================

def export_discovered_feature_metadata() -> list[dict]:

    return [
        {
            "feature_id": spec.feature_id,
            "name": spec.name,
            "version": spec.version,
            "domain": spec.domain,
            "layer": spec.layer,
            "description": spec.description,
            "dependencies": list(
                spec.dependencies
            ),
            "status": spec.status,
            "owner": spec.owner,
            "tags": list(spec.tags),
            "metadata": dict(
                spec.metadata or {}
            ),
        }
        for spec in discover_feature_specs()
    ]


# ============================================================
# CANONICAL ROBOMLM FEATURE DOMAINS
# ============================================================

FEATURE_DOMAIN_CORE = "core"
FEATURE_DOMAIN_EVIDENCE = "evidence"
FEATURE_DOMAIN_CONTEXT = "context"
FEATURE_DOMAIN_DECISION = "decision"
FEATURE_DOMAIN_RISK = "risk"
FEATURE_DOMAIN_CAS = "cas"
FEATURE_DOMAIN_MEMORY = "memory"
FEATURE_DOMAIN_OPPORTUNITY = "opportunity"
FEATURE_DOMAIN_RESEARCH = "research"
FEATURE_DOMAIN_AUTOMATION = "automation"
FEATURE_DOMAIN_INTELLIGENCE = "intelligence"
FEATURE_DOMAIN_METRICS = "metrics"


# ============================================================
# CANONICAL ROBOMLM FEATURE LAYERS
# ============================================================

FEATURE_LAYER_FOUNDATION = "foundation"
FEATURE_LAYER_EVIDENCE = "evidence"
FEATURE_LAYER_CONTEXT = "context"
FEATURE_LAYER_DECISION = "decision"
FEATURE_LAYER_RISK = "risk"
FEATURE_LAYER_CONTROL = "control"
FEATURE_LAYER_MEMORY = "memory"
FEATURE_LAYER_OPPORTUNITY = "opportunity"
FEATURE_LAYER_RESEARCH = "research"
FEATURE_LAYER_AUTOMATION = "automation"
FEATURE_LAYER_METRICS = "metrics"
FEATURE_LAYER_ORCHESTRATION = "orchestration"


# ============================================================
# CANONICAL FEATURE SPEC BUILDER
# ============================================================

def _canonical_feature(
    feature_id: str,
    name: str,
    domain: str,
    layer: str,
    description: str,
    *,
    dependencies: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> FeatureRegistrationSpec:

    return FeatureRegistrationSpec(
        feature_id=feature_id,
        name=name,
        version="1.0.0",
        domain=domain,
        layer=layer,
        description=description,
        dependencies=dependencies,
        status="registered",
        owner="ROBOMLM",
        tags=tags,
        metadata=metadata or {},
    )


# ============================================================
# CANONICAL ROBOMLM FEATURE CATALOG
# ============================================================
#
# NOTE:
# These are feature-level declarations only.
# They do NOT contain formulas, trading rules,
# signals, or decision authority.
#
# Exact implementation formulas remain inside
# their respective intelligence/engine modules.
# ============================================================

ROBOMLM_CANONICAL_FEATURE_SPECS = (

    # --------------------------------------------------------
    # CORE / PLATFORM
    # --------------------------------------------------------

    _canonical_feature(
        "market_data_ingestion",
        "Market Data Ingestion",
        FEATURE_DOMAIN_CORE,
        FEATURE_LAYER_FOUNDATION,
        "Feature representing normalized market-data ingestion.",
        tags=("data", "market", "foundation"),
    ),

    _canonical_feature(
        "market_universe",
        "Market Universe",
        FEATURE_DOMAIN_CORE,
        FEATURE_LAYER_FOUNDATION,
        "Feature representing connected instruments and venues.",
        dependencies=("market_data_ingestion",),
        tags=("universe", "instrument", "venue"),
    ),

    _canonical_feature(
        "market_session",
        "Market Session Awareness",
        FEATURE_DOMAIN_CORE,
        FEATURE_LAYER_FOUNDATION,
        "Feature representing market-session state awareness.",
        dependencies=("market_data_ingestion",),
        tags=("session", "timing"),
    ),

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    _canonical_feature(
        "evidence_processing",
        "Evidence Processing",
        FEATURE_DOMAIN_EVIDENCE,
        FEATURE_LAYER_EVIDENCE,
        "Feature representing the Evidence Cortex processing stage.",
        dependencies=("market_data_ingestion",),
        tags=("evidence", "cortex"),
    ),

    _canonical_feature(
        "evidence_conflict_resolution",
        "Evidence Conflict Resolution",
        FEATURE_DOMAIN_EVIDENCE,
        FEATURE_LAYER_EVIDENCE,
        "Feature representing conflicting-evidence handling.",
        dependencies=("evidence_processing",),
        tags=("evidence", "conflict"),
    ),

    _canonical_feature(
        "evidence_confidence",
        "Evidence Confidence",
        FEATURE_DOMAIN_EVIDENCE,
        FEATURE_LAYER_EVIDENCE,
        "Feature representing confidence assessment of evidence.",
        dependencies=(
            "evidence_processing",
            "evidence_conflict_resolution",
        ),
        tags=("evidence", "confidence"),
    ),

    _canonical_feature(
        "evidence_package",
        "Evidence Package",
        FEATURE_DOMAIN_EVIDENCE,
        FEATURE_LAYER_EVIDENCE,
        "Feature representing the structured evidence package.",
        dependencies=("evidence_confidence",),
        tags=("evidence", "package"),
    ),

    # --------------------------------------------------------
    # MARKET CONTEXT
    # --------------------------------------------------------

    _canonical_feature(
        "market_context",
        "Market Context",
        FEATURE_DOMAIN_CONTEXT,
        FEATURE_LAYER_CONTEXT,
        "Feature representing consolidated market context.",
        dependencies=("evidence_package",),
        tags=("context", "market"),
    ),

    _canonical_feature(
        "market_regime",
        "Market Regime",
        FEATURE_DOMAIN_CONTEXT,
        FEATURE_LAYER_CONTEXT,
        "Feature representing market-regime classification.",
        dependencies=("market_context",),
        tags=("regime", "context"),
    ),

    _canonical_feature(
        "market_relationships",
        "Market Relationships",
        FEATURE_DOMAIN_CONTEXT,
        FEATURE_LAYER_CONTEXT,
        "Feature representing cross-market and internal relationships.",
        dependencies=("market_context",),
        tags=("relationship", "context"),
    ),

    # --------------------------------------------------------
    # OPPORTUNITY
    # --------------------------------------------------------

    _canonical_feature(
        "opportunity_detection",
        "Opportunity Detection",
        FEATURE_DOMAIN_OPPORTUNITY,
        FEATURE_LAYER_OPPORTUNITY,
        "Feature representing opportunity identification.",
        dependencies=(
            "market_context",
            "market_regime",
        ),
        tags=("opportunity", "discovery"),
    ),

    _canonical_feature(
        "opportunity_ranking",
        "Opportunity Ranking",
        FEATURE_DOMAIN_OPPORTUNITY,
        FEATURE_LAYER_OPPORTUNITY,
        "Feature representing comparative opportunity ranking.",
        dependencies=("opportunity_detection",),
        tags=("opportunity", "ranking"),
    ),

    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    _canonical_feature(
        "decision_readiness",
        "Decision Readiness",
        FEATURE_DOMAIN_DECISION,
        FEATURE_LAYER_DECISION,
        "Feature representing readiness assessment before decision formation.",
        dependencies=("evidence_package",),
        tags=("decision", "readiness"),
    ),

    _canonical_feature(
        "decision_formation",
        "Decision Formation",
        FEATURE_DOMAIN_DECISION,
        FEATURE_LAYER_DECISION,
        "Feature representing structured decision formation.",
        dependencies=(
            "decision_readiness",
            "market_context",
            "opportunity_ranking",
        ),
        tags=("decision", "formation"),
    ),

    _canonical_feature(
        "decision_validation",
        "Decision Validation",
        FEATURE_DOMAIN_DECISION,
        FEATURE_LAYER_DECISION,
        "Feature representing validation of a formed decision.",
        dependencies=("decision_formation",),
        tags=("decision", "validation"),
    ),

    _canonical_feature(
        "decision_intelligence",
        "Decision Intelligence",
        FEATURE_DOMAIN_DECISION,
        FEATURE_LAYER_DECISION,
        "Feature representing the final structured decision-intelligence output.",
        dependencies=("decision_validation",),
        tags=("decision", "intelligence"),
    ),

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    _canonical_feature(
        "risk_assessment",
        "Risk Assessment",
        FEATURE_DOMAIN_RISK,
        FEATURE_LAYER_RISK,
        "Feature representing risk assessment before action.",
        dependencies=("decision_intelligence",),
        tags=("risk", "assessment"),
    ),

    _canonical_feature(
        "exposure_control",
        "Exposure Control",
        FEATURE_DOMAIN_RISK,
        FEATURE_LAYER_RISK,
        "Feature representing exposure-level risk control.",
        dependencies=("risk_assessment",),
        tags=("risk", "exposure"),
    ),

    # --------------------------------------------------------
    # CAS
    # --------------------------------------------------------

    _canonical_feature(
        "cas_governance",
        "CAS Governance",
        FEATURE_DOMAIN_CAS,
        FEATURE_LAYER_CONTROL,
        "Feature representing Controlled Action System governance.",
        dependencies=(
            "decision_intelligence",
            "risk_assessment",
        ),
        tags=("cas", "control", "governance"),
    ),

    _canonical_feature(
        "execution_safety",
        "Execution Safety",
        FEATURE_DOMAIN_CAS,
        FEATURE_LAYER_CONTROL,
        "Feature representing execution-safety gating.",
        dependencies=("cas_governance",),
        tags=("cas", "execution", "safety"),
    ),

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    _canonical_feature(
        "market_memory",
        "Market Memory",
        FEATURE_DOMAIN_MEMORY,
        FEATURE_LAYER_MEMORY,
        "Feature representing persistent market-memory capability.",
        dependencies=("market_data_ingestion",),
        tags=("memory", "market"),
    ),

    _canonical_feature(
        "evidence_memory",
        "Evidence Memory",
        FEATURE_DOMAIN_MEMORY,
        FEATURE_LAYER_MEMORY,
        "Feature representing historical evidence memory.",
        dependencies=(
            "evidence_package",
            "market_memory",
        ),
        tags=("memory", "evidence"),
    ),

    _canonical_feature(
        "decision_memory",
        "Decision Memory",
        FEATURE_DOMAIN_MEMORY,
        FEATURE_LAYER_MEMORY,
        "Feature representing historical decision memory.",
        dependencies=(
            "decision_intelligence",
            "market_memory",
        ),
        tags=("memory", "decision"),
    ),

    _canonical_feature(
        "outcome_memory",
        "Outcome Memory",
        FEATURE_DOMAIN_MEMORY,
        FEATURE_LAYER_MEMORY,
        "Feature representing outcome and result memory.",
        dependencies=("decision_memory",),
        tags=("memory", "outcome"),
    ),

    # --------------------------------------------------------
    # RESEARCH
    # --------------------------------------------------------

    _canonical_feature(
        "research_validation",
        "Research Validation",
        FEATURE_DOMAIN_RESEARCH,
        FEATURE_LAYER_RESEARCH,
        "Feature representing research validation capability.",
        dependencies=("outcome_memory",),
        tags=("research", "validation"),
    ),

    _canonical_feature(
        "learning_feedback",
        "Learning Feedback",
        FEATURE_DOMAIN_RESEARCH,
        FEATURE_LAYER_RESEARCH,
        "Feature representing validated learning feedback.",
        dependencies=(
            "research_validation",
            "outcome_memory",
        ),
        tags=("research", "learning"),
    ),

    # --------------------------------------------------------
    # AUTOMATION
    # --------------------------------------------------------

    _canonical_feature(
        "automation_gate",
        "Automation Gate",
        FEATURE_DOMAIN_AUTOMATION,
        FEATURE_LAYER_AUTOMATION,
        "Feature representing controlled automation eligibility.",
        dependencies=(
            "execution_safety",
            "risk_assessment",
        ),
        tags=("automation", "gate"),
    ),
)


# ============================================================
# CANONICAL CATALOG VALIDATION
# ============================================================

def validate_canonical_feature_catalog() -> bool:

    ids = set()

    for spec in ROBOMLM_CANONICAL_FEATURE_SPECS:

        _validate_feature_spec(spec)

        if spec.feature_id in ids:
            raise FeatureRegistryError(
                f"Duplicate canonical feature ID: "
                f"{spec.feature_id}"
            )

        ids.add(spec.feature_id)

    known_ids = ids

    for spec in ROBOMLM_CANONICAL_FEATURE_SPECS:

        missing = [
            dependency
            for dependency in spec.dependencies
            if dependency not in known_ids
            and dependency not in feature_registry._features
        ]

        if missing:
            raise FeatureDependencyError(
                f"Canonical feature '{spec.feature_id}' "
                f"has unresolved dependencies: "
                f"{missing}"
            )

    return True


# ============================================================
# CANONICAL FEATURE REGISTRATION
# ============================================================

def register_canonical_features() -> tuple[
    FeatureDefinition,
    ...,
]:

    validate_canonical_feature_catalog()

    return feature_registry.register_specs(
        ROBOMLM_CANONICAL_FEATURE_SPECS
    )


# ============================================================
# CANONICAL FEATURE IDS
# ============================================================

def canonical_feature_ids() -> tuple[str, ...]:

    return tuple(
        spec.feature_id
        for spec in ROBOMLM_CANONICAL_FEATURE_SPECS
    )


# ============================================================
# CANONICAL FEATURE LOOKUP
# ============================================================

def canonical_feature_spec(
    feature_id: str,
) -> FeatureRegistrationSpec:

    feature_id = feature_id.strip().lower()

    for spec in ROBOMLM_CANONICAL_FEATURE_SPECS:

        if spec.feature_id == feature_id:
            return spec

    raise FeatureNotFoundError(
        f"Canonical feature not found: "
        f"{feature_id}"
    )


# ============================================================
# DOMAIN REPORT
# ============================================================

def canonical_feature_domain_report() -> dict:

    report = {}

    for spec in ROBOMLM_CANONICAL_FEATURE_SPECS:

        report.setdefault(
            spec.domain,
            [],
        ).append(
            spec.feature_id
        )

    return {
        domain: tuple(
            sorted(feature_ids)
        )
        for domain, feature_ids in sorted(
            report.items()
        )
    }


# ============================================================
# DEPENDENCY REPORT
# ============================================================

def canonical_feature_dependency_report() -> dict:

    return {
        spec.feature_id: tuple(
            spec.dependencies
        )
        for spec in ROBOMLM_CANONICAL_FEATURE_SPECS
    }


# ============================================================
# INSTALL CANONICAL FEATURE REGISTRY
# ============================================================

def install_robomlm_feature_registry() -> dict:

    validate_canonical_feature_catalog()

    registered = register_canonical_features()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "canonical_count": len(
            ROBOMLM_CANONICAL_FEATURE_SPECS
        ),
        "registered_count": len(
            registered
        ),
        "feature_ids": canonical_feature_ids(),
        "health": feature_registry.health(),
    }
# ============================================================
# FEATURE REGISTRY — PART 5
# Runtime Control + Atomic Install + Audit + Freeze
# ============================================================

from copy import deepcopy


# ============================================================
# ADDITIONAL EXCEPTIONS
# ============================================================

class FeatureRegistryFrozenError(FeatureRegistryError):
    """Raised when a mutation is attempted on a frozen registry."""


class FeatureAuditError(FeatureRegistryError):
    """Raised when the final feature registry audit fails."""


class FeatureAtomicInstallError(FeatureRegistryError):
    """Raised when atomic feature installation fails."""


# ============================================================
# INTERNAL FREEZE STATE
# ============================================================

FeatureRegistry._frozen = False


# ============================================================
# FREEZE / UNFREEZE
# ============================================================

def _feature_is_frozen(self) -> bool:
    return bool(
        getattr(self, "_frozen", False)
    )


def _feature_freeze(self) -> None:
    self._frozen = True


def _feature_unfreeze(self) -> None:
    self._frozen = False


FeatureRegistry.is_frozen = _feature_is_frozen
FeatureRegistry.freeze = _feature_freeze
FeatureRegistry.unfreeze = _feature_unfreeze


# ============================================================
# MUTATION GUARD
# ============================================================

def _feature_assert_mutable(self) -> None:

    if self.is_frozen():
        raise FeatureRegistryFrozenError(
            "Feature registry is frozen. "
            "Unfreeze it before performing a mutation."
        )


FeatureRegistry.assert_mutable = _feature_assert_mutable


# ============================================================
# ORIGINAL MUTATION METHODS
# ============================================================

_feature_original_register = FeatureRegistry.register
_feature_original_replace = FeatureRegistry.replace
_feature_original_unregister = FeatureRegistry.unregister
_feature_original_clear = FeatureRegistry.clear


# ============================================================
# GUARDED REGISTER
# ============================================================

def _feature_guarded_register(
    self,
    definition: FeatureDefinition,
) -> FeatureDefinition:

    self.assert_mutable()

    return _feature_original_register(
        self,
        definition,
    )


FeatureRegistry.register = _feature_guarded_register


# ============================================================
# GUARDED REPLACE
# ============================================================

def _feature_guarded_replace(
    self,
    definition: FeatureDefinition,
) -> FeatureDefinition:

    self.assert_mutable()

    return _feature_original_replace(
        self,
        definition,
    )


FeatureRegistry.replace = _feature_guarded_replace


# ============================================================
# GUARDED UNREGISTER
# ============================================================

def _feature_guarded_unregister(
    self,
    feature_id: str,
    force: bool = False,
) -> FeatureDefinition:

    self.assert_mutable()

    return _feature_original_unregister(
        self,
        feature_id,
        force=force,
    )


FeatureRegistry.unregister = _feature_guarded_unregister


# ============================================================
# GUARDED CLEAR
# ============================================================

def _feature_guarded_clear(
    self,
    force: bool = False,
) -> None:

    self.assert_mutable()

    return _feature_original_clear(
        self,
        force=force,
    )


FeatureRegistry.clear = _feature_guarded_clear


# ============================================================
# GUARDED STATUS CHANGE
# ============================================================

_feature_original_set_status = FeatureRegistry.set_status


def _feature_guarded_set_status(
    self,
    feature_id: str,
    status: str,
) -> FeatureDefinition:

    self.assert_mutable()

    return _feature_original_set_status(
        self,
        feature_id,
        status,
    )


FeatureRegistry.set_status = _feature_guarded_set_status


# ============================================================
# REGISTRY CLONE
# ============================================================

def _feature_clone(self) -> "FeatureRegistry":

    clone = FeatureRegistry()

    clone._features = deepcopy(
        self._features
    )

    clone._frozen = self._frozen

    return clone


FeatureRegistry.clone = _feature_clone


# ============================================================
# ATOMIC REGISTRATION
# ============================================================

def _feature_atomic_register(
    self,
    definitions: Iterable[FeatureDefinition],
) -> tuple[FeatureDefinition, ...]:

    self.assert_mutable()

    definitions = tuple(definitions)

    backup = deepcopy(
        self._features
    )

    try:

        result = self.bootstrap(
            definitions
        )

        self.assert_no_cycles()

        self.validate_all_dependencies()

        return result

    except Exception as exc:

        self._features = backup

        raise FeatureAtomicInstallError(
            "Atomic feature registration failed. "
            "Registry state was rolled back."
        ) from exc


FeatureRegistry.atomic_register = _feature_atomic_register


# ============================================================
# ATOMIC SPEC REGISTRATION
# ============================================================

def _feature_atomic_register_specs(
    self,
    specs: Iterable[FeatureRegistrationSpec],
) -> tuple[FeatureDefinition, ...]:

    specs = tuple(specs)

    definitions = tuple(
        spec.to_definition()
        for spec in specs
    )

    return self.atomic_register(
        definitions
    )


FeatureRegistry.atomic_register_specs = (
    _feature_atomic_register_specs
)


# ============================================================
# FINAL DEPENDENCY AUDIT
# ============================================================

def _feature_dependency_audit(self) -> dict:

    missing = {}

    for feature in self._features.values():

        unresolved = [
            dependency
            for dependency in feature.dependencies
            if dependency not in self._features
        ]

        if unresolved:
            missing[
                feature.feature_id
            ] = tuple(unresolved)

    cycles = self.detect_cycles()

    self_dependencies = []

    for feature in self._features.values():

        if feature.feature_id in feature.dependencies:
            self_dependencies.append(
                feature.feature_id
            )

    return {
        "healthy": (
            not missing
            and not cycles
            and not self_dependencies
        ),
        "missing_dependencies": missing,
        "cycles": cycles,
        "self_dependencies": tuple(
            sorted(self_dependencies)
        ),
    }


FeatureRegistry.dependency_audit = (
    _feature_dependency_audit
)


# ============================================================
# STATUS AUDIT
# ============================================================

def _feature_status_audit(self) -> dict:

    invalid_statuses = {}

    for feature in self._features.values():

        if feature.status not in VALID_FEATURE_STATUSES:

            invalid_statuses[
                feature.feature_id
            ] = feature.status

    return {
        "healthy": not invalid_statuses,
        "invalid_statuses": invalid_statuses,
    }


FeatureRegistry.status_audit = (
    _feature_status_audit
)


# ============================================================
# DEFINITION AUDIT
# ============================================================

def _feature_definition_audit(self) -> dict:

    invalid_features = {}

    for feature_id, feature in self._features.items():

        try:
            self._validate_definition(
                feature
            )

        except Exception as exc:

            invalid_features[
                feature_id
            ] = str(exc)

    return {
        "healthy": not invalid_features,
        "invalid_features": invalid_features,
    }


FeatureRegistry.definition_audit = (
    _feature_definition_audit
)


# ============================================================
# CANONICAL CATALOG AUDIT
# ============================================================

def audit_canonical_features() -> dict:

    catalog_ids = {
        spec.feature_id
        for spec in ROBOMLM_CANONICAL_FEATURE_SPECS
    }

    registry_ids = set(
        feature_registry.feature_ids()
    )

    missing_from_registry = (
        catalog_ids - registry_ids
    )

    extra_in_registry = (
        registry_ids - catalog_ids
    )

    return {
        "healthy": (
            not missing_from_registry
            and not extra_in_registry
        ),
        "catalog_count": len(
            catalog_ids
        ),
        "registry_count": len(
            registry_ids
        ),
        "missing_from_registry": tuple(
            sorted(missing_from_registry)
        ),
        "extra_in_registry": tuple(
            sorted(extra_in_registry)
        ),
    }


# ============================================================
# COMPLETE REGISTRY AUDIT
# ============================================================

def _feature_full_audit(self) -> dict:

    definition_audit = (
        self.definition_audit()
    )

    dependency_audit = (
        self.dependency_audit()
    )

    status_audit = (
        self.status_audit()
    )

    consistency = (
        self.consistency_check()
    )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "feature_count": self.count(),
        "frozen": self.is_frozen(),

        "definition": definition_audit,
        "dependency": dependency_audit,
        "status": status_audit,
        "consistency": consistency,

        "healthy": (
            definition_audit["healthy"]
            and dependency_audit["healthy"]
            and status_audit["healthy"]
            and consistency["healthy"]
        ),
    }


FeatureRegistry.full_audit = _feature_full_audit


# ============================================================
# ASSERT HEALTHY
# ============================================================

def _feature_assert_healthy(self) -> bool:

    audit = self.full_audit()

    if not audit["healthy"]:
        raise FeatureAuditError(
            f"Feature registry audit failed: {audit}"
        )

    return True


FeatureRegistry.assert_healthy = (
    _feature_assert_healthy
)


# ============================================================
# FREEZE AFTER VALIDATION
# ============================================================

def _feature_freeze_if_healthy(self) -> dict:

    self.assert_healthy()

    self.freeze()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "frozen": True,
        "feature_count": self.count(),
        "healthy": True,
    }


FeatureRegistry.freeze_if_healthy = (
    _feature_freeze_if_healthy
)


# ============================================================
# FINAL REGISTRY EXPORT
# ============================================================

def _feature_final_export(self) -> dict:

    audit = self.full_audit()

    return {
        "registry": {
            "name": REGISTRY_NAME,
            "version": REGISTRY_VERSION,
            "frozen": self.is_frozen(),
        },
        "summary": self.summary(),
        "audit": audit,
        "features": self.export_metadata(),
    }


FeatureRegistry.final_export = (
    _feature_final_export
)


# ============================================================
# FEATURE REGISTRY INSTALLER
# ============================================================

def install_feature_registry(
    *,
    freeze_after_install: bool = False,
) -> dict:

    validate_canonical_feature_catalog()

    # Avoid duplicate registration if already installed.
    if feature_registry.count() == 0:

        feature_registry.atomic_register_specs(
            ROBOMLM_CANONICAL_FEATURE_SPECS
        )

    else:

        catalog_ids = set(
            canonical_feature_ids()
        )

        registered_ids = set(
            feature_registry.feature_ids()
        )

        missing = catalog_ids - registered_ids

        if missing:

            specs = tuple(
                spec
                for spec in ROBOMLM_CANONICAL_FEATURE_SPECS
                if spec.feature_id in missing
            )

            feature_registry.atomic_register_specs(
                specs
            )

    feature_registry.assert_healthy()

    if freeze_after_install:
        feature_registry.freeze()

    return feature_registry.final_export()


# ============================================================
# REGISTRY RESET — DEVELOPMENT / TEST ONLY
# ============================================================

def reset_feature_registry_for_testing() -> None:

    if feature_registry.is_frozen():
        feature_registry.unfreeze()

    feature_registry.clear(
        force=True
    )