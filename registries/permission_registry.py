# ============================================================
# ROBOMLM PERMISSION REGISTRY — PART 1
# Foundation + Definition + Basic Registration
# ============================================================

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional, Tuple


# ============================================================
# REGISTRY METADATA
# ============================================================

REGISTRY_NAME = "permission_registry"
REGISTRY_VERSION = "1.0.0"

VALID_PERMISSION_STATUSES = {
    "registered",
    "active",
    "disabled",
    "deprecated",
}


# ============================================================
# EXCEPTIONS
# ============================================================

class PermissionRegistryError(Exception):
    """Base exception for permission registry errors."""


class PermissionAlreadyRegisteredError(
    PermissionRegistryError
):
    """Raised when a permission already exists."""


class PermissionNotFoundError(
    PermissionRegistryError
):
    """Raised when a requested permission does not exist."""


class InvalidPermissionDefinitionError(
    PermissionRegistryError
):
    """Raised when a permission definition is invalid."""


class PermissionStateError(
    PermissionRegistryError
):
    """Raised when a permission state transition is invalid."""


# ============================================================
# PERMISSION DEFINITION
# ============================================================

@dataclass(frozen=True)
class PermissionDefinition:
    """
    Immutable metadata definition of a ROBOMLM permission.

    The registry describes permissions only.
    It does not perform authorization decisions.
    """

    permission_id: str
    name: str
    version: str

    domain: str
    resource: str
    action: str

    description: str = ""

    status: str = "registered"

    owner: str = "ROBOMLM"

    tags: Tuple[str, ...] = ()

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    registered_at: str = field(
        default_factory=lambda:
        datetime.now(
            timezone.utc
        ).isoformat()
    )


# ============================================================
# PERMISSION REGISTRY
# ============================================================

class PermissionRegistry:
    """
    Central registry for ROBOMLM permission metadata.

    Responsibilities:

    - permission identity
    - permission metadata
    - resource/action declaration
    - permission lifecycle state
    - basic lookup
    - basic filtering

    Non-responsibilities:

    - authentication
    - user authorization
    - policy evaluation
    - CAS decisions
    - risk decisions
    - execution decisions
    """

    def __init__(self) -> None:

        self._permissions: Dict[
            str,
            PermissionDefinition,
        ] = {}


    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        definition: PermissionDefinition,
    ) -> PermissionDefinition:

        self._validate_definition(
            definition
        )

        permission_id = (
            definition.permission_id
        )

        if permission_id in self._permissions:

            raise PermissionAlreadyRegisteredError(
                f"Permission already registered: "
                f"{permission_id}"
            )

        self._permissions[
            permission_id
        ] = definition

        return definition


    # ========================================================
    # REGISTER MANY
    # ========================================================

    def register_many(
        self,
        definitions: Iterable[
            PermissionDefinition
        ],
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        registered = []

        for definition in definitions:

            registered.append(
                self.register(
                    definition
                )
            )

        return tuple(registered)


    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        permission_id: str,
    ) -> PermissionDefinition:

        permission_id = (
            self._normalize_permission_id(
                permission_id
            )
        )

        try:
            return self._permissions[
                permission_id
            ]

        except KeyError as exc:

            raise PermissionNotFoundError(
                f"Permission not found: "
                f"{permission_id}"
            ) from exc


    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        permission_id: str,
    ) -> bool:

        permission_id = (
            self._normalize_permission_id(
                permission_id
            )
        )

        return permission_id in self._permissions


    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:

        return len(
            self._permissions
        )


    # ========================================================
    # LIST ALL
    # ========================================================

    def list_all(
        self,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        return tuple(
            sorted(
                self._permissions.values(),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # LIST BY DOMAIN
    # ========================================================

    def list_by_domain(
        self,
        domain: str,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        domain = self._normalize_text(
            domain,
            "domain",
        )

        return tuple(
            sorted(
                (
                    permission
                    for permission
                    in self._permissions.values()
                    if permission.domain
                    == domain
                ),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # LIST BY RESOURCE
    # ========================================================

    def list_by_resource(
        self,
        resource: str,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        resource = self._normalize_text(
            resource,
            "resource",
        )

        return tuple(
            sorted(
                (
                    permission
                    for permission
                    in self._permissions.values()
                    if permission.resource
                    == resource
                ),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # LIST BY ACTION
    # ========================================================

    def list_by_action(
        self,
        action: str,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        action = self._normalize_text(
            action,
            "action",
        )

        return tuple(
            sorted(
                (
                    permission
                    for permission
                    in self._permissions.values()
                    if permission.action
                    == action
                ),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # LIST BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        if status not in VALID_PERMISSION_STATUSES:

            raise PermissionStateError(
                f"Invalid permission status: "
                f"{status}"
            )

        return tuple(
            sorted(
                (
                    permission
                    for permission
                    in self._permissions.values()
                    if permission.status
                    == status
                ),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # LIST BY TAG
    # ========================================================

    def list_by_tag(
        self,
        tag: str,
    ) -> Tuple[
        PermissionDefinition,
        ...,
    ]:

        tag = self._normalize_text(
            tag,
            "tag",
        )

        return tuple(
            sorted(
                (
                    permission
                    for permission
                    in self._permissions.values()
                    if tag in permission.tags
                ),
                key=lambda item:
                item.permission_id,
            )
        )


    # ========================================================
    # VALIDATE DEFINITION
    # ========================================================

    def _validate_definition(
        self,
        definition: PermissionDefinition,
    ) -> None:

        if not isinstance(
            definition,
            PermissionDefinition,
        ):
            raise InvalidPermissionDefinitionError(
                "Expected PermissionDefinition."
            )

        self._normalize_permission_id(
            definition.permission_id
        )

        self._normalize_text(
            definition.name,
            "name",
        )

        self._normalize_text(
            definition.version,
            "version",
        )

        self._normalize_text(
            definition.domain,
            "domain",
        )

        self._normalize_text(
            definition.resource,
            "resource",
        )

        self._normalize_text(
            definition.action,
            "action",
        )

        if definition.status not in (
            VALID_PERMISSION_STATUSES
        ):

            raise InvalidPermissionDefinitionError(
                f"Invalid permission status: "
                f"{definition.status}"
            )

        if not isinstance(
            definition.tags,
            tuple,
        ):

            raise InvalidPermissionDefinitionError(
                "Permission tags must be a tuple."
            )

        if not isinstance(
            definition.metadata,
            dict,
        ):

            raise InvalidPermissionDefinitionError(
                "Permission metadata must be a dictionary."
            )


    # ========================================================
    # NORMALIZE PERMISSION ID
    # ========================================================

    @staticmethod
    def _normalize_permission_id(
        permission_id: str,
    ) -> str:

        if not isinstance(
            permission_id,
            str,
        ):

            raise InvalidPermissionDefinitionError(
                "Permission ID must be a string."
            )

        permission_id = (
            permission_id
            .strip()
            .lower()
        )

        if not permission_id:

            raise InvalidPermissionDefinitionError(
                "Permission ID cannot be empty."
            )

        return permission_id


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def _normalize_text(
        value: str,
        field_name: str,
    ) -> str:

        if not isinstance(
            value,
            str,
        ):

            raise InvalidPermissionDefinitionError(
                f"{field_name} must be a string."
            )

        value = value.strip()

        if not value:

            raise InvalidPermissionDefinitionError(
                f"{field_name} cannot be empty."
            )

        return value


# ============================================================
# GLOBAL REGISTRY INSTANCE
# ============================================================

permission_registry = PermissionRegistry()


# ============================================================
# CONVENIENCE REGISTRATION FUNCTION
# ============================================================

def register_permission(
    *,
    permission_id: str,
    name: str,
    version: str,
    domain: str,
    resource: str,
    action: str,
    description: str = "",
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: Tuple[str, ...] = (),
    metadata: Optional[
        Dict[str, Any]
    ] = None,
) -> PermissionDefinition:

    definition = PermissionDefinition(
        permission_id=permission_id,
        name=name,
        version=version,
        domain=domain,
        resource=resource,
        action=action,
        description=description,
        status=status,
        owner=owner,
        tags=tags,
        metadata=dict(
            metadata or {}
        ),
    )

    return permission_registry.register(
        definition
    )
# ============================================================
# ROBOMLM PERMISSION REGISTRY — PART 2
# Lifecycle + Conflict + Safe Registration + Relationships
# ============================================================


# ============================================================
# ADDITIONAL EXCEPTIONS
# ============================================================

class PermissionRegistrationConflictError(
    PermissionRegistryError
):
    """Raised when permission registration conflicts."""


class PermissionUnregisterError(
    PermissionRegistryError
):
    """Raised when permission removal is not allowed."""


class PermissionDependencyError(
    PermissionRegistryError
):
    """Raised when permission relationships are invalid."""


# ============================================================
# LIFECYCLE MANAGEMENT
# ============================================================

def _permission_set_status(
    self,
    permission_id: str,
    status: str,
) -> PermissionDefinition:

    permission_id = (
        self._normalize_permission_id(
            permission_id
        )
    )

    if status not in VALID_PERMISSION_STATUSES:
        raise PermissionStateError(
            f"Invalid permission status: {status}"
        )

    permission = self.get(permission_id)

    updated = PermissionDefinition(
        permission_id=permission.permission_id,
        name=permission.name,
        version=permission.version,
        domain=permission.domain,
        resource=permission.resource,
        action=permission.action,
        description=permission.description,
        status=status,
        owner=permission.owner,
        tags=permission.tags,
        metadata=dict(permission.metadata),
        registered_at=permission.registered_at,
    )

    self._permissions[
        permission_id
    ] = updated

    return updated


def _permission_activate(
    self,
    permission_id: str,
) -> PermissionDefinition:

    return self.set_status(
        permission_id,
        "active",
    )


def _permission_disable(
    self,
    permission_id: str,
) -> PermissionDefinition:

    return self.set_status(
        permission_id,
        "disabled",
    )


def _permission_deprecate(
    self,
    permission_id: str,
) -> PermissionDefinition:

    return self.set_status(
        permission_id,
        "deprecated",
    )


PermissionRegistry.set_status = (
    _permission_set_status
)

PermissionRegistry.activate = (
    _permission_activate
)

PermissionRegistry.disable = (
    _permission_disable
)

PermissionRegistry.deprecate = (
    _permission_deprecate
)


# ============================================================
# RESOURCE + ACTION KEY
# ============================================================

def _permission_resource_action_key(
    permission: PermissionDefinition,
) -> str:

    return (
        f"{permission.resource}:"
        f"{permission.action}"
    )


PermissionRegistry.resource_action_key = (
    _permission_resource_action_key
)


# ============================================================
# FIND BY RESOURCE + ACTION
# ============================================================

def _permission_find_by_resource_action(
    self,
    resource: str,
    action: str,
) -> Tuple[
    PermissionDefinition,
    ...,
]:

    resource = self._normalize_text(
        resource,
        "resource",
    )

    action = self._normalize_text(
        action,
        "action",
    )

    return tuple(
        sorted(
            (
                permission
                for permission
                in self._permissions.values()
                if permission.resource == resource
                and permission.action == action
            ),
            key=lambda item:
            item.permission_id,
        )
    )


PermissionRegistry.find_by_resource_action = (
    _permission_find_by_resource_action
)


# ============================================================
# CONFLICT CHECK
# ============================================================

def _permission_check_conflict(
    self,
    definition: PermissionDefinition,
) -> bool:

    self._validate_definition(
        definition
    )

    existing = self._permissions.get(
        definition.permission_id
    )

    if existing is None:
        return False

    return existing != definition


PermissionRegistry.check_conflict = (
    _permission_check_conflict
)


# ============================================================
# SAFE REGISTRATION
# ============================================================

def _permission_register_safe(
    self,
    definition: PermissionDefinition,
) -> PermissionDefinition:

    self._validate_definition(
        definition
    )

    existing = self._permissions.get(
        definition.permission_id
    )

    # New permission.
    if existing is None:
        return self.register(
            definition
        )

    # Exact same definition is idempotent.
    if existing == definition:
        return existing

    raise PermissionRegistrationConflictError(
        f"Permission '{definition.permission_id}' "
        f"already exists with a different definition."
    )


PermissionRegistry.register_safe = (
    _permission_register_safe
)


# ============================================================
# REPLACE
# ============================================================

def _permission_replace(
    self,
    definition: PermissionDefinition,
) -> PermissionDefinition:

    self._validate_definition(
        definition
    )

    permission_id = (
        definition.permission_id
    )

    if permission_id not in self._permissions:
        raise PermissionNotFoundError(
            f"Permission not found: "
            f"{permission_id}"
        )

    self._permissions[
        permission_id
    ] = definition

    return definition


PermissionRegistry.replace = (
    _permission_replace
)


# ============================================================
# PERMISSION IDS
# ============================================================

def _permission_ids(
    self,
) -> Tuple[str, ...]:

    return tuple(
        sorted(
            self._permissions.keys()
        )
    )


PermissionRegistry.permission_ids = (
    _permission_ids
)


# ============================================================
# ACTIVE PERMISSIONS
# ============================================================

def _permission_active_permissions(
    self,
) -> Tuple[
    PermissionDefinition,
    ...,
]:

    return self.list_by_status(
        "active"
    )


PermissionRegistry.active_permissions = (
    _permission_active_permissions
)


# ============================================================
# RESOURCE INDEX
# ============================================================

def _permission_resource_index(
    self,
) -> Dict[
    str,
    Tuple[str, ...],
]:

    index: Dict[
        str,
        list[str],
    ] = {}

    for permission in self._permissions.values():

        index.setdefault(
            permission.resource,
            [],
        ).append(
            permission.permission_id
        )

    return {
        resource: tuple(
            sorted(permission_ids)
        )
        for resource, permission_ids
        in sorted(index.items())
    }


PermissionRegistry.resource_index = (
    _permission_resource_index
)


# ============================================================
# ACTION INDEX
# ============================================================

def _permission_action_index(
    self,
) -> Dict[
    str,
    Tuple[str, ...],
]:

    index: Dict[
        str,
        list[str],
    ] = {}

    for permission in self._permissions.values():

        index.setdefault(
            permission.action,
            [],
        ).append(
            permission.permission_id
        )

    return {
        action: tuple(
            sorted(permission_ids)
        )
        for action, permission_ids
        in sorted(index.items())
    }


PermissionRegistry.action_index = (
    _permission_action_index
)


# ============================================================
# DOMAIN INDEX
# ============================================================

def _permission_domain_index(
    self,
) -> Dict[
    str,
    Tuple[str, ...],
]:

    index: Dict[
        str,
        list[str],
    ] = {}

    for permission in self._permissions.values():

        index.setdefault(
            permission.domain,
            [],
        ).append(
            permission.permission_id
        )

    return {
        domain: tuple(
            sorted(permission_ids)
        )
        for domain, permission_ids
        in sorted(index.items())
    }


PermissionRegistry.domain_index = (
    _permission_domain_index
)


# ============================================================
# TAG INDEX
# ============================================================

def _permission_tag_index(
    self,
) -> Dict[
    str,
    Tuple[str, ...],
]:

    index: Dict[
        str,
        list[str],
    ] = {}

    for permission in self._permissions.values():

        for tag in permission.tags:

            index.setdefault(
                tag,
                [],
            ).append(
                permission.permission_id
            )

    return {
        tag: tuple(
            sorted(
                set(permission_ids)
            )
        )
        for tag, permission_ids
        in sorted(index.items())
    }


PermissionRegistry.tag_index = (
    _permission_tag_index
)


# ============================================================
# UNREGISTER
# ============================================================

def _permission_unregister(
    self,
    permission_id: str,
    force: bool = False,
) -> PermissionDefinition:

    permission_id = (
        self._normalize_permission_id(
            permission_id
        )
    )

    permission = self.get(
        permission_id
    )

    # Permission relationships may be declared
    # later through metadata. Check them here
    # without assuming a specific authorization model.
    dependents = []

    for candidate in self._permissions.values():

        dependencies = candidate.metadata.get(
            "depends_on",
            (),
        )

        if permission_id in dependencies:
            dependents.append(
                candidate.permission_id
            )

    if dependents and not force:

        raise PermissionUnregisterError(
            f"Cannot unregister permission "
            f"'{permission_id}'. "
            f"Dependent permissions exist: "
            f"{', '.join(sorted(dependents))}"
        )

    del self._permissions[
        permission_id
    ]

    return permission


PermissionRegistry.unregister = (
    _permission_unregister
)


# ============================================================
# DEPENDENTS
# ============================================================

def _permission_dependents(
    self,
    permission_id: str,
) -> Tuple[str, ...]:

    permission_id = (
        self._normalize_permission_id(
            permission_id
        )
    )

    if permission_id not in self._permissions:
        raise PermissionNotFoundError(
            f"Permission not found: "
            f"{permission_id}"
        )

    dependents = []

    for permission in self._permissions.values():

        dependencies = permission.metadata.get(
            "depends_on",
            (),
        )

        if permission_id in dependencies:
            dependents.append(
                permission.permission_id
            )

    return tuple(
        sorted(dependents)
    )


PermissionRegistry.dependents = (
    _permission_dependents
)


# ============================================================
# DEPENDENCY GRAPH
# ============================================================

def _permission_dependency_graph(
    self,
) -> Dict[
    str,
    Tuple[str, ...],
]:

    graph = {}

    for permission in self._permissions.values():

        dependencies = permission.metadata.get(
            "depends_on",
            (),
        )

        if isinstance(
            dependencies,
            str,
        ):
            dependencies = (
                dependencies,
            )

        graph[
            permission.permission_id
        ] = tuple(
            dependencies
        )

    return graph


PermissionRegistry.dependency_graph = (
    _permission_dependency_graph
)


# ============================================================
# DEPENDENCY VALIDATION
# ============================================================

def _permission_validate_dependencies(
    self,
    permission_id: str,
) -> bool:

    permission_id = (
        self._normalize_permission_id(
            permission_id
        )
    )

    permission = self.get(
        permission_id
    )

    dependencies = permission.metadata.get(
        "depends_on",
        (),
    )

    if isinstance(
        dependencies,
        str,
    ):
        dependencies = (
            dependencies,
        )

    missing = [
        dependency
        for dependency in dependencies
        if dependency
        not in self._permissions
    ]

    if missing:

        raise PermissionDependencyError(
            f"Permission '{permission_id}' "
            f"has missing dependencies: "
            f"{', '.join(missing)}"
        )

    return True


PermissionRegistry.validate_dependencies = (
    _permission_validate_dependencies
)


# ============================================================
# VALIDATE ALL DEPENDENCIES
# ============================================================

def _permission_validate_all_dependencies(
    self,
) -> bool:

    errors = {}

    for permission_id in self._permissions:

        try:

            self.validate_dependencies(
                permission_id
            )

        except PermissionDependencyError as exc:

            errors[
                permission_id
            ] = str(exc)

    if errors:

        raise PermissionDependencyError(
            f"Permission dependency validation "
            f"failed: {errors}"
        )

    return True


PermissionRegistry.validate_all_dependencies = (
    _permission_validate_all_dependencies
)


# ============================================================
# SUMMARY
# ============================================================

def _permission_summary(
    self,
) -> dict:

    status_counts = {
        status: 0
        for status
        in VALID_PERMISSION_STATUSES
    }

    domain_counts = {}
    resource_counts = {}
    action_counts = {}

    for permission in self._permissions.values():

        status_counts[
            permission.status
        ] += 1

        domain_counts[
            permission.domain
        ] = (
            domain_counts.get(
                permission.domain,
                0,
            ) + 1
        )

        resource_counts[
            permission.resource
        ] = (
            resource_counts.get(
                permission.resource,
                0,
            ) + 1
        )

        action_counts[
            permission.action
        ] = (
            action_counts.get(
                permission.action,
                0,
            ) + 1
        )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "total_permissions": (
            len(self._permissions)
        ),
        "status_counts": status_counts,
        "domain_counts": dict(
            sorted(
                domain_counts.items()
            )
        ),
        "resource_counts": dict(
            sorted(
                resource_counts.items()
            )
        ),
        "action_counts": dict(
            sorted(
                action_counts.items()
            )
        ),
    }


PermissionRegistry.summary = (
    _permission_summary
)


# ============================================================
# HEALTH CHECK
# ============================================================

def _permission_health(
    self,
) -> dict:

    dependency_errors = []

    for permission_id in self._permissions:

        try:

            self.validate_dependencies(
                permission_id
            )

        except PermissionDependencyError as exc:

            dependency_errors.append(
                {
                    "permission_id":
                        permission_id,
                    "error":
                        str(exc),
                }
            )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": not dependency_errors,
        "permission_count": (
            len(self._permissions)
        ),
        "dependency_errors": (
            dependency_errors
        ),
    }
    

PermissionRegistry.health = (
    _permission_health
)
# ============================================================
# PERMISSION REGISTRY — PART 3
# Search / Bootstrap / Snapshot / Restore / Consistency
# ============================================================

from dataclasses import asdict


class PermissionBootstrapError(PermissionRegistryError):
    """Raised when permission bootstrap cannot be completed."""


class PermissionSnapshotError(PermissionRegistryError):
    """Raised when permission snapshot handling fails."""


# ============================================================
# SEARCH
# ============================================================

def _permission_find(
    self,
    domain: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
):
    results = list(self._permissions.values())

    if domain is not None:
        domain = self._normalize_text(domain)
        results = [
            p for p in results
            if p.domain == domain
        ]

    if resource is not None:
        resource = self._normalize_text(resource)
        results = [
            p for p in results
            if p.resource == resource
        ]

    if action is not None:
        action = self._normalize_text(action)
        results = [
            p for p in results
            if p.action == action
        ]

    if status is not None:
        status = self._normalize_text(status)
        results = [
            p for p in results
            if p.status == status
        ]

    if tag is not None:
        tag = self._normalize_text(tag)
        results = [
            p for p in results
            if tag in p.tags
        ]

    return tuple(results)


def _permission_find_by_prefix(self, prefix: str):
    prefix = self._normalize_permission_id(prefix)

    return tuple(
        permission
        for permission in self._permissions.values()
        if permission.permission_id.startswith(prefix)
    )


def _permission_find_by_domain(self, domain: str):
    return self.find(domain=domain)


def _permission_find_by_resource(self, resource: str):
    return self.find(resource=resource)


def _permission_find_by_action(self, action: str):
    return self.find(action=action)


def _permission_find_by_tag(self, tag: str):
    return self.find(tag=tag)


PermissionRegistry.find = _permission_find
PermissionRegistry.find_by_prefix = _permission_find_by_prefix
PermissionRegistry.find_by_domain = _permission_find_by_domain
PermissionRegistry.find_by_resource = _permission_find_by_resource
PermissionRegistry.find_by_action = _permission_find_by_action
PermissionRegistry.find_by_tag = _permission_find_by_tag


# ============================================================
# DEPENDENCY EXTRACTION
# ============================================================

def _permission_dependency_ids(permission: PermissionDefinition):
    dependencies = permission.metadata.get("depends_on", ())

    if dependencies is None:
        return ()

    if isinstance(dependencies, str):
        dependencies = (dependencies,)

    return tuple(
        self_id
        for self_id in (
            str(dep).strip()
            for dep in dependencies
        )
        if self_id
    )


def _permission_dependency_graph_for(
    self,
    definitions: Iterable[PermissionDefinition],
):
    definitions = tuple(definitions)

    graph = {
        definition.permission_id: tuple(
            dep
            for dep in (
                str(dep).strip()
                for dep in definition.metadata.get(
                    "depends_on",
                    ()
                )
            )
            if dep
        )
        for definition in definitions
    }

    return graph


# ============================================================
# BOOTSTRAP VALIDATION
# ============================================================

def _permission_validate_bootstrap(
    self,
    definitions: Iterable[PermissionDefinition],
):
    definitions = tuple(definitions)

    ids = [
        definition.permission_id
        for definition in definitions
    ]

    if len(ids) != len(set(ids)):
        raise PermissionBootstrapError(
            "Duplicate permission IDs found in bootstrap."
        )

    definition_map = {
        definition.permission_id: definition
        for definition in definitions
    }

    # Dependencies may already exist in the registry
    # or may be supplied in the same bootstrap batch.
    available_ids = set(self._permissions.keys())
    available_ids.update(definition_map.keys())

    for definition in definitions:
        dependencies = definition.metadata.get(
            "depends_on",
            ()
        )

        if isinstance(dependencies, str):
            dependencies = (dependencies,)

        for dependency in dependencies:
            dependency = str(dependency).strip()

            if dependency and dependency not in available_ids:
                raise PermissionDependencyError(
                    f"Permission '{definition.permission_id}' "
                    f"depends on missing permission "
                    f"'{dependency}'."
                )

    return True


# ============================================================
# DEPENDENCY-RESOLVED BOOTSTRAP
# ============================================================

def _permission_bootstrap(
    self,
    definitions: Iterable[PermissionDefinition],
):
    definitions = tuple(definitions)

    self.validate_bootstrap(definitions)

    definition_map = {
        definition.permission_id: definition
        for definition in definitions
    }

    pending = set(definition_map.keys())
    registered_order = []

    while pending:
        progress = False

        for permission_id in tuple(pending):
            definition = definition_map[permission_id]

            dependencies = definition.metadata.get(
                "depends_on",
                ()
            )

            if isinstance(dependencies, str):
                dependencies = (dependencies,)

            dependencies = {
                str(dep).strip()
                for dep in dependencies
                if str(dep).strip()
            }

            unresolved = {
                dependency
                for dependency in dependencies
                if (
                    dependency in pending
                    or not self.exists(dependency)
                )
            }

            if unresolved:
                continue

            self.register_safe(definition)

            pending.remove(permission_id)
            registered_order.append(permission_id)
            progress = True

        if not progress:
            unresolved_map = {}

            for permission_id in pending:
                definition = definition_map[permission_id]

                dependencies = definition.metadata.get(
                    "depends_on",
                    ()
                )

                if isinstance(dependencies, str):
                    dependencies = (dependencies,)

                unresolved_map[permission_id] = tuple(
                    dependency
                    for dependency in dependencies
                    if (
                        dependency in pending
                        or not self.exists(dependency)
                    )
                )

            raise PermissionBootstrapError(
                "Unable to resolve permission dependency graph: "
                f"{unresolved_map}"
            )

    self.validate_all_dependencies()

    return tuple(
        self.get(permission_id)
        for permission_id in registered_order
    )


PermissionRegistry.validate_bootstrap = _permission_validate_bootstrap
PermissionRegistry.bootstrap = _permission_bootstrap


# ============================================================
# SNAPSHOT
# ============================================================

def _permission_snapshot(self):
    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "permission_count": self.count(),
        "permissions": [
            asdict(permission)
            for permission in self.list_all()
        ],
    }


def _permission_restore_snapshot(
    self,
    snapshot: Dict[str, Any],
    replace_existing: bool = False,
):
    if not isinstance(snapshot, dict):
        raise PermissionSnapshotError(
            "Snapshot must be a dictionary."
        )

    permissions = snapshot.get("permissions")

    if not isinstance(permissions, list):
        raise PermissionSnapshotError(
            "Snapshot does not contain a valid "
            "'permissions' list."
        )

    definitions = []

    for item in permissions:
        if not isinstance(item, dict):
            raise PermissionSnapshotError(
                "Invalid permission snapshot entry."
            )

        item = dict(item)

        # registered_at must be accepted as a datetime
        # by PermissionDefinition.
        registered_at = item.get("registered_at")

        if isinstance(registered_at, str):
            try:
                item["registered_at"] = datetime.fromisoformat(
                    registered_at
                )
            except ValueError as exc:
                raise PermissionSnapshotError(
                    "Invalid registered_at timestamp."
                ) from exc

        definitions.append(
            PermissionDefinition(**item)
        )

    if replace_existing:
        self._permissions.clear()

    return self.bootstrap(definitions)


PermissionRegistry.snapshot = _permission_snapshot
PermissionRegistry.restore_snapshot = _permission_restore_snapshot


# ============================================================
# METADATA EXPORT
# ============================================================

def _permission_export_metadata(self):
    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "permission_count": self.count(),
        "permissions": [
            {
                "permission_id": permission.permission_id,
                "name": permission.name,
                "version": permission.version,
                "domain": permission.domain,
                "resource": permission.resource,
                "action": permission.action,
                "description": permission.description,
                "status": permission.status,
                "owner": permission.owner,
                "tags": tuple(permission.tags),
                "metadata": dict(permission.metadata),
                "registered_at": permission.registered_at.isoformat(),
            }
            for permission in self.list_all()
        ],
    }


PermissionRegistry.export_metadata = _permission_export_metadata


# ============================================================
# CONSISTENCY CHECK
# ============================================================

def _permission_consistency_check(self):
    errors = []
    warnings = []

    permissions = self.list_all()

    # --------------------------------------------------------
    # ID uniqueness
    # --------------------------------------------------------

    ids = [
        permission.permission_id
        for permission in permissions
    ]

    if len(ids) != len(set(ids)):
        errors.append(
            "Duplicate permission IDs detected."
        )

    # --------------------------------------------------------
    # Definition validation
    # --------------------------------------------------------

    for permission in permissions:
        try:
            self._validate_definition(permission)
        except Exception as exc:
            errors.append(
                f"{permission.permission_id}: "
                f"invalid definition: {exc}"
            )

    # --------------------------------------------------------
    # Dependency validation
    # --------------------------------------------------------

    try:
        self.validate_all_dependencies()
    except Exception as exc:
        errors.append(
            f"Dependency validation failed: {exc}"
        )

    # --------------------------------------------------------
    # Resource/action consistency
    # --------------------------------------------------------

    resource_action_seen = {}

    for permission in permissions:
        key = (
            permission.resource,
            permission.action,
        )

        existing = resource_action_seen.get(key)

        if existing is not None:
            warnings.append(
                "Multiple permissions share resource/action "
                f"'{key}': "
                f"{existing} and {permission.permission_id}"
            )
        else:
            resource_action_seen[key] = permission.permission_id

    # --------------------------------------------------------
    # Status consistency
    # --------------------------------------------------------

    for permission in permissions:
        if permission.status not in VALID_PERMISSION_STATUSES:
            errors.append(
                f"{permission.permission_id}: "
                f"invalid status '{permission.status}'."
            )

    return {
        "healthy": not errors,
        "permission_count": self.count(),
        "errors": tuple(errors),
        "warnings": tuple(warnings),
    }


PermissionRegistry.consistency_check = _permission_consistency_check


# ============================================================
# FULL AUDIT
# ============================================================

def _permission_full_audit(self):
    consistency = self.consistency_check()
    health = self.health()
    summary = self.summary()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": (
            consistency["healthy"]
            and health.get("healthy", False)
        ),
        "summary": summary,
        "health": health,
        "consistency": consistency,
    }


PermissionRegistry.full_audit = _permission_full_audit


# ============================================================
# ASSERT HEALTHY
# ============================================================

def _permission_assert_healthy(self):
    audit = self.full_audit()

    if not audit["healthy"]:
        raise PermissionRegistryError(
            "Permission registry is unhealthy: "
            f"{audit}"
        )

    return True


PermissionRegistry.assert_healthy = _permission_assert_healthy


# ============================================================
# STATE
# ============================================================

def _permission_state(self):
    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": self.count(),
        "active": len(self.active_permissions()),
        "domains": tuple(
            sorted(
                {
                    permission.domain
                    for permission in self.list_all()
                }
            )
        ),
        "resources": tuple(
            sorted(
                {
                    permission.resource
                    for permission in self.list_all()
                }
            )
        ),
        "actions": tuple(
            sorted(
                {
                    permission.action
                    for permission in self.list_all()
                }
            )
        ),
        "healthy": self.health().get(
            "healthy",
            False,
        ),
    }


PermissionRegistry.state = _permission_state
# ============================================================
# PERMISSION REGISTRY — PART 4
# Declarative Specs / Discovery / Registration
# ============================================================

from dataclasses import dataclass, field


# ============================================================
# REGISTRATION SPEC
# ============================================================

@dataclass(frozen=True)
class PermissionRegistrationSpec:
    """
    Declarative permission registration specification.

    This object describes a permission.
    It does not perform authorization.
    """

    permission_id: str
    name: str
    version: str
    domain: str
    resource: str
    action: str

    description: str = ""

    status: str = "registered"
    owner: str = ""

    tags: Tuple[str, ...] = field(
        default_factory=tuple
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_definition(self) -> PermissionDefinition:
        return PermissionDefinition(
            permission_id=self.permission_id,
            name=self.name,
            version=self.version,
            domain=self.domain,
            resource=self.resource,
            action=self.action,
            description=self.description,
            status=self.status,
            owner=self.owner,
            tags=tuple(self.tags),
            metadata=dict(self.metadata),
        )


# ============================================================
# SPEC VALIDATION
# ============================================================

def _validate_permission_spec(
    spec: PermissionRegistrationSpec,
):
    if not isinstance(
        spec,
        PermissionRegistrationSpec,
    ):
        raise InvalidPermissionDefinitionError(
            "Expected PermissionRegistrationSpec."
        )

    definition = spec.to_definition()

    # Reuse the registry's canonical validation rules.
    permission_registry._validate_definition(
        definition
    )

    return True


# ============================================================
# REGISTER SPEC
# ============================================================

def _permission_register_spec(
    self,
    spec: PermissionRegistrationSpec,
):
    _validate_permission_spec(spec)

    return self.register(
        spec.to_definition()
    )


def _permission_register_specs(
    self,
    specs: Iterable[PermissionRegistrationSpec],
):
    definitions = []

    for spec in specs:
        _validate_permission_spec(spec)
        definitions.append(
            spec.to_definition()
        )

    return self.bootstrap(definitions)


PermissionRegistry.register_spec = _permission_register_spec
PermissionRegistry.register_specs = _permission_register_specs


# ============================================================
# GLOBAL DISCOVERY STORE
# ============================================================

_PERMISSION_REGISTRATION_SPECS: Dict[
    str,
    PermissionRegistrationSpec,
] = {}


# ============================================================
# PERMISSION SPEC DECORATOR
# ============================================================

def permission_spec(
    permission_id: str,
    name: str,
    version: str,
    domain: str,
    resource: str,
    action: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    tags: Iterable[str] = (),
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Declaratively attach a PermissionRegistrationSpec
    to a class/function without executing authorization logic.
    """

    if metadata is None:
        metadata = {}

    spec = PermissionRegistrationSpec(
        permission_id=permission_id,
        name=name,
        version=version,
        domain=domain,
        resource=resource,
        action=action,
        description=description,
        status=status,
        owner=owner,
        tags=tuple(tags),
        metadata=dict(metadata),
    )

    _validate_permission_spec(spec)

    def decorator(target):
        existing = _PERMISSION_REGISTRATION_SPECS.get(
            spec.permission_id
        )

        if existing is not None:
            if existing != spec:
                raise PermissionRegistrationConflictError(
                    "Conflicting permission specification "
                    f"for '{spec.permission_id}'."
                )

        _PERMISSION_REGISTRATION_SPECS[
            spec.permission_id
        ] = spec

        setattr(
            target,
            "__robomlm_permission_spec__",
            spec,
        )

        return target

    return decorator


# ============================================================
# DISCOVERY
# ============================================================

def discover_permission_specs():
    """
    Return all declaratively registered permission specs.

    Discovery only reads metadata.
    It does not execute permission logic.
    """

    return tuple(
        _PERMISSION_REGISTRATION_SPECS.values()
    )


def get_permission_spec(
    permission_id: str,
):
    permission_id = permission_registry._normalize_permission_id(
        permission_id
    )

    return _PERMISSION_REGISTRATION_SPECS.get(
        permission_id
    )


# ============================================================
# REGISTER DISCOVERED PERMISSIONS
# ============================================================

def _permission_register_discovered(
    self,
):
    specs = discover_permission_specs()

    if not specs:
        return ()

    return self.register_specs(specs)


PermissionRegistry.register_discovered = (
    _permission_register_discovered
)


# ============================================================
# DISCOVERY REPORT
# ============================================================

def _permission_discovery_report(self):
    discovered = discover_permission_specs()

    registered_ids = set(
        self.permission_ids()
    )

    discovered_ids = {
        spec.permission_id
        for spec in discovered
    }

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "discovered_count": len(discovered),
        "registered_count": len(registered_ids),

        "discovered_permission_ids": tuple(
            sorted(discovered_ids)
        ),

        "registered_and_discovered": tuple(
            sorted(
                discovered_ids
                & registered_ids
            )
        ),

        "discovered_but_not_registered": tuple(
            sorted(
                discovered_ids
                - registered_ids
            )
        ),

        "registered_but_not_discovered": tuple(
            sorted(
                registered_ids
                - discovered_ids
            )
        ),
    }


PermissionRegistry.discovery_report = (
    _permission_discovery_report
)


# ============================================================
# DISCOVERED METADATA EXPORT
# ============================================================

def export_discovered_permission_metadata():
    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "permission_count": len(
            _PERMISSION_REGISTRATION_SPECS
        ),
        "permissions": [
            {
                "permission_id": spec.permission_id,
                "name": spec.name,
                "version": spec.version,
                "domain": spec.domain,
                "resource": spec.resource,
                "action": spec.action,
                "description": spec.description,
                "status": spec.status,
                "owner": spec.owner,
                "tags": tuple(spec.tags),
                "metadata": dict(spec.metadata),
            }
            for spec
            in discover_permission_specs()
        ],
    }


# ============================================================
# SPEC CONSISTENCY CHECK
# ============================================================

def _permission_spec_consistency_check(self):
    errors = []
    warnings = []

    specs = discover_permission_specs()

    # --------------------------------------------------------
    # Duplicate IDs
    # --------------------------------------------------------

    ids = [
        spec.permission_id
        for spec in specs
    ]

    if len(ids) != len(set(ids)):
        errors.append(
            "Duplicate permission specification IDs detected."
        )

    # --------------------------------------------------------
    # Validate every discovered specification
    # --------------------------------------------------------

    for spec in specs:
        try:
            _validate_permission_spec(spec)
        except Exception as exc:
            errors.append(
                f"{spec.permission_id}: "
                f"invalid specification: {exc}"
            )

    # --------------------------------------------------------
    # Compare discovered specs with registry
    # --------------------------------------------------------

    for spec in specs:
        if not self.exists(spec.permission_id):
            warnings.append(
                f"Permission '{spec.permission_id}' "
                "is discovered but not registered."
            )
            continue

        registered = self.get(
            spec.permission_id
        )

        expected = spec.to_definition()

        if registered != expected:
            errors.append(
                f"Permission '{spec.permission_id}' "
                "differs from its discovered specification."
            )

    return {
        "healthy": not errors,
        "discovered_count": len(specs),
        "errors": tuple(errors),
        "warnings": tuple(warnings),
    }


PermissionRegistry.spec_consistency_check = (
    _permission_spec_consistency_check
)


# ============================================================
# FULL DISCOVERY AUDIT
# ============================================================

def _permission_discovery_audit(self):
    discovery = self.discovery_report()
    consistency = self.spec_consistency_check()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": consistency["healthy"],
        "discovery": discovery,
        "consistency": consistency,
    }


PermissionRegistry.discovery_audit = (
    _permission_discovery_audit
)


# ============================================================
# ASSERT DISCOVERY HEALTH
# ============================================================

def _permission_assert_discovery_healthy(self):
    audit = self.discovery_audit()

    if not audit["healthy"]:
        raise PermissionRegistryError(
            "Permission discovery is unhealthy: "
            f"{audit}"
        )

    return True


PermissionRegistry.assert_discovery_healthy = (
    _permission_assert_discovery_healthy
)
# ============================================================
# PERMISSION REGISTRY — PART 5
# Freeze / Atomic Install / Canonical Catalog / Final Audit
# ============================================================

from copy import deepcopy


# ============================================================
# PART 5 EXCEPTIONS
# ============================================================

class PermissionRegistryFrozenError(PermissionRegistryError):
    """Raised when a mutation is attempted on a frozen registry."""


class PermissionAuditError(PermissionRegistryError):
    """Raised when permission registry audit fails."""


class PermissionAtomicInstallError(PermissionRegistryError):
    """Raised when an atomic permission installation fails."""


# ============================================================
# FREEZE STATE
# ============================================================

PermissionRegistry._frozen = False


def _permission_is_frozen(self):
    return bool(
        getattr(self, "_frozen", False)
    )


def _permission_assert_mutable(self):
    if self.is_frozen():
        raise PermissionRegistryFrozenError(
            "Permission registry is frozen. "
            "Unfreeze it before mutation."
        )

    return True


def _permission_freeze(self):
    self._frozen = True
    return True


def _permission_unfreeze(self):
    self._frozen = False
    return True


PermissionRegistry.is_frozen = _permission_is_frozen
PermissionRegistry.assert_mutable = _permission_assert_mutable
PermissionRegistry.freeze = _permission_freeze
PermissionRegistry.unfreeze = _permission_unfreeze


# ============================================================
# MUTATION GUARDS
# ============================================================

_permission_original_register = PermissionRegistry.register
_permission_original_replace = PermissionRegistry.replace
_permission_original_unregister = PermissionRegistry.unregister


def _permission_guarded_register(
    self,
    definition: PermissionDefinition,
):
    self.assert_mutable()

    return _permission_original_register(
        self,
        definition,
    )


def _permission_guarded_replace(
    self,
    definition: PermissionDefinition,
):
    self.assert_mutable()

    return _permission_original_replace(
        self,
        definition,
    )


def _permission_guarded_unregister(
    self,
    permission_id: str,
    force: bool = False,
):
    self.assert_mutable()

    return _permission_original_unregister(
        self,
        permission_id,
        force=force,
    )


PermissionRegistry.register = _permission_guarded_register
PermissionRegistry.replace = _permission_guarded_replace
PermissionRegistry.unregister = _permission_guarded_unregister


# ============================================================
# GUARDED CLEAR
# ============================================================

if hasattr(PermissionRegistry, "clear"):

    _permission_original_clear = (
        PermissionRegistry.clear
    )

    def _permission_guarded_clear(
        self,
        force: bool = False,
    ):
        self.assert_mutable()

        return _permission_original_clear(
            self,
            force=force,
        )

    PermissionRegistry.clear = _permission_guarded_clear


# ============================================================
# GUARDED STATUS CHANGES
# ============================================================

_permission_original_set_status = (
    PermissionRegistry.set_status
)


def _permission_guarded_set_status(
    self,
    permission_id: str,
    status: str,
):
    self.assert_mutable()

    return _permission_original_set_status(
        self,
        permission_id,
        status,
    )


PermissionRegistry.set_status = (
    _permission_guarded_set_status
)


# ============================================================
# CLONE
# ============================================================

def _permission_clone(self):
    cloned = PermissionRegistry()

    cloned._permissions = deepcopy(
        self._permissions
    )

    cloned._frozen = self.is_frozen()

    return cloned


PermissionRegistry.clone = _permission_clone


# ============================================================
# ATOMIC REGISTER
# ============================================================

def _permission_atomic_register(
    self,
    definitions: Iterable[PermissionDefinition],
):
    self.assert_mutable()

    definitions = tuple(definitions)

    backup = deepcopy(
        self._permissions
    )

    try:
        registered = self.bootstrap(
            definitions
        )

        self.validate_all_dependencies()

        return registered

    except Exception as exc:

        self._permissions = backup

        raise PermissionAtomicInstallError(
            "Atomic permission registration failed. "
            "Registry state was rolled back."
        ) from exc


PermissionRegistry.atomic_register = (
    _permission_atomic_register
)


# ============================================================
# ATOMIC SPEC REGISTER
# ============================================================

def _permission_atomic_register_specs(
    self,
    specs: Iterable[PermissionRegistrationSpec],
):
    definitions = []

    for spec in specs:
        _validate_permission_spec(spec)

        definitions.append(
            spec.to_definition()
        )

    return self.atomic_register(
        definitions
    )


PermissionRegistry.atomic_register_specs = (
    _permission_atomic_register_specs
)


# ============================================================
# DEPENDENCY AUDIT
# ============================================================

def _permission_dependency_audit(self):
    errors = []

    for permission in self.list_all():

        dependencies = permission.metadata.get(
            "depends_on",
            ()
        )

        if isinstance(dependencies, str):
            dependencies = (dependencies,)

        for dependency in dependencies:

            dependency = str(
                dependency
            ).strip()

            if not dependency:
                continue

            if not self.exists(dependency):
                errors.append(
                    f"{permission.permission_id} "
                    f"depends on missing permission "
                    f"{dependency}"
                )

    return {
        "healthy": not errors,
        "permission_count": self.count(),
        "errors": tuple(errors),
    }


PermissionRegistry.dependency_audit = (
    _permission_dependency_audit
)


# ============================================================
# STATUS AUDIT
# ============================================================

def _permission_status_audit(self):
    errors = []
    status_counts = {
        status: 0
        for status in VALID_PERMISSION_STATUSES
    }

    for permission in self.list_all():

        if permission.status not in (
            VALID_PERMISSION_STATUSES
        ):
            errors.append(
                f"{permission.permission_id}: "
                f"invalid status "
                f"'{permission.status}'"
            )
            continue

        status_counts[
            permission.status
        ] += 1

    return {
        "healthy": not errors,
        "status_counts": status_counts,
        "errors": tuple(errors),
    }


PermissionRegistry.status_audit = (
    _permission_status_audit
)


# ============================================================
# DEFINITION AUDIT
# ============================================================

def _permission_definition_audit(self):
    errors = []

    for permission in self.list_all():

        try:
            self._validate_definition(
                permission
            )

        except Exception as exc:
            errors.append(
                f"{permission.permission_id}: "
                f"{exc}"
            )

    return {
        "healthy": not errors,
        "permission_count": self.count(),
        "errors": tuple(errors),
    }


PermissionRegistry.definition_audit = (
    _permission_definition_audit
)


# ============================================================
# CANONICAL PERMISSION CATALOG
# ============================================================

PERMISSION_DOMAIN_CORE = "core"
PERMISSION_DOMAIN_MARKET = "market"
PERMISSION_DOMAIN_EVIDENCE = "evidence"
PERMISSION_DOMAIN_DECISION = "decision"
PERMISSION_DOMAIN_RISK = "risk"
PERMISSION_DOMAIN_CAS = "cas"
PERMISSION_DOMAIN_MEMORY = "memory"
PERMISSION_DOMAIN_DISCOVERY = "discovery"
PERMISSION_DOMAIN_RESEARCH = "research"
PERMISSION_DOMAIN_AUTOMATION = "automation"
PERMISSION_DOMAIN_ACCOUNT = "account"
PERMISSION_DOMAIN_ADMIN = "admin"


# ------------------------------------------------------------
# Canonical actions
# ------------------------------------------------------------

PERMISSION_ACTION_VIEW = "view"
PERMISSION_ACTION_READ = "read"
PERMISSION_ACTION_USE = "use"
PERMISSION_ACTION_RUN = "run"
PERMISSION_ACTION_MANAGE = "manage"
PERMISSION_ACTION_ADMIN = "admin"


# ------------------------------------------------------------
# Canonical resource families
# ------------------------------------------------------------

PERMISSION_RESOURCE_TERMINAL = "terminal"
PERMISSION_RESOURCE_MARKET_DATA = "market_data"
PERMISSION_RESOURCE_EVIDENCE = "evidence"
PERMISSION_RESOURCE_DECISION = "decision"
PERMISSION_RESOURCE_RISK = "risk"
PERMISSION_RESOURCE_CAS = "cas"
PERMISSION_RESOURCE_MEMORY = "memory"
PERMISSION_RESOURCE_DISCOVERY = "discovery"
PERMISSION_RESOURCE_RESEARCH = "research"
PERMISSION_RESOURCE_AUTOMATION = "automation"
PERMISSION_RESOURCE_ACCOUNT = "account"
PERMISSION_RESOURCE_ADMIN = "admin"


# ============================================================
# CANONICAL PERMISSION BUILDER
# ============================================================

def _canonical_permission(
    permission_id: str,
    name: str,
    domain: str,
    resource: str,
    action: str,
    description: str,
    *,
    status: str = "registered",
    owner: str = "ROBOMLM",
    tags: Iterable[str] = (),
    metadata: Optional[Dict[str, Any]] = None,
):
    return PermissionRegistrationSpec(
        permission_id=permission_id,
        name=name,
        version="1.0.0",
        domain=domain,
        resource=resource,
        action=action,
        description=description,
        status=status,
        owner=owner,
        tags=tuple(tags),
        metadata=dict(
            metadata or {}
        ),
    )


# ============================================================
# ROBOMLM CANONICAL PERMISSIONS
# ============================================================

ROBOMLM_CANONICAL_PERMISSION_SPECS = (

    _canonical_permission(
        "terminal.view",
        "View Terminal",
        PERMISSION_DOMAIN_CORE,
        PERMISSION_RESOURCE_TERMINAL,
        PERMISSION_ACTION_VIEW,
        "View the ROBOMLM Terminal.",
        tags=("terminal", "read"),
    ),

    _canonical_permission(
        "market_data.read",
        "Read Market Data",
        PERMISSION_DOMAIN_MARKET,
        PERMISSION_RESOURCE_MARKET_DATA,
        PERMISSION_ACTION_READ,
        "Read market data exposed to ROBOMLM.",
        tags=("market", "data", "read"),
    ),

    _canonical_permission(
        "evidence.view",
        "View Evidence",
        PERMISSION_DOMAIN_EVIDENCE,
        PERMISSION_RESOURCE_EVIDENCE,
        PERMISSION_ACTION_VIEW,
        "View evidence generated by the Evidence Cortex.",
        tags=("evidence", "read"),
        metadata={
            "depends_on": (
                "market_data.read",
            )
        },
    ),

    _canonical_permission(
        "decision.view",
        "View Decision Intelligence",
        PERMISSION_DOMAIN_DECISION,
        PERMISSION_RESOURCE_DECISION,
        PERMISSION_ACTION_VIEW,
        "View decision intelligence outputs.",
        tags=("decision", "read"),
        metadata={
            "depends_on": (
                "evidence.view",
            )
        },
    ),

    _canonical_permission(
        "risk.view",
        "View Risk",
        PERMISSION_DOMAIN_RISK,
        PERMISSION_RESOURCE_RISK,
        PERMISSION_ACTION_VIEW,
        "View risk assessment outputs.",
        tags=("risk", "read"),
        metadata={
            "depends_on": (
                "decision.view",
            )
        },
    ),

    _canonical_permission(
        "cas.view",
        "View CAS",
        PERMISSION_DOMAIN_CAS,
        PERMISSION_RESOURCE_CAS,
        PERMISSION_ACTION_VIEW,
        "View CAS governance state.",
        tags=("cas", "read"),
        metadata={
            "depends_on": (
                "risk.view",
            )
        },
    ),

    _canonical_permission(
        "memory.view",
        "View Market Memory",
        PERMISSION_DOMAIN_MEMORY,
        PERMISSION_RESOURCE_MEMORY,
        PERMISSION_ACTION_VIEW,
        "View permitted market-memory information.",
        tags=("memory", "read"),
    ),

    _canonical_permission(
        "discovery.use",
        "Use Opportunity Discovery",
        PERMISSION_DOMAIN_DISCOVERY,
        PERMISSION_RESOURCE_DISCOVERY,
        PERMISSION_ACTION_USE,
        "Use the opportunity discovery system.",
        tags=("discovery", "opportunity"),
        metadata={
            "depends_on": (
                "market_data.read",
            )
        },
    ),

    _canonical_permission(
        "research.use",
        "Use Research",
        PERMISSION_DOMAIN_RESEARCH,
        PERMISSION_RESOURCE_RESEARCH,
        PERMISSION_ACTION_USE,
        "Use the Research environment.",
        tags=("research",),
    ),

    _canonical_permission(
        "automation.run",
        "Run Automation",
        PERMISSION_DOMAIN_AUTOMATION,
        PERMISSION_RESOURCE_AUTOMATION,
        PERMISSION_ACTION_RUN,
        "Request use of the automation capability.",
        tags=("automation",),
        metadata={
            "depends_on": (
                "decision.view",
                "risk.view",
                "cas.view",
            )
        },
    ),

    _canonical_permission(
        "account.manage",
        "Manage Account",
        PERMISSION_DOMAIN_ACCOUNT,
        PERMISSION_RESOURCE_ACCOUNT,
        PERMISSION_ACTION_MANAGE,
        "Manage permitted account settings.",
        tags=("account",),
    ),

    _canonical_permission(
        "admin.manage",
        "Manage Administration",
        PERMISSION_DOMAIN_ADMIN,
        PERMISSION_RESOURCE_ADMIN,
        PERMISSION_ACTION_ADMIN,
        "Access administrative management capabilities.",
        tags=("admin", "restricted"),
    ),
)


# ============================================================
# CANONICAL CATALOG VALIDATION
# ============================================================

def validate_canonical_permission_catalog():
    ids = [
        spec.permission_id
        for spec in ROBOMLM_CANONICAL_PERMISSION_SPECS
    ]

    if len(ids) != len(set(ids)):
        raise PermissionAuditError(
            "Canonical permission catalog contains "
            "duplicate permission IDs."
        )

    for spec in (
        ROBOMLM_CANONICAL_PERMISSION_SPECS
    ):
        _validate_permission_spec(spec)

    return True


# ============================================================
# REGISTER CANONICAL PERMISSIONS
# ============================================================

def register_canonical_permissions():
    validate_canonical_permission_catalog()

    definitions = tuple(
        spec.to_definition()
        for spec
        in ROBOMLM_CANONICAL_PERMISSION_SPECS
    )

    return permission_registry.atomic_register(
        definitions
    )


# ============================================================
# CANONICAL LOOKUP
# ============================================================

def canonical_permission_ids():
    return tuple(
        spec.permission_id
        for spec
        in ROBOMLM_CANONICAL_PERMISSION_SPECS
    )


def canonical_permission_spec(
    permission_id: str,
):
    permission_id = str(
        permission_id
    ).strip()

    for spec in (
        ROBOMLM_CANONICAL_PERMISSION_SPECS
    ):
        if spec.permission_id == permission_id:
            return spec

    raise PermissionNotFoundError(
        f"Canonical permission not found: "
        f"{permission_id}"
    )


# ============================================================
# CANONICAL DOMAIN REPORT
# ============================================================

def canonical_permission_domain_report():
    report = {}

    for spec in (
        ROBOMLM_CANONICAL_PERMISSION_SPECS
    ):
        report.setdefault(
            spec.domain,
            []
        ).append(
            spec.permission_id
        )

    return {
        domain: tuple(
            sorted(permission_ids)
        )
        for domain, permission_ids
        in report.items()
    }


# ============================================================
# CANONICAL DEPENDENCY REPORT
# ============================================================

def canonical_permission_dependency_report():
    report = {}

    for spec in (
        ROBOMLM_CANONICAL_PERMISSION_SPECS
    ):
        dependencies = spec.metadata.get(
            "depends_on",
            ()
        )

        if isinstance(
            dependencies,
            str,
        ):
            dependencies = (
                dependencies,
            )

        report[
            spec.permission_id
        ] = tuple(
            str(dep).strip()
            for dep in dependencies
            if str(dep).strip()
        )

    return report


# ============================================================
# CANONICAL AUDIT
# ============================================================

def audit_canonical_permissions():
    validate_canonical_permission_catalog()

    canonical_ids = set(
        canonical_permission_ids()
    )

    registered_ids = set(
        permission_registry.permission_ids()
    )

    missing = canonical_ids - registered_ids
    extra = registered_ids - canonical_ids

    return {
        "healthy": not missing,
        "canonical_count": len(
            canonical_ids
        ),
        "registered_count": len(
            registered_ids
        ),
        "missing_canonical_permissions": tuple(
            sorted(missing)
        ),
        "registered_noncanonical_permissions": tuple(
            sorted(extra)
        ),
        "domain_report":
            canonical_permission_domain_report(),
        "dependency_report":
            canonical_permission_dependency_report(),
    }


# ============================================================
# FULL PERMISSION REGISTRY AUDIT
# ============================================================

def _permission_full_registry_audit(self):
    canonical = audit_canonical_permissions()
    dependency = self.dependency_audit()
    status = self.status_audit()
    definition = self.definition_audit()
    consistency = self.consistency_check()
    discovery = self.discovery_audit()

    healthy = all(
        (
            canonical["healthy"],
            dependency["healthy"],
            status["healthy"],
            definition["healthy"],
            consistency["healthy"],
            discovery["healthy"],
        )
    )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": healthy,
        "canonical": canonical,
        "dependency": dependency,
        "status": status,
        "definition": definition,
        "consistency": consistency,
        "discovery": discovery,
    }


PermissionRegistry.full_registry_audit = (
    _permission_full_registry_audit
)


# ============================================================
# ASSERT FULL HEALTH
# ============================================================

def _permission_assert_full_health(self):
    audit = self.full_registry_audit()

    if not audit["healthy"]:
        raise PermissionAuditError(
            "Permission registry full audit failed: "
            f"{audit}"
        )

    return True


PermissionRegistry.assert_full_health = (
    _permission_assert_full_health
)


# ============================================================
# FREEZE ONLY AFTER HEALTHY AUDIT
# ============================================================

def _permission_freeze_if_healthy(self):
    self.assert_full_health()

    self.freeze()

    return {
        "frozen": True,
        "healthy": True,
        "permission_count": self.count(),
    }


PermissionRegistry.freeze_if_healthy = (
    _permission_freeze_if_healthy
)


# ============================================================
# FINAL EXPORT
# ============================================================

def _permission_final_export(self):
    return {
        "registry": self.export_metadata(),
        "state": self.state(),
        "audit": self.full_registry_audit(),
        "canonical_permission_ids":
            canonical_permission_ids(),
    }


PermissionRegistry.final_export = (
    _permission_final_export
)


# ============================================================
# INSTALLATION ENTRY POINT
# ============================================================

def install_permission_registry(
    freeze_after_install: bool = False,
):
    """
    Install canonical ROBOMLM permissions.

    Installation is atomic.
    Existing registry state is preserved if installation fails.
    """

    if permission_registry.is_frozen():
        raise PermissionRegistryFrozenError(
            "Permission registry is already frozen."
        )

    register_canonical_permissions()

    # Decorator-discovered permissions are optional.
    # They are installed only when explicitly discovered.
    if _PERMISSION_REGISTRATION_SPECS:
        permission_registry.atomic_register_specs(
            discover_permission_specs()
        )

    permission_registry.assert_full_health()

    if freeze_after_install:
        permission_registry.freeze()

    return permission_registry.final_export()


# ============================================================
# TEST RESET
# ============================================================

def reset_permission_registry_for_testing():
    """
    Testing utility only.

    Clears registry and discovery state.
    """

    permission_registry.unfreeze()

    permission_registry._permissions.clear()

    _PERMISSION_REGISTRATION_SPECS.clear()

    return True