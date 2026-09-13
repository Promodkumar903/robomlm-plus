from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class DeploymentRecord:
    """
    Immutable record describing a ROBOMLM deployment state.
    """

    deployment_id: str
    target: str
    version: str
    status: str

    environment: str | None = None
    deployed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "deployment_id": self.deployment_id,
            "target": self.target,
            "version": self.version,
            "status": self.status,
            "environment": self.environment,
            "deployed_at": self.deployed_at.isoformat(),
            "metadata": dict(self.metadata),
        }

    def is_active(self) -> bool:
        return self.status.upper() in {
            "ACTIVE",
            "DEPLOYED",
            "RUNNING",
        }

    def is_valid(self) -> bool:
        if not self.deployment_id:
            return False

        if not self.target:
            return False

        if not self.version:
            return False

        if not self.status:
            return False

        return True


class DeploymentAdmin:
    """
    Administrative boundary for deployment lifecycle operations.

    This class records and validates deployment state.
    Actual infrastructure-specific deployment is intentionally
    delegated to the deployment adapter/runtime layer.
    """

    def __init__(
        self,
        *,
        environment: str = "UNKNOWN",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.environment = environment
        self._metadata: dict[str, Any] = dict(metadata or {})
        self._deployment_counter = 0
        self._current_deployment: DeploymentRecord | None = None

    @property
    def current_deployment(self) -> DeploymentRecord | None:
        return self._current_deployment

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def _next_deployment_id(self) -> str:
        self._deployment_counter += 1

        return f"DEPLOY-{self._deployment_counter:06d}"

    def prepare_deployment(
        self,
        *,
        target: str,
        version: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> DeploymentRecord:
        """
        Prepare a deployment record without performing infrastructure
        changes.
        """

        if not target or not target.strip():
            raise ValueError("target must not be empty")

        if not version or not version.strip():
            raise ValueError("version must not be empty")

        deployment_metadata = dict(self._metadata)
        deployment_metadata.update(metadata or {})

        return DeploymentRecord(
            deployment_id=self._next_deployment_id(),
            target=target.strip(),
            version=version.strip(),
            status="PREPARED",
            environment=self.environment,
            metadata=deployment_metadata,
        )

    def activate_deployment(
        self,
        deployment: DeploymentRecord,
    ) -> DeploymentRecord:
        """
        Mark a prepared deployment as active.

        Infrastructure execution remains outside this administrative
        state-management class.
        """

        if not isinstance(deployment, DeploymentRecord):
            raise TypeError(
                "deployment must be a DeploymentRecord"
            )

        if not deployment.is_valid():
            raise ValueError("invalid deployment record")

        activated = DeploymentRecord(
            deployment_id=deployment.deployment_id,
            target=deployment.target,
            version=deployment.version,
            status="ACTIVE",
            environment=deployment.environment,
            deployed_at=datetime.now(timezone.utc),
            metadata=dict(deployment.metadata),
        )

        self._current_deployment = activated

        return activated

    def deactivate_deployment(
        self,
        deployment: DeploymentRecord | None = None,
    ) -> DeploymentRecord | None:
        """
        Mark the selected/current deployment as inactive.
        """

        selected = deployment or self._current_deployment

        if selected is None:
            return None

        if not isinstance(selected, DeploymentRecord):
            raise TypeError(
                "deployment must be a DeploymentRecord"
            )

        deactivated = DeploymentRecord(
            deployment_id=selected.deployment_id,
            target=selected.target,
            version=selected.version,
            status="INACTIVE",
            environment=selected.environment,
            deployed_at=selected.deployed_at,
            metadata=dict(selected.metadata),
        )

        if (
            self._current_deployment is not None
            and self._current_deployment.deployment_id
            == selected.deployment_id
        ):
            self._current_deployment = deactivated

        return deactivated

    def rollback_state(
        self,
        *,
        target: str,
        version: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> DeploymentRecord:
        """
        Create a deployment record representing a rollback target.

        No infrastructure rollback is executed here.
        """

        if not target or not target.strip():
            raise ValueError("target must not be empty")

        if not version or not version.strip():
            raise ValueError("version must not be empty")

        rollback_metadata = dict(self._metadata)
        rollback_metadata.update(metadata or {})
        rollback_metadata["operation"] = "ROLLBACK"

        return DeploymentRecord(
            deployment_id=self._next_deployment_id(),
            target=target.strip(),
            version=version.strip(),
            status="ROLLBACK_PENDING",
            environment=self.environment,
            metadata=rollback_metadata,
        )

    def status(self) -> dict[str, Any]:
        """
        Return the current deployment administration state.
        """

        return {
            "environment": self.environment,
            "deployment_count": self._deployment_counter,
            "current_deployment": (
                self._current_deployment.to_dict()
                if self._current_deployment is not None
                else None
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": dict(self._metadata),
        }