from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True)
class RequestContext:
    """
    Canonical execution context carried across ROBOMLM processing stages.
    """

    request_id: str
    source: str

    user_id: str | None = None
    session_id: str | None = None

    market: str | None = None
    instrument_id: str | None = None
    contract_id: str | None = None

    operating_mode: str | None = None
    use_case: str | None = None

    correlation_id: str | None = None

    requested_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)

        data["requested_at"] = self.requested_at.isoformat()
        data["metadata"] = dict(self.metadata)

        return data

    def is_valid(self) -> bool:
        if not self.request_id:
            return False

        if not self.source:
            return False

        if self.requested_at.tzinfo is None:
            return False

        return True

    def with_metadata(
        self,
        **metadata: Any,
    ) -> "RequestContext":
        updated_metadata = dict(self.metadata)
        updated_metadata.update(metadata)

        return RequestContext(
            request_id=self.request_id,
            source=self.source,
            user_id=self.user_id,
            session_id=self.session_id,
            market=self.market,
            instrument_id=self.instrument_id,
            contract_id=self.contract_id,
            operating_mode=self.operating_mode,
            use_case=self.use_case,
            correlation_id=self.correlation_id,
            requested_at=self.requested_at,
            metadata=updated_metadata,
        )