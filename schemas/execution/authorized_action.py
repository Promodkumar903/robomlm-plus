from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class AuthorizedAction:
    """
    Canonical authorization record for an execution action.

    This schema describes whether an action is authorized.
    It does not perform the action itself.
    """

    action_id: str
    action_type: str

    authorized: bool = False
    authorization_source: str | None = None

    actor_id: str | None = None
    account_id: str | None = None

    market: str | None = None
    instrument_id: str | None = None

    reason: str | None = None
    constraints: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    authorized_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary representation."""
        data = asdict(self)
        data["authorized_at"] = self.authorized_at.isoformat()
        data["constraints"] = dict(self.constraints)
        data["metadata"] = dict(self.metadata)
        return data

    def is_valid(self) -> bool:
        """Return whether the authorization record is structurally valid."""
        if not self.action_id:
            return False

        if not self.action_type:
            return False

        if self.authorized and not self.authorization_source:
            return False

        return True