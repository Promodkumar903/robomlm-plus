from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class ExecutionResult:
    """
    Canonical result produced by the execution layer.

    This schema records what happened after an authorized execution
    action was processed. It does not itself perform execution.
    """

    execution_id: str
    action_id: str
    status: str

    instrument_id: str | None = None
    account_id: str | None = None

    requested_quantity: float | None = None
    executed_quantity: float | None = None

    requested_price: float | None = None
    executed_price: float | None = None

    order_id: str | None = None
    venue: str | None = None

    error_code: str | None = None
    error_message: str | None = None

    execution_time: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["execution_time"] = self.execution_time.isoformat()
        data["metadata"] = dict(self.metadata)
        return data

    def is_successful(self) -> bool:
        """Return whether execution completed successfully."""
        return self.status.lower() in {
            "success",
            "successful",
            "executed",
            "filled",
            "complete",
            "completed",
        }

    def is_failed(self) -> bool:
        """Return whether execution failed."""
        return self.status.lower() in {
            "failed",
            "failure",
            "error",
            "rejected",
            "cancelled",
            "canceled",
        }

    def is_valid(self) -> bool:
        """Return whether the execution result is structurally valid."""
        if not self.execution_id:
            return False

        if not self.action_id:
            return False

        if not self.status:
            return False

        if self.requested_quantity is not None:
            if self.requested_quantity < 0:
                return False

        if self.executed_quantity is not None:
            if self.executed_quantity < 0:
                return False

        if self.requested_price is not None:
            if self.requested_price < 0:
                return False

        if self.executed_price is not None:
            if self.executed_price < 0:
                return False

        return True