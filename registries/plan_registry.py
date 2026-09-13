# ============================================================
# ROBOMLM_PLUS
# PLAN REGISTRY — PART 1
# Plan Definition + Registry Foundation
# ============================================================

"""
Plan Registry — Part 1

Purpose
-------
Central metadata registry for ROBOMLM product plans.

This registry defines WHAT a plan is.

It does NOT:
    - process payments
    - calculate billing
    - authorize users
    - enforce permissions
    - execute trades
    - make intelligence decisions
    - implement CAS decisions

Those responsibilities belong to their respective layers.

Architecture Boundary
---------------------
Plan Registry
    ↓
Plan identity + metadata + lifecycle

Subscription / Entitlement Layer
    ↓
User's actual subscription state

Authorization Layer
    ↓
Permission decision

Execution / CAS
    ↓
Operational safety and execution authority
"""


from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional, Tuple


# ============================================================
# REGISTRY CONSTANTS
# ============================================================

REGISTRY_NAME = "plan_registry"
REGISTRY_VERSION = "1.0.0"


VALID_PLAN_STATUSES = {
    "registered",
    "active",
    "disabled",
    "deprecated",
}


# ============================================================
# REGISTRY EXCEPTIONS
# ============================================================

class PlanRegistryError(Exception):
    """Base exception for Plan Registry."""


class PlanAlreadyRegisteredError(PlanRegistryError):
    """Raised when a plan ID is already registered."""


class PlanNotFoundError(PlanRegistryError):
    """Raised when a requested plan does not exist."""


class InvalidPlanDefinitionError(PlanRegistryError):
    """Raised when a plan definition is invalid."""


class PlanStateError(PlanRegistryError):
    """Raised when an invalid plan state transition is requested."""


# ============================================================
# PLAN DEFINITION
# ============================================================

@dataclass(frozen=True)
class PlanDefinition:
    """
    Immutable definition of a ROBOMLM product plan.

    This is descriptive metadata only.

    Feature access and authorization decisions must NOT
    be performed by this object.
    """

    plan_id: str
    name: str
    version: str

    description: str = ""

    status: str = "registered"

    owner: str = ""

    # Product classification
    tier: str = ""

    # Optional display / commercial metadata.
    # No billing calculation is performed here.
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    tags: Tuple[str, ...] = field(
        default_factory=tuple
    )

    registered_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


# ============================================================
# PLAN REGISTRY
# ============================================================

class PlanRegistry:
    """
    Central registry for ROBOMLM plan definitions.
    """

    def __init__(self):
        self._plans: Dict[str, PlanDefinition] = {}


    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        definition: PlanDefinition,
    ) -> PlanDefinition:
        """
        Register a new plan.

        Existing plan IDs are rejected.
        """

        self._validate_definition(
            definition
        )

        plan_id = self._normalize_plan_id(
            definition.plan_id
        )

        if plan_id in self._plans:
            raise PlanAlreadyRegisteredError(
                f"Plan already registered: {plan_id}"
            )

        self._plans[plan_id] = definition

        return definition


    # ========================================================
    # REGISTER MANY
    # ========================================================

    def register_many(
        self,
        definitions: Iterable[PlanDefinition],
    ) -> Tuple[PlanDefinition, ...]:
        """
        Register multiple plans.

        Registration is sequential.
        """

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
        plan_id: str,
    ) -> PlanDefinition:
        """
        Return a registered plan.
        """

        plan_id = self._normalize_plan_id(
            plan_id
        )

        try:
            return self._plans[plan_id]

        except KeyError as exc:
            raise PlanNotFoundError(
                f"Plan not found: {plan_id}"
            ) from exc


    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        plan_id: str,
    ) -> bool:
        """
        Check whether a plan is registered.
        """

        plan_id = self._normalize_plan_id(
            plan_id
        )

        return plan_id in self._plans


    # ========================================================
    # COUNT
    # ========================================================

    def count(self) -> int:
        """
        Return number of registered plans.
        """

        return len(
            self._plans
        )


    # ========================================================
    # LIST ALL
    # ========================================================

    def list_all(self) -> Tuple[PlanDefinition, ...]:
        """
        Return all registered plans.

        Sorted by plan_id for deterministic output.
        """

        return tuple(
            self._plans[plan_id]
            for plan_id in sorted(
                self._plans
            )
        )


    # ========================================================
    # LIST BY STATUS
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> Tuple[PlanDefinition, ...]:
        """
        Return plans matching a lifecycle status.
        """

        status = self._normalize_text(
            status
        )

        return tuple(
            plan
            for plan in self._plans.values()
            if plan.status == status
        )


    # ========================================================
    # LIST BY TIER
    # ========================================================

    def list_by_tier(
        self,
        tier: str,
    ) -> Tuple[PlanDefinition, ...]:
        """
        Return plans belonging to a product tier.
        """

        tier = self._normalize_text(
            tier
        )

        return tuple(
            plan
            for plan in self._plans.values()
            if plan.tier == tier
        )


    # ========================================================
    # LIST BY TAG
    # ========================================================

    def list_by_tag(
        self,
        tag: str,
    ) -> Tuple[PlanDefinition, ...]:
        """
        Return plans containing the specified tag.
        """

        tag = self._normalize_text(
            tag
        )

        return tuple(
            plan
            for plan in self._plans.values()
            if tag in plan.tags
        )


    # ========================================================
    # VALIDATE DEFINITION
    # ========================================================

    def _validate_definition(
        self,
        definition: PlanDefinition,
    ) -> bool:
        """
        Validate basic plan-definition integrity.

        This does not validate commercial pricing or
        subscription entitlement rules.
        """

        if not isinstance(
            definition,
            PlanDefinition,
        ):
            raise InvalidPlanDefinitionError(
                "Expected PlanDefinition."
            )


        plan_id = self._normalize_plan_id(
            definition.plan_id
        )

        if not plan_id:
            raise InvalidPlanDefinitionError(
                "plan_id cannot be empty."
            )


        name = self._normalize_text(
            definition.name
        )

        if not name:
            raise InvalidPlanDefinitionError(
                f"Plan '{plan_id}' must have a name."
            )


        version = self._normalize_text(
            definition.version
        )

        if not version:
            raise InvalidPlanDefinitionError(
                f"Plan '{plan_id}' must have a version."
            )


        status = self._normalize_text(
            definition.status
        )

        if status not in VALID_PLAN_STATUSES:
            raise InvalidPlanDefinitionError(
                f"Invalid status '{status}' for "
                f"plan '{plan_id}'."
            )


        tier = self._normalize_text(
            definition.tier
        )

        if not tier:
            raise InvalidPlanDefinitionError(
                f"Plan '{plan_id}' must define a tier."
            )


        if not isinstance(
            definition.metadata,
            dict,
        ):
            raise InvalidPlanDefinitionError(
                f"Plan '{plan_id}' metadata must be a dict."
            )


        if not isinstance(
            definition.tags,
            tuple,
        ):
            raise InvalidPlanDefinitionError(
                f"Plan '{plan_id}' tags must be a tuple."
            )


        return True


    # ========================================================
    # NORMALIZE PLAN ID
    # ========================================================

    @staticmethod
    def _normalize_plan_id(
        plan_id: str,
    ) -> str:
        """
        Normalize a plan identifier.
        """

        if plan_id is None:
            return ""

        return str(
            plan_id
        ).strip().lower()


    # ========================================================
    # NORMALIZE TEXT
    # ========================================================

    @staticmethod
    def _normalize_text(
        value: str,
    ) -> str:
        """
        Normalize ordinary registry text.
        """

        if value is None:
            return ""

        return str(
            value
        ).strip().lower()


# ============================================================
# GLOBAL PLAN REGISTRY
# ============================================================

plan_registry = PlanRegistry()


# ============================================================
# CONVENIENCE REGISTRATION FUNCTION
# ============================================================

def register_plan(
    plan_id: str,
    name: str,
    version: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    tier: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    tags: Iterable[str] = (),
) -> PlanDefinition:
    """
    Convenience helper for registering a plan.
    """

    definition = PlanDefinition(
        plan_id=plan_id,
        name=name,
        version=version,
        description=description,
        status=status,
        owner=owner,
        tier=tier,
        metadata=dict(
            metadata or {}
        ),
        tags=tuple(tags),
    )

    return plan_registry.register(
        definition
    )
# ============================================================
# PLAN REGISTRY — PART 2
# Lifecycle / Conflict / Indexes / Dependencies
# ============================================================


# ============================================================
# PART 2 EXCEPTIONS
# ============================================================

class PlanRegistrationConflictError(PlanRegistryError):
    """Raised when a plan registration conflicts with existing data."""


class PlanUnregisterError(PlanRegistryError):
    """Raised when a plan cannot be safely unregistered."""


class PlanDependencyError(PlanRegistryError):
    """Raised when a plan dependency is invalid."""


class PlanVersionError(PlanRegistryError):
    """Raised when an invalid plan version operation is requested."""


# ============================================================
# LIFECYCLE
# ============================================================

def _plan_set_status(
    self,
    plan_id: str,
    status: str,
) -> PlanDefinition:
    """
    Change the lifecycle status of a registered plan.
    """

    plan_id = self._normalize_plan_id(
        plan_id
    )

    status = self._normalize_text(
        status
    )

    if status not in VALID_PLAN_STATUSES:
        raise PlanStateError(
            f"Invalid plan status: {status}"
        )

    existing = self.get(
        plan_id
    )

    updated = PlanDefinition(
        plan_id=existing.plan_id,
        name=existing.name,
        version=existing.version,
        description=existing.description,
        status=status,
        owner=existing.owner,
        tier=existing.tier,
        metadata=dict(existing.metadata),
        tags=tuple(existing.tags),
        registered_at=existing.registered_at,
    )

    self._plans[plan_id] = updated

    return updated


def _plan_activate(
    self,
    plan_id: str,
) -> PlanDefinition:
    return self.set_status(
        plan_id,
        "active",
    )


def _plan_disable(
    self,
    plan_id: str,
) -> PlanDefinition:
    return self.set_status(
        plan_id,
        "disabled",
    )


def _plan_deprecate(
    self,
    plan_id: str,
) -> PlanDefinition:
    return self.set_status(
        plan_id,
        "deprecated",
    )


PlanRegistry.set_status = _plan_set_status
PlanRegistry.activate = _plan_activate
PlanRegistry.disable = _plan_disable
PlanRegistry.deprecate = _plan_deprecate


# ============================================================
# PLAN CONFLICT CHECK
# ============================================================

def _plan_check_conflict(
    self,
    definition: PlanDefinition,
) -> bool:
    """
    Check whether a plan ID already exists.

    Returns:
        True  -> conflict exists
        False -> no conflict
    """

    self._validate_definition(
        definition
    )

    plan_id = self._normalize_plan_id(
        definition.plan_id
    )

    return plan_id in self._plans


# ============================================================
# SAFE REGISTER
# ============================================================

def _plan_register_safe(
    self,
    definition: PlanDefinition,
) -> PlanDefinition:
    """
    Register a plan only when no ID conflict exists.
    """

    if self.check_conflict(
        definition
    ):
        raise PlanRegistrationConflictError(
            f"Plan registration conflict: "
            f"{definition.plan_id}"
        )

    return self.register(
        definition
    )


PlanRegistry.check_conflict = _plan_check_conflict
PlanRegistry.register_safe = _plan_register_safe


# ============================================================
# REPLACE
# ============================================================

def _plan_replace(
    self,
    definition: PlanDefinition,
) -> PlanDefinition:
    """
    Replace an existing plan definition.

    Replacement is explicit and deterministic.
    """

    self._validate_definition(
        definition
    )

    plan_id = self._normalize_plan_id(
        definition.plan_id
    )

    if plan_id not in self._plans:
        raise PlanNotFoundError(
            f"Cannot replace unknown plan: {plan_id}"
        )

    self._plans[plan_id] = definition

    return definition


PlanRegistry.replace = _plan_replace


# ============================================================
# PLAN IDS
# ============================================================

def _plan_ids(
    self,
) -> Tuple[str, ...]:
    """
    Return all registered plan IDs.
    """

    return tuple(
        sorted(
            self._plans.keys()
        )
    )


PlanRegistry.plan_ids = _plan_ids


# ============================================================
# ACTIVE PLANS
# ============================================================

def _active_plans(
    self,
) -> Tuple[PlanDefinition, ...]:
    """
    Return currently active plans.
    """

    return self.list_by_status(
        "active"
    )


PlanRegistry.active_plans = _active_plans


# ============================================================
# TIER INDEX
# ============================================================

def _tier_index(
    self,
):
    """
    Return:

        tier -> plan IDs
    """

    index = {}

    for plan in self.list_all():
        index.setdefault(
            plan.tier,
            []
        ).append(
            plan.plan_id
        )

    return {
        tier: tuple(
            sorted(plan_ids)
        )
        for tier, plan_ids
        in index.items()
    }


PlanRegistry.tier_index = _tier_index


# ============================================================
# STATUS INDEX
# ============================================================

def _status_index(
    self,
):
    """
    Return:

        status -> plan IDs
    """

    index = {}

    for plan in self.list_all():
        index.setdefault(
            plan.status,
            []
        ).append(
            plan.plan_id
        )

    return {
        status: tuple(
            sorted(plan_ids)
        )
        for status, plan_ids
        in index.items()
    }


PlanRegistry.status_index = _status_index


# ============================================================
# TAG INDEX
# ============================================================

def _tag_index(
    self,
):
    """
    Return:

        tag -> plan IDs
    """

    index = {}

    for plan in self.list_all():

        for tag in plan.tags:

            index.setdefault(
                tag,
                []
            ).append(
                plan.plan_id
            )

    return {
        tag: tuple(
            sorted(plan_ids)
        )
        for tag, plan_ids
        in index.items()
    }


PlanRegistry.tag_index = _tag_index


# ============================================================
# DOMAIN INDEX
# ============================================================

def _domain_index(
    self,
):
    """
    Return:

        domain -> plan IDs

    Domain is metadata only.
    """

    index = {}

    for plan in self.list_all():

        domain = plan.metadata.get(
            "domain"
        )

        if not domain:
            continue

        domain = str(
            domain
        ).strip().lower()

        index.setdefault(
            domain,
            []
        ).append(
            plan.plan_id
        )

    return {
        domain: tuple(
            sorted(plan_ids)
        )
        for domain, plan_ids
        in index.items()
    }


PlanRegistry.domain_index = _domain_index


# ============================================================
# PLAN DEPENDENCY EXTRACTION
# ============================================================

def _plan_dependencies(
    self,
    plan_id: str,
) -> Tuple[str, ...]:
    """
    Return dependencies declared in plan metadata.

    Dependency metadata is intentionally generic.

    Example:

        metadata={
            "depends_on": (
                "some_plan",
            )
        }

    The registry does not interpret commercial meaning.
    """

    plan = self.get(
        plan_id
    )

    dependencies = plan.metadata.get(
        "depends_on",
        (),
    )

    if dependencies is None:
        return ()

    if isinstance(
        dependencies,
        str,
    ):
        dependencies = (
            dependencies,
        )

    return tuple(
        str(dependency).strip()
        for dependency in dependencies
        if str(dependency).strip()
    )


# ============================================================
# DEPENDENTS
# ============================================================

def _plan_dependents(
    self,
    plan_id: str,
) -> Tuple[str, ...]:
    """
    Find plans that depend on the supplied plan.
    """

    plan_id = self._normalize_plan_id(
        plan_id
    )

    # Validate requested plan.
    self.get(
        plan_id
    )

    dependents = []

    for plan in self.list_all():

        dependencies = self._plan_dependencies(
            plan.plan_id
        )

        if plan_id in dependencies:
            dependents.append(
                plan.plan_id
            )

    return tuple(
        sorted(dependents)
    )


PlanRegistry.dependencies = _plan_dependencies
PlanRegistry.dependents = _plan_dependents


# ============================================================
# DEPENDENCY GRAPH
# ============================================================

def _plan_dependency_graph(
    self,
):
    """
    Return the complete plan dependency graph.

    Format:

        {
            "plan_a": ("plan_b",),
            "plan_b": (),
        }
    """

    return {
        plan.plan_id:
            self.dependencies(
                plan.plan_id
            )
        for plan in self.list_all()
    }


PlanRegistry.dependency_graph = _plan_dependency_graph


# ============================================================
# VALIDATE PLAN DEPENDENCIES
# ============================================================

def _plan_validate_dependencies(
    self,
    plan_id: str,
) -> bool:
    """
    Validate dependencies for one plan.
    """

    plan_id = self._normalize_plan_id(
        plan_id
    )

    self.get(
        plan_id
    )

    for dependency in self.dependencies(
        plan_id
    ):

        dependency = self._normalize_plan_id(
            dependency
        )

        if dependency == plan_id:
            raise PlanDependencyError(
                f"Plan '{plan_id}' cannot "
                "depend on itself."
            )

        if not self.exists(
            dependency
        ):
            raise PlanDependencyError(
                f"Plan '{plan_id}' depends on "
                f"missing plan '{dependency}'."
            )

    return True


# ============================================================
# VALIDATE ALL DEPENDENCIES
# ============================================================

def _plan_validate_all_dependencies(
    self,
) -> bool:
    """
    Validate dependencies for every registered plan.
    """

    for plan in self.list_all():
        self.validate_dependencies(
            plan.plan_id
        )

    return True


PlanRegistry.validate_dependencies = (
    _plan_validate_dependencies
)

PlanRegistry.validate_all_dependencies = (
    _plan_validate_all_dependencies
)


# ============================================================
# SUMMARY
# ============================================================

def _plan_summary(
    self,
):
    """
    Return deterministic registry summary.
    """

    status_counts = {
        status: len(
            self.list_by_status(
                status
            )
        )
        for status in VALID_PLAN_STATUSES
    }

    tier_counts = {}

    for plan in self.list_all():
        tier_counts[
            plan.tier
        ] = tier_counts.get(
            plan.tier,
            0,
        ) + 1

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "total_plans": self.count(),
        "active_plans": len(
            self.active_plans()
        ),
        "status_counts": status_counts,
        "tier_counts": tier_counts,
        "plan_ids": self.plan_ids(),
    }


PlanRegistry.summary = _plan_summary


# ============================================================
# HEALTH CHECK
# ============================================================

def _plan_health(
    self,
):
    """
    Lightweight health check for the Plan Registry.
    """

    errors = []

    for plan in self.list_all():

        try:
            self._validate_definition(
                plan
            )

        except Exception as exc:
            errors.append(
                f"{plan.plan_id}: {exc}"
            )

    try:
        self.validate_all_dependencies()

    except Exception as exc:
        errors.append(
            f"Dependency validation failed: {exc}"
        )

    return {
        "healthy": not errors,
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "plan_count": self.count(),
        "errors": tuple(errors),
    }


PlanRegistry.health = _plan_health
# ============================================================
# PLAN REGISTRY — PART 3
# Search / Bootstrap / Snapshot / Restore / Consistency
# ============================================================


# ============================================================
# PART 3 EXCEPTIONS
# ============================================================

class PlanBootstrapError(PlanRegistryError):
    """Raised when plan bootstrap cannot be completed."""


class PlanSnapshotError(PlanRegistryError):
    """Raised when plan snapshot handling fails."""


# ============================================================
# SEARCH
# ============================================================

def _plan_find(
    self,
    tier: Optional[str] = None,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    owner: Optional[str] = None,
):
    """
    Search registered plans using metadata fields.

    This performs lookup only.
    It does not perform authorization or entitlement decisions.
    """

    results = list(
        self._plans.values()
    )

    if tier is not None:
        tier = self._normalize_text(
            tier
        )

        results = [
            plan
            for plan in results
            if plan.tier == tier
        ]

    if status is not None:
        status = self._normalize_text(
            status
        )

        results = [
            plan
            for plan in results
            if plan.status == status
        ]

    if tag is not None:
        tag = self._normalize_text(
            tag
        )

        results = [
            plan
            for plan in results
            if tag in plan.tags
        ]

    if owner is not None:
        owner = self._normalize_text(
            owner
        )

        results = [
            plan
            for plan in results
            if self._normalize_text(
                plan.owner
            ) == owner
        ]

    return tuple(
        sorted(
            results,
            key=lambda item: item.plan_id,
        )
    )


def _plan_find_by_prefix(
    self,
    prefix: str,
):
    """
    Find plans whose IDs start with prefix.
    """

    prefix = self._normalize_plan_id(
        prefix
    )

    return tuple(
        plan
        for plan in self.list_all()
        if plan.plan_id.startswith(
            prefix
        )
    )


def _plan_find_by_tag(
    self,
    tag: str,
):
    return self.find(
        tag=tag
    )


def _plan_find_by_tier(
    self,
    tier: str,
):
    return self.find(
        tier=tier
    )


def _plan_find_by_status(
    self,
    status: str,
):
    return self.find(
        status=status
    )


PlanRegistry.find = _plan_find
PlanRegistry.find_by_prefix = _plan_find_by_prefix
PlanRegistry.find_by_tag = _plan_find_by_tag
PlanRegistry.find_by_tier = _plan_find_by_tier
PlanRegistry.find_by_status = _plan_find_by_status


# ============================================================
# BOOTSTRAP VALIDATION
# ============================================================

def _plan_validate_bootstrap(
    self,
    definitions: Iterable[PlanDefinition],
):
    """
    Validate a complete bootstrap batch before mutation.

    Dependencies may already exist in the registry or may
    be supplied inside the same bootstrap batch.
    """

    definitions = tuple(
        definitions
    )

    definition_map = {}

    for definition in definitions:

        self._validate_definition(
            definition
        )

        plan_id = self._normalize_plan_id(
            definition.plan_id
        )

        if plan_id in definition_map:
            raise PlanBootstrapError(
                "Duplicate plan ID in bootstrap: "
                f"{plan_id}"
            )

        definition_map[
            plan_id
        ] = definition

    available_ids = set(
        self._plans.keys()
    )

    available_ids.update(
        definition_map.keys()
    )

    for definition in definitions:

        dependencies = definition.metadata.get(
            "depends_on",
            (),
        )

        if dependencies is None:
            dependencies = ()

        if isinstance(
            dependencies,
            str,
        ):
            dependencies = (
                dependencies,
            )

        for dependency in dependencies:

            dependency = self._normalize_plan_id(
                dependency
            )

            if not dependency:
                continue

            if dependency not in available_ids:
                raise PlanDependencyError(
                    f"Plan '{definition.plan_id}' "
                    f"depends on missing plan "
                    f"'{dependency}'."
                )

    return True


PlanRegistry.validate_bootstrap = (
    _plan_validate_bootstrap
)


# ============================================================
# DEPENDENCY-RESOLVED BOOTSTRAP
# ============================================================

def _plan_bootstrap(
    self,
    definitions: Iterable[PlanDefinition],
):
    """
    Register plans in dependency-resolved order.

    Existing dependencies are allowed.

    Same-batch dependencies are registered before their
    dependent plans.
    """

    definitions = tuple(
        definitions
    )

    self.validate_bootstrap(
        definitions
    )

    definition_map = {
        self._normalize_plan_id(
            definition.plan_id
        ): definition
        for definition in definitions
    }

    pending = set(
        definition_map.keys()
    )

    registered_order = []

    while pending:

        progress = False

        for plan_id in tuple(
            sorted(pending)
        ):

            definition = definition_map[
                plan_id
            ]

            dependencies = definition.metadata.get(
                "depends_on",
                (),
            )

            if dependencies is None:
                dependencies = ()

            if isinstance(
                dependencies,
                str,
            ):
                dependencies = (
                    dependencies,
                )

            dependencies = {
                self._normalize_plan_id(
                    dependency
                )
                for dependency in dependencies
                if self._normalize_plan_id(
                    dependency
                )
            }

            unresolved = {
                dependency
                for dependency in dependencies
                if (
                    dependency in pending
                    or not self.exists(
                        dependency
                    )
                )
            }

            if unresolved:
                continue

            self.register_safe(
                definition
            )

            pending.remove(
                plan_id
            )

            registered_order.append(
                plan_id
            )

            progress = True

        if not progress:

            unresolved_map = {}

            for plan_id in sorted(
                pending
            ):

                definition = definition_map[
                    plan_id
                ]

                dependencies = definition.metadata.get(
                    "depends_on",
                    (),
                )

                if dependencies is None:
                    dependencies = ()

                if isinstance(
                    dependencies,
                    str,
                ):
                    dependencies = (
                        dependencies,
                    )

                unresolved_map[
                    plan_id
                ] = tuple(
                    dependency
                    for dependency in dependencies
                    if (
                        self._normalize_plan_id(
                            dependency
                        ) in pending
                        or not self.exists(
                            self._normalize_plan_id(
                                dependency
                            )
                        )
                    )
                )

            raise PlanBootstrapError(
                "Unable to resolve plan dependency graph: "
                f"{unresolved_map}"
            )

    self.validate_all_dependencies()

    return tuple(
        self.get(
            plan_id
        )
        for plan_id in registered_order
    )


PlanRegistry.bootstrap = _plan_bootstrap


# ============================================================
# SNAPSHOT
# ============================================================

def _plan_snapshot(
    self,
):
    """
    Create a serializable registry snapshot.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "plan_count": self.count(),
        "plans": [
            {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "version": plan.version,
                "description": plan.description,
                "status": plan.status,
                "owner": plan.owner,
                "tier": plan.tier,
                "metadata": dict(
                    plan.metadata
                ),
                "tags": tuple(
                    plan.tags
                ),
                "registered_at":
                    plan.registered_at.isoformat(),
            }
            for plan in self.list_all()
        ],
    }


PlanRegistry.snapshot = _plan_snapshot


# ============================================================
# SNAPSHOT RESTORE
# ============================================================

def _plan_restore_snapshot(
    self,
    snapshot: Dict[str, Any],
    replace_existing: bool = False,
):
    """
    Restore plans from a registry snapshot.

    By default existing registry state is preserved and
    duplicate IDs are rejected.
    """

    if not isinstance(
        snapshot,
        dict,
    ):
        raise PlanSnapshotError(
            "Snapshot must be a dictionary."
        )

    plans = snapshot.get(
        "plans"
    )

    if not isinstance(
        plans,
        list,
    ):
        raise PlanSnapshotError(
            "Snapshot does not contain a valid "
            "'plans' list."
        )

    definitions = []

    for item in plans:

        if not isinstance(
            item,
            dict,
        ):
            raise PlanSnapshotError(
                "Invalid plan snapshot entry."
            )

        item = dict(
            item
        )

        registered_at = item.get(
            "registered_at"
        )

        if isinstance(
            registered_at,
            str,
        ):
            try:
                item[
                    "registered_at"
                ] = datetime.fromisoformat(
                    registered_at
                )

            except ValueError as exc:
                raise PlanSnapshotError(
                    "Invalid registered_at timestamp "
                    f"for plan '{item.get('plan_id')}'."
                ) from exc

        try:
            definitions.append(
                PlanDefinition(
                    **item
                )
            )

        except TypeError as exc:
            raise PlanSnapshotError(
                "Invalid PlanDefinition in snapshot: "
                f"{item}"
            ) from exc

    if replace_existing:

        previous_state = dict(
            self._plans
        )

        try:
            self._plans.clear()

            return self.bootstrap(
                definitions
            )

        except Exception as exc:

            self._plans = previous_state

            raise PlanSnapshotError(
                "Snapshot restore failed. "
                "Previous registry state restored."
            ) from exc

    return self.bootstrap(
        definitions
    )


PlanRegistry.restore_snapshot = (
    _plan_restore_snapshot
)


# ============================================================
# METADATA EXPORT
# ============================================================

def _plan_export_metadata(
    self,
):
    """
    Export deterministic plan metadata.

    This is metadata export only.
    No billing or entitlement calculation is performed.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "plan_count": self.count(),
        "plans": [
            {
                "plan_id": plan.plan_id,
                "name": plan.name,
                "version": plan.version,
                "description": plan.description,
                "status": plan.status,
                "owner": plan.owner,
                "tier": plan.tier,
                "metadata": dict(
                    plan.metadata
                ),
                "tags": tuple(
                    plan.tags
                ),
                "registered_at":
                    plan.registered_at.isoformat(),
            }
            for plan in self.list_all()
        ],
    }


PlanRegistry.export_metadata = (
    _plan_export_metadata
)


# ============================================================
# CONSISTENCY CHECK
# ============================================================

def _plan_consistency_check(
    self,
):
    """
    Perform structural consistency validation.
    """

    errors = []
    warnings = []

    plans = self.list_all()

    # --------------------------------------------------------
    # ID uniqueness
    # --------------------------------------------------------

    ids = [
        plan.plan_id
        for plan in plans
    ]

    if len(ids) != len(
        set(ids)
    ):
        errors.append(
            "Duplicate plan IDs detected."
        )

    # --------------------------------------------------------
    # Definition validation
    # --------------------------------------------------------

    for plan in plans:

        try:
            self._validate_definition(
                plan
            )

        except Exception as exc:

            errors.append(
                f"{plan.plan_id}: "
                f"invalid definition: {exc}"
            )

    # --------------------------------------------------------
    # Dependency validation
    # --------------------------------------------------------

    try:

        self.validate_all_dependencies()

    except Exception as exc:

        errors.append(
            "Dependency validation failed: "
            f"{exc}"
        )

    # --------------------------------------------------------
    # Tier consistency
    # --------------------------------------------------------

    tier_map = {}

    for plan in plans:

        tier = self._normalize_text(
            plan.tier
        )

        if not tier:
            errors.append(
                f"{plan.plan_id}: empty tier."
            )
            continue

        tier_map.setdefault(
            tier,
            []
        ).append(
            plan.plan_id
        )

    # --------------------------------------------------------
    # Multiple plans within same tier
    # --------------------------------------------------------

    for tier, plan_ids in tier_map.items():

        if len(plan_ids) > 1:

            warnings.append(
                f"Multiple plans registered "
                f"under tier '{tier}': "
                f"{tuple(sorted(plan_ids))}"
            )

    # --------------------------------------------------------
    # Status consistency
    # --------------------------------------------------------

    for plan in plans:

        if plan.status not in (
            VALID_PLAN_STATUSES
        ):

            errors.append(
                f"{plan.plan_id}: "
                f"invalid status "
                f"'{plan.status}'."
            )

    return {
        "healthy": not errors,
        "plan_count": self.count(),
        "errors": tuple(errors),
        "warnings": tuple(warnings),
    }


PlanRegistry.consistency_check = (
    _plan_consistency_check
)


# ============================================================
# FULL AUDIT
# ============================================================

def _plan_full_audit(
    self,
):
    """
    Complete registry audit.
    """

    consistency = (
        self.consistency_check()
    )

    health = (
        self.health()
    )

    summary = (
        self.summary()
    )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "healthy": (
            consistency["healthy"]
            and health.get(
                "healthy",
                False,
            )
        ),
        "summary": summary,
        "health": health,
        "consistency": consistency,
    }


PlanRegistry.full_audit = (
    _plan_full_audit
)


# ============================================================
# ASSERT HEALTHY
# ============================================================

def _plan_assert_healthy(
    self,
):
    """
    Raise if registry health checks fail.
    """

    audit = self.full_audit()

    if not audit["healthy"]:

        raise PlanRegistryError(
            "Plan registry is unhealthy: "
            f"{audit}"
        )

    return True


PlanRegistry.assert_healthy = (
    _plan_assert_healthy
)


# ============================================================
# STATE
# ============================================================

def _plan_state(
    self,
):
    """
    Return current registry state.
    """

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "count": self.count(),
        "active": len(
            self.active_plans()
        ),
        "tiers": tuple(
            sorted(
                {
                    plan.tier
                    for plan in self.list_all()
                }
            )
        ),
        "statuses": tuple(
            sorted(
                {
                    plan.status
                    for plan in self.list_all()
                }
            )
        ),
        "plan_ids": self.plan_ids(),
        "healthy": self.health().get(
            "healthy",
            False,
        ),
    }


PlanRegistry.state = _plan_state
# ============================================================
# PLAN REGISTRY — PART 4
# Declarative Registration Specification + Discovery
# ============================================================

from dataclasses import dataclass, field


# ============================================================
# 4.1 — PLAN REGISTRATION SPECIFICATION
# ============================================================

@dataclass(frozen=True)
class PlanRegistrationSpec:
    """
    Declarative registration specification for a ROBOMLM plan.

    This layer defines WHAT a plan declares.

    It does NOT:
        - process payments
        - calculate billing
        - grant entitlements
        - authorize users
        - execute trades
        - make CAS decisions
        - enforce subscription rules
    """

    plan_id: str
    name: str
    version: str
    description: str = ""
    status: str = "registered"
    owner: str = ""
    tier: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Tuple[str, ...] = field(default_factory=tuple)

    def to_definition(self) -> PlanDefinition:
        """
        Convert declarative specification into immutable PlanDefinition.
        """

        return PlanDefinition(
            plan_id=self.plan_id,
            name=self.name,
            version=self.version,
            description=self.description,
            status=self.status,
            owner=self.owner,
            tier=self.tier,
            metadata=dict(self.metadata),
            tags=tuple(self.tags),
        )


# ============================================================
# 4.2 — SPEC VALIDATION
# ============================================================

def _validate_plan_spec(spec: PlanRegistrationSpec) -> None:
    """
    Validate a PlanRegistrationSpec using the same structural
    rules as PlanDefinition.
    """

    if not isinstance(spec, PlanRegistrationSpec):
        raise InvalidPlanDefinitionError(
            "Expected PlanRegistrationSpec"
        )

    definition = spec.to_definition()

    plan_registry._validate_definition(definition)


# ============================================================
# 4.3 — REGISTER SPEC
# ============================================================

def _plan_register_spec(
    self,
    spec: PlanRegistrationSpec,
) -> PlanDefinition:
    """
    Validate and register one declarative plan specification.
    """

    _validate_plan_spec(spec)

    definition = spec.to_definition()

    return self.register(definition)


PlanRegistry.register_spec = _plan_register_spec


# ============================================================
# 4.4 — REGISTER MULTIPLE SPECS
# ============================================================

def _plan_register_specs(
    self,
    specs: Iterable[PlanRegistrationSpec],
) -> Tuple[PlanDefinition, ...]:
    """
    Register multiple declarative specifications.

    Existing registry behavior is preserved.
    """

    specs = tuple(specs)

    for spec in specs:
        _validate_plan_spec(spec)

    definitions = tuple(
        spec.to_definition()
        for spec in specs
    )

    return self.register_many(definitions)


PlanRegistry.register_specs = _plan_register_specs


# ============================================================
# 4.5 — DECLARATIVE SPEC STORE
# ============================================================

_PLAN_REGISTRATION_SPECS: Dict[
    str,
    PlanRegistrationSpec,
] = {}


# ============================================================
# 4.6 — PLAN SPEC DECORATOR
# ============================================================

def plan_spec(
    plan_id: str,
    name: str,
    version: str,
    description: str = "",
    status: str = "registered",
    owner: str = "",
    tier: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    tags: Optional[Iterable[str]] = None,
):
    """
    Declarative decorator for registering a plan specification.

    The decorator does NOT install the plan into the active registry.

    It only records the specification for later discovery /
    controlled registration.
    """

    normalized_metadata = (
        dict(metadata)
        if metadata is not None
        else {}
    )

    normalized_tags = (
        tuple(tags)
        if tags is not None
        else tuple()
    )

    spec = PlanRegistrationSpec(
        plan_id=plan_id,
        name=name,
        version=version,
        description=description,
        status=status,
        owner=owner,
        tier=tier,
        metadata=normalized_metadata,
        tags=normalized_tags,
    )

    _validate_plan_spec(spec)

    def decorator(target):
        """
        Attach the specification to the decorated object and
        retain it in the central discovery store.
        """

        existing = _PLAN_REGISTRATION_SPECS.get(spec.plan_id)

        if existing is not None and existing != spec:
            raise PlanRegistrationConflictError(
                f"Conflicting plan specification: {spec.plan_id}"
            )

        _PLAN_REGISTRATION_SPECS[spec.plan_id] = spec

        setattr(
            target,
            "__robomlm_plan_spec__",
            spec,
        )

        return target

    return decorator


# ============================================================
# 4.7 — DISCOVER ALL PLAN SPECS
# ============================================================

def discover_plan_specs() -> Tuple[PlanRegistrationSpec, ...]:
    """
    Return all declaratively registered plan specifications.
    """

    return tuple(
        _PLAN_REGISTRATION_SPECS.values()
    )


# ============================================================
# 4.8 — GET ONE PLAN SPEC
# ============================================================

def get_plan_spec(
    plan_id: str,
) -> PlanRegistrationSpec:
    """
    Retrieve one discovered plan specification.
    """

    normalized_id = str(plan_id).strip()

    try:
        return _PLAN_REGISTRATION_SPECS[normalized_id]
    except KeyError as exc:
        raise PlanNotFoundError(
            f"Plan specification not found: {normalized_id}"
        ) from exc


# ============================================================
# 4.9 — REGISTER DISCOVERED SPECS
# ============================================================

def _plan_register_discovered(
    self,
    replace_existing: bool = False,
) -> Tuple[PlanDefinition, ...]:
    """
    Register all discovered plan specifications.

    Discovery and installation remain separate operations.
    """

    specs = discover_plan_specs()

    if not specs:
        return tuple()

    definitions = tuple(
        spec.to_definition()
        for spec in specs
    )

    if replace_existing:
        results = []

        for definition in definitions:
            if self.exists(definition.plan_id):
                self.replace(definition)
            else:
                self.register(definition)

            results.append(
                self.get(definition.plan_id)
            )

        return tuple(results)

    return self.register_many(definitions)


PlanRegistry.register_discovered = _plan_register_discovered


# ============================================================
# 4.10 — DISCOVERY REPORT
# ============================================================

def _plan_discovery_report(self) -> Dict[str, Any]:
    """
    Return a non-mutating discovery report.
    """

    specs = discover_plan_specs()

    discovered_ids = tuple(
        spec.plan_id
        for spec in specs
    )

    registered_ids = tuple(
        self.plan_ids()
    )

    missing_from_registry = tuple(
        plan_id
        for plan_id in discovered_ids
        if plan_id not in registered_ids
    )

    registered_without_spec = tuple(
        plan_id
        for plan_id in registered_ids
        if plan_id not in discovered_ids
    )

    conflicts = []

    for spec in specs:
        if self.exists(spec.plan_id):
            registered = self.get(spec.plan_id)

            if registered != spec.to_definition():
                conflicts.append(spec.plan_id)

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "discovered_count": len(specs),
        "registered_count": self.count(),
        "discovered_ids": discovered_ids,
        "missing_from_registry": missing_from_registry,
        "registered_without_spec": registered_without_spec,
        "conflicts": tuple(conflicts),
        "healthy": not (
            missing_from_registry
            or conflicts
        ),
    }


PlanRegistry.discovery_report = _plan_discovery_report


# ============================================================
# 4.11 — EXPORT DISCOVERED PLAN METADATA
# ============================================================

def export_discovered_plan_metadata() -> Tuple[Dict[str, Any], ...]:
    """
    Export discovered plan specifications as serializable metadata.

    No subscription or entitlement information is calculated here.
    """

    exported = []

    for spec in discover_plan_specs():
        exported.append(
            {
                "plan_id": spec.plan_id,
                "name": spec.name,
                "version": spec.version,
                "description": spec.description,
                "status": spec.status,
                "owner": spec.owner,
                "tier": spec.tier,
                "metadata": dict(spec.metadata),
                "tags": tuple(spec.tags),
            }
        )

    return tuple(exported)


# ============================================================
# 4.12 — SPEC CONSISTENCY CHECK
# ============================================================

def _plan_spec_consistency_check(self) -> Dict[str, Any]:
    """
    Compare discovered specifications with active registry
    definitions.
    """

    issues = []

    for spec in discover_plan_specs():

        try:
            _validate_plan_spec(spec)
        except Exception as exc:
            issues.append(
                {
                    "plan_id": spec.plan_id,
                    "issue": "invalid_spec",
                    "detail": str(exc),
                }
            )
            continue

        if self.exists(spec.plan_id):
            registered = self.get(spec.plan_id)

            if registered != spec.to_definition():
                issues.append(
                    {
                        "plan_id": spec.plan_id,
                        "issue": "definition_mismatch",
                    }
                )

    return {
        "checked_specs": len(
            discover_plan_specs()
        ),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


PlanRegistry.spec_consistency_check = (
    _plan_spec_consistency_check
)


# ============================================================
# 4.13 — DISCOVERY AUDIT
# ============================================================

def _plan_discovery_audit(self) -> Dict[str, Any]:
    """
    Full non-mutating discovery audit.
    """

    report = self.discovery_report()
    consistency = self.spec_consistency_check()

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


PlanRegistry.discovery_audit = _plan_discovery_audit


# ============================================================
# 4.14 — ASSERT DISCOVERY HEALTH
# ============================================================

def _plan_assert_discovery_healthy(self) -> bool:
    """
    Raise PlanRegistryError if discovery state is unhealthy.
    """

    audit = self.discovery_audit()

    if not audit["healthy"]:
        raise PlanRegistryError(
            f"Plan discovery audit failed: {audit}"
        )

    return True


PlanRegistry.assert_discovery_healthy = (
    _plan_assert_discovery_healthy
)


# ============================================================
# END OF PLAN REGISTRY — PART 4
# ============================================================
# ============================================================
# PLAN REGISTRY — PART 5
# Canonical ROBOMLM Plans + Atomic Installation + Freeze
# ============================================================

from copy import deepcopy


# ============================================================
# 5.1 — PART 5 EXCEPTIONS
# ============================================================

class PlanRegistryFrozenError(PlanRegistryError):
    """Raised when a mutation is attempted on a frozen registry."""


class PlanAuditError(PlanRegistryError):
    """Raised when plan registry audit fails."""


class PlanAtomicInstallError(PlanRegistryError):
    """Raised when atomic plan installation fails."""


# ============================================================
# 5.2 — FREEZE CONTROL
# ============================================================

PlanRegistry._frozen = False


def _plan_assert_mutable(self) -> bool:
    """
    Ensure registry is mutable before a mutation.
    """

    if getattr(self, "_frozen", False):
        raise PlanRegistryFrozenError(
            "Plan registry is frozen and cannot be mutated."
        )

    return True


def _plan_freeze(self) -> bool:
    """
    Freeze the registry against structural mutations.
    """

    self._frozen = True
    return True


def _plan_unfreeze(self) -> bool:
    """
    Unfreeze the registry.
    """

    self._frozen = False
    return True


PlanRegistry.assert_mutable = _plan_assert_mutable
PlanRegistry.freeze = _plan_freeze
PlanRegistry.unfreeze = _plan_unfreeze


# ============================================================
# 5.3 — MUTATION GUARDS
# ============================================================

_plan_original_register = PlanRegistry.register
_plan_original_replace = PlanRegistry.replace
_plan_original_unregister = PlanRegistry.unregister
_plan_original_set_status = PlanRegistry.set_status


def _guarded_plan_register(self, definition):
    self.assert_mutable()
    return _plan_original_register(self, definition)


def _guarded_plan_replace(self, definition):
    self.assert_mutable()
    return _plan_original_replace(self, definition)


def _guarded_plan_unregister(
    self,
    plan_id: str,
    force: bool = False,
):
    self.assert_mutable()
    return _plan_original_unregister(
        self,
        plan_id,
        force=force,
    )


def _guarded_plan_set_status(
    self,
    plan_id: str,
    status: str,
):
    self.assert_mutable()
    return _plan_original_set_status(
        self,
        plan_id,
        status,
    )


PlanRegistry.register = _guarded_plan_register
PlanRegistry.replace = _guarded_plan_replace
PlanRegistry.unregister = _guarded_plan_unregister
PlanRegistry.set_status = _guarded_plan_set_status


# ============================================================
# 5.4 — CLONE
# ============================================================

def _plan_clone(self):
    """
    Create an independent registry clone.
    """

    clone = PlanRegistry()

    clone._plans = deepcopy(self._plans)
    clone._frozen = getattr(
        self,
        "_frozen",
        False,
    )

    return clone


PlanRegistry.clone = _plan_clone


# ============================================================
# 5.5 — ATOMIC SINGLE INSTALL
# ============================================================

def _plan_atomic_register(
    self,
    definition: PlanDefinition,
) -> PlanDefinition:
    """
    Register one plan atomically.

    On failure, original registry state is restored.
    """

    self.assert_mutable()

    previous = deepcopy(self._plans)

    try:
        result = self.register(definition)

        return result

    except Exception as exc:
        self._plans = previous

        raise PlanAtomicInstallError(
            f"Atomic plan registration failed: "
            f"{definition.plan_id}"
        ) from exc


PlanRegistry.atomic_register = _plan_atomic_register


# ============================================================
# 5.6 — ATOMIC MULTI-PLAN INSTALL
# ============================================================

def _plan_atomic_register_specs(
    self,
    specs: Iterable[PlanRegistrationSpec],
) -> Tuple[PlanDefinition, ...]:
    """
    Register multiple plan specifications atomically.

    If any plan fails, the complete operation is rolled back.
    """

    self.assert_mutable()

    specs = tuple(specs)

    previous = deepcopy(self._plans)

    try:
        definitions = tuple(
            spec.to_definition()
            for spec in specs
        )

        self._plan_validate_bootstrap(
            definitions
        )

        results = self.bootstrap(
            definitions
        )

        return tuple(results)

    except Exception as exc:
        self._plans = previous

        raise PlanAtomicInstallError(
            "Atomic multi-plan installation failed."
        ) from exc


PlanRegistry.atomic_register_specs = (
    _plan_atomic_register_specs
)


# ============================================================
# 5.7 — CANONICAL ROBOMLM DOMAINS
# ============================================================

PLAN_DOMAIN_PRODUCT = "product"
PLAN_DOMAIN_AUTOMATION = "automation"


# ============================================================
# 5.8 — CANONICAL ROBOMLM PLAN BUILDER
# ============================================================

def _canonical_plan(
    plan_id: str,
    name: str,
    tier: str,
    description: str,
    *,
    status: str = "active",
    owner: str = "ROBOMLM",
    tags: Iterable[str] = (),
    metadata: Optional[Dict[str, Any]] = None,
) -> PlanRegistrationSpec:
    """
    Build a canonical plan specification.

    This function only defines plan metadata.
    It does not define entitlement or authorization rules.
    """

    plan_metadata = {
        "domain": PLAN_DOMAIN_PRODUCT,
        "canonical": True,
    }

    if metadata:
        plan_metadata.update(
            dict(metadata)
        )

    return PlanRegistrationSpec(
        plan_id=plan_id,
        name=name,
        version="1.0.0",
        description=description,
        status=status,
        owner=owner,
        tier=tier,
        metadata=plan_metadata,
        tags=tuple(tags),
    )


# ============================================================
# 5.9 — CANONICAL ROBOMLM PLAN CATALOG
# ============================================================

ROBOMLM_CANONICAL_PLAN_SPECS = (
    _canonical_plan(
        plan_id="free",
        name="ROBOMLM Free",
        tier="free",
        description=(
            "Entry-level ROBOMLM market intelligence "
            "product plan."
        ),
        tags=(
            "canonical",
            "product",
            "free",
        ),
    ),

    _canonical_plan(
        plan_id="pro",
        name="ROBOMLM Pro",
        tier="pro",
        description=(
            "Professional ROBOMLM market intelligence "
            "product plan."
        ),
        tags=(
            "canonical",
            "product",
            "pro",
        ),
    ),

    _canonical_plan(
        plan_id="elite",
        name="ROBOMLM Elite",
        tier="elite",
        description=(
            "Advanced ROBOMLM market intelligence "
            "product plan."
        ),
        tags=(
            "canonical",
            "product",
            "elite",
        ),
    ),

    _canonical_plan(
        plan_id="auto",
        name="ROBOMLM Auto",
        tier="auto",
        description=(
            "ROBOMLM plan supporting gated "
            "automation capabilities."
        ),
        tags=(
            "canonical",
            "product",
            "automation",
            "auto",
        ),
        metadata={
            "domain": PLAN_DOMAIN_AUTOMATION,
        },
    ),
)


# ============================================================
# 5.10 — CANONICAL CATALOG VALIDATION
# ============================================================

def validate_canonical_plan_catalog() -> Dict[str, Any]:
    """
    Validate the canonical ROBOMLM plan catalog.
    """

    issues = []
    seen_ids = set()

    for spec in ROBOMLM_CANONICAL_PLAN_SPECS:

        if spec.plan_id in seen_ids:
            issues.append(
                {
                    "plan_id": spec.plan_id,
                    "issue": "duplicate_plan_id",
                }
            )

        seen_ids.add(spec.plan_id)

        try:
            _validate_plan_spec(spec)
        except Exception as exc:
            issues.append(
                {
                    "plan_id": spec.plan_id,
                    "issue": "invalid_definition",
                    "detail": str(exc),
                }
            )

        if not spec.metadata.get(
            "canonical",
            False,
        ):
            issues.append(
                {
                    "plan_id": spec.plan_id,
                    "issue": "missing_canonical_marker",
                }
            )

        if not spec.tier.strip():
            issues.append(
                {
                    "plan_id": spec.plan_id,
                    "issue": "missing_tier",
                }
            )

    return {
        "catalog": "ROBOMLM_CANONICAL_PLAN_SPECS",
        "count": len(
            ROBOMLM_CANONICAL_PLAN_SPECS
        ),
        "plan_ids": tuple(
            spec.plan_id
            for spec in ROBOMLM_CANONICAL_PLAN_SPECS
        ),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


# ============================================================
# 5.11 — REGISTER CANONICAL PLANS
# ============================================================

def _plan_register_canonical(
    self,
    replace_existing: bool = False,
) -> Tuple[PlanDefinition, ...]:
    """
    Install the canonical ROBOMLM plan catalog.
    """

    catalog_audit = (
        validate_canonical_plan_catalog()
    )

    if not catalog_audit["healthy"]:
        raise PlanAtomicInstallError(
            f"Canonical plan catalog is invalid: "
            f"{catalog_audit}"
        )

    self.assert_mutable()

    previous = deepcopy(self._plans)

    try:

        results = []

        for spec in ROBOMLM_CANONICAL_PLAN_SPECS:

            definition = spec.to_definition()

            if self.exists(
                definition.plan_id
            ):
                if not replace_existing:
                    raise PlanAlreadyRegisteredError(
                        f"Canonical plan already exists: "
                        f"{definition.plan_id}"
                    )

                self.replace(
                    definition
                )

            else:
                self.register(
                    definition
                )

            results.append(
                self.get(
                    definition.plan_id
                )
            )

        return tuple(results)

    except Exception as exc:

        self._plans = previous

        raise PlanAtomicInstallError(
            "Canonical ROBOMLM plan installation failed."
        ) from exc


PlanRegistry.register_canonical = (
    _plan_register_canonical
)


# ============================================================
# 5.12 — CANONICAL PLAN IDS
# ============================================================

def canonical_plan_ids() -> Tuple[str, ...]:
    """
    Return canonical ROBOMLM plan identifiers.
    """

    return tuple(
        spec.plan_id
        for spec in ROBOMLM_CANONICAL_PLAN_SPECS
    )


# ============================================================
# 5.13 — CANONICAL PLAN LOOKUP
# ============================================================

def canonical_plan_spec(
    plan_id: str,
) -> PlanRegistrationSpec:
    """
    Return one canonical plan specification.
    """

    normalized_id = str(
        plan_id
    ).strip()

    for spec in ROBOMLM_CANONICAL_PLAN_SPECS:

        if spec.plan_id == normalized_id:
            return spec

    raise PlanNotFoundError(
        f"Canonical plan not found: "
        f"{normalized_id}"
    )


# ============================================================
# 5.14 — CANONICAL TIER REPORT
# ============================================================

def canonical_plan_tier_report() -> Dict[str, str]:
    """
    Return canonical plan -> tier mapping.

    This is classification metadata only.
    """

    return {
        spec.plan_id: spec.tier
        for spec in ROBOMLM_CANONICAL_PLAN_SPECS
    }


# ============================================================
# 5.15 — CANONICAL PLAN AUDIT
# ============================================================

def _plan_audit_canonical(
    self,
) -> Dict[str, Any]:
    """
    Audit canonical catalog against the active registry.
    """

    catalog_audit = (
        validate_canonical_plan_catalog()
    )

    missing = []
    mismatched = []

    for spec in ROBOMLM_CANONICAL_PLAN_SPECS:

        if not self.exists(spec.plan_id):
            missing.append(
                spec.plan_id
            )
            continue

        registered = self.get(
            spec.plan_id
        )

        if registered != spec.to_definition():
            mismatched.append(
                spec.plan_id
            )

    return {
        "catalog": catalog_audit,
        "missing": tuple(missing),
        "mismatched": tuple(mismatched),
        "healthy": (
            catalog_audit["healthy"]
            and not missing
            and not mismatched
        ),
    }


PlanRegistry.audit_canonical = (
    _plan_audit_canonical
)


# ============================================================
# 5.16 — DEPENDENCY AUDIT
# ============================================================

def _plan_dependency_audit(
    self,
) -> Dict[str, Any]:
    """
    Audit all declared plan dependencies.
    """

    issues = []

    try:
        self.validate_all_dependencies()
    except Exception as exc:
        issues.append(
            {
                "issue": "dependency_validation_failed",
                "detail": str(exc),
            }
        )

    graph = self.dependency_graph()

    return {
        "dependency_graph": graph,
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


PlanRegistry.dependency_audit = (
    _plan_dependency_audit
)


# ============================================================
# 5.17 — STATUS AUDIT
# ============================================================

def _plan_status_audit(
    self,
) -> Dict[str, Any]:
    """
    Audit lifecycle status of every registered plan.
    """

    issues = []

    for plan in self.list_all():

        if plan.status not in VALID_PLAN_STATUSES:
            issues.append(
                {
                    "plan_id": plan.plan_id,
                    "issue": "invalid_status",
                    "status": plan.status,
                }
            )

        if not plan.tier.strip():
            issues.append(
                {
                    "plan_id": plan.plan_id,
                    "issue": "missing_tier",
                }
            )

    return {
        "checked": self.count(),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


PlanRegistry.status_audit = (
    _plan_status_audit
)


# ============================================================
# 5.18 — DEFINITION AUDIT
# ============================================================

def _plan_definition_audit(
    self,
) -> Dict[str, Any]:
    """
    Validate every registered PlanDefinition.
    """

    issues = []

    for plan in self.list_all():

        try:
            self._validate_definition(
                plan
            )
        except Exception as exc:
            issues.append(
                {
                    "plan_id": plan.plan_id,
                    "issue": "invalid_definition",
                    "detail": str(exc),
                }
            )

    return {
        "checked": self.count(),
        "issue_count": len(issues),
        "issues": tuple(issues),
        "healthy": not issues,
    }


PlanRegistry.definition_audit = (
    _plan_definition_audit
)


# ============================================================
# 5.19 — FULL REGISTRY AUDIT
# ============================================================

def _plan_full_registry_audit(
    self,
) -> Dict[str, Any]:
    """
    Complete non-mutating registry audit.
    """

    definition = self.definition_audit()
    status = self.status_audit()
    dependency = self.dependency_audit()
    canonical = self.audit_canonical()

    try:
        discovery = self.discovery_audit()
    except Exception as exc:
        discovery = {
            "healthy": False,
            "error": str(exc),
        }

    healthy = all(
        section.get(
            "healthy",
            False,
        )
        for section in (
            definition,
            status,
            dependency,
            canonical,
            discovery,
        )
    )

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "frozen": getattr(
            self,
            "_frozen",
            False,
        ),
        "definition": definition,
        "status": status,
        "dependency": dependency,
        "canonical": canonical,
        "discovery": discovery,
        "healthy": healthy,
    }


PlanRegistry.full_registry_audit = (
    _plan_full_registry_audit
)


# ============================================================
# 5.20 — ASSERT FULL HEALTH
# ============================================================

def _plan_assert_full_health(
    self,
) -> bool:
    """
    Raise PlanAuditError if complete registry audit fails.
    """

    audit = self.full_registry_audit()

    if not audit["healthy"]:
        raise PlanAuditError(
            f"Plan registry health check failed: "
            f"{audit}"
        )

    return True


PlanRegistry.assert_full_health = (
    _plan_assert_full_health
)


# ============================================================
# 5.21 — FREEZE ONLY WHEN HEALTHY
# ============================================================

def _plan_freeze_if_healthy(
    self,
) -> bool:
    """
    Audit first, then freeze.

    A failed audit prevents the registry from entering
    final frozen state.
    """

    self.assert_full_health()

    self.freeze()

    return True


PlanRegistry.freeze_if_healthy = (
    _plan_freeze_if_healthy
)


# ============================================================
# 5.22 — FINAL EXPORT
# ============================================================

def _plan_final_export(
    self,
) -> Dict[str, Any]:
    """
    Export final registry state and audit information.
    """

    audit = self.full_registry_audit()

    return {
        "registry_name": REGISTRY_NAME,
        "registry_version": REGISTRY_VERSION,
        "frozen": getattr(
            self,
            "_frozen",
            False,
        ),
        "plan_count": self.count(),
        "plans": self.export_metadata(),
        "canonical_plan_ids": canonical_plan_ids(),
        "audit": audit,
    }


PlanRegistry.final_export = (
    _plan_final_export
)


# ============================================================
# 5.23 — INSTALL COMPLETE PLAN REGISTRY
# ============================================================

def install_plan_registry(
    *,
    include_discovered: bool = True,
    freeze_after_install: bool = False,
) -> Dict[str, Any]:
    """
    Install the canonical ROBOMLM plan registry.

    Installation sequence:

        1. Validate canonical catalog
        2. Install canonical plans
        3. Optionally install discovered specifications
        4. Run complete audit
        5. Optionally freeze

    The complete installation is atomic.
    """

    catalog_audit = (
        validate_canonical_plan_catalog()
    )

    if not catalog_audit["healthy"]:
        raise PlanAtomicInstallError(
            f"Canonical catalog validation failed: "
            f"{catalog_audit}"
        )

    plan_registry.assert_mutable()

    previous = deepcopy(
        plan_registry._plans
    )

    try:

        # ----------------------------------------------------
        # Canonical plans
        # ----------------------------------------------------

        plan_registry.register_canonical(
            replace_existing=False
        )

        # ----------------------------------------------------
        # Discovered plans
        # ----------------------------------------------------

        if include_discovered:

            discovered = (
                discover_plan_specs()
            )

            if discovered:

                canonical_ids = set(
                    canonical_plan_ids()
                )

                external_specs = tuple(
                    spec
                    for spec in discovered
                    if spec.plan_id
                    not in canonical_ids
                )

                if external_specs:
                    plan_registry.atomic_register_specs(
                        external_specs
                    )

        # ----------------------------------------------------
        # Complete audit
        # ----------------------------------------------------

        audit = (
            plan_registry.full_registry_audit()
        )

        if not audit["healthy"]:
            raise PlanAtomicInstallError(
                f"Post-install plan audit failed: "
                f"{audit}"
            )

        # ----------------------------------------------------
        # Optional final freeze
        # ----------------------------------------------------

        if freeze_after_install:
            plan_registry.freeze()

        return plan_registry.final_export()

    except Exception as exc:

        plan_registry._plans = previous

        raise PlanAtomicInstallError(
            "Complete plan registry installation failed."
        ) from exc


# ============================================================
# 5.24 — TEST RESET
# ============================================================

def reset_plan_registry_for_testing() -> None:
    """
    Reset registry state for controlled tests.

    This function is explicitly intended for testing /
    development environments.
    """

    plan_registry._frozen = False
    plan_registry._plans.clear()


# ============================================================
# 5.25 — CANONICAL PLAN SUMMARY
# ============================================================

def canonical_plan_summary() -> Dict[str, Any]:
    """
    Non-mutating summary of the canonical plan catalog.
    """

    return {
        "count": len(
            ROBOMLM_CANONICAL_PLAN_SPECS
        ),
        "plans": tuple(
            {
                "plan_id": spec.plan_id,
                "name": spec.name,
                "tier": spec.tier,
                "version": spec.version,
                "status": spec.status,
            }
            for spec in ROBOMLM_CANONICAL_PLAN_SPECS
        ),
    }


# ============================================================
# END OF PLAN REGISTRY — PART 5
# ============================================================