from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


def generate_id(prefix: str) -> str:
    """
    Generate a stable application identifier with a semantic prefix.
    """
    clean_prefix = str(prefix).strip().upper()

    if not clean_prefix:
        clean_prefix = "ID"

    return f"{clean_prefix}-{uuid4().hex}"


@dataclass(frozen=True)
class IdentifierSet:
    """
    Canonical identifiers used to maintain entity lineage across ROBOMLM.
    """

    event_id: str | None = None
    request_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    account_id: str | None = None

    market_id: str | None = None
    instrument_id: str | None = None
    contract_id: str | None = None

    evidence_id: str | None = None
    intelligence_id: str | None = None
    decision_id: str | None = None
    action_id: str | None = None
    execution_id: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "event_id": self.event_id,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "account_id": self.account_id,
            "market_id": self.market_id,
            "instrument_id": self.instrument_id,
            "contract_id": self.contract_id,
            "evidence_id": self.evidence_id,
            "intelligence_id": self.intelligence_id,
            "decision_id": self.decision_id,
            "action_id": self.action_id,
            "execution_id": self.execution_id,
        }

    def is_valid(self) -> bool:
        """
        Validate identifiers without requiring every field to be populated.

        Different ROBOMLM lifecycle objects legitimately use different
        subsets of the identifier set.
        """
        values = self.to_dict().values()

        return all(
            value is None or bool(str(value).strip())
            for value in values
        )


def ensure_id(value: str | None, prefix: str) -> str:
    """
    Return an existing non-empty identifier or generate a new one.
    """
    if value is not None and str(value).strip():
        return str(value).strip()

    return generate_id(prefix)