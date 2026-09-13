"""
ROBOMLM PLUS
Decision Database Model

Purpose:
    Define the persistent structure for ROBOMLM decision records.

Design:
    - Stores decision identity, context, evidence, confidence,
      risk and lifecycle state.
    - Keeps decision data separate from decision-generation logic.
    - No broker/exchange interaction.
    - No order execution.
    - Persistence is handled by repository/database layers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Optional
from uuid import uuid4


@dataclass
class DecisionRecord:
    """Structured ROBOMLM decision record."""

    decision_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    decision_type: str = ""
    decision_state: str = ""
    verdict: str = ""

    market: Optional[str] = None
    instrument: Optional[str] = None
    venue: Optional[str] = None

    mode: Optional[str] = None
    timeframe: Optional[str] = None

    direction: Optional[str] = None

    confidence: Optional[float] = None
    score: Optional[float] = None

    evidence_ids: list[str] = field(default_factory=list)

    risk_level: Optional[str] = None
    risk_score: Optional[float] = None

    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        """Normalize and validate model values."""

        self.decision_id = str(self.decision_id).strip()

        if not self.decision_id:
            raise ValueError("decision_id cannot be empty.")

        self.decision_type = str(self.decision_type).strip()
        self.decision_state = str(self.decision_state).strip()
        self.verdict = str(self.verdict).strip()

        if self.market is not None:
            self.market = str(self.market).strip() or None

        if self.instrument is not None:
            self.instrument = str(self.instrument).strip() or None

        if self.venue is not None:
            self.venue = str(self.venue).strip() or None

        if self.mode is not None:
            self.mode = str(self.mode).strip() or None

        if self.timeframe is not None:
            self.timeframe = str(self.timeframe).strip() or None

        if self.direction is not None:
            self.direction = str(self.direction).strip() or None

        if self.risk_level is not None:
            self.risk_level = str(self.risk_level).strip() or None

        if self.user_id is not None:
            self.user_id = str(self.user_id).strip() or None

        if self.session_id is not None:
            self.session_id = str(self.session_id).strip() or None

        if self.request_id is not None:
            self.request_id = str(self.request_id).strip() or None

        self.evidence_ids = [
            str(item).strip()
            for item in self.evidence_ids
            if str(item).strip()
        ]

        if not isinstance(self.metadata, dict):
            self.metadata = dict(self.metadata)

        self._validate_numeric_fields()

        self.timestamp = self._normalize_datetime(self.timestamp)
        self.created_at = self._normalize_datetime(self.created_at)
        self.updated_at = self._normalize_datetime(self.updated_at)

    def _validate_numeric_fields(self) -> None:
        """Validate optional numeric values."""

        numeric_fields = {
            "confidence": self.confidence,
            "score": self.score,
            "risk_score": self.risk_score,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
        }

        for name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(f"{name} must be numeric, not boolean.")

            try:
                numeric_value = float(value)
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    f"{name} must be numeric."
                ) from exc

            if name in {
                "confidence",
                "score",
                "risk_score",
            }:
                if not 0.0 <= numeric_value <= 100.0:
                    raise ValueError(
                        f"{name} must be between 0 and 100."
                    )

            setattr(self, name, numeric_value)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        """Ensure datetime values are timezone-aware UTC."""

        if not isinstance(value, datetime):
            raise TypeError("Timestamp values must be datetime instances.")

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)

    def touch(self) -> None:
        """Update the modification timestamp."""

        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable dictionary representation."""

        data = asdict(self)

        data["timestamp"] = self.timestamp.isoformat()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()

        return data

    @classmethod
    def from_dict(
        cls,
        data: Mapping[str, Any],
    ) -> "DecisionRecord":
        """Create a decision record from a mapping."""

        if not isinstance(data, Mapping):
            raise TypeError("data must be a mapping.")

        values = dict(data)

        for field_name in (
            "timestamp",
            "created_at",
            "updated_at",
        ):
            value = values.get(field_name)

            if isinstance(value, str):
                values[field_name] = datetime.fromisoformat(value)

        return cls(**values)

    def add_evidence(self, evidence_id: str) -> None:
        """Attach an evidence identifier to the decision."""

        evidence_id = str(evidence_id).strip()

        if not evidence_id:
            raise ValueError("evidence_id cannot be empty.")

        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

        self.touch()

    def remove_evidence(self, evidence_id: str) -> bool:
        """Remove an evidence identifier if present."""

        evidence_id = str(evidence_id).strip()

        if evidence_id in self.evidence_ids:
            self.evidence_ids.remove(evidence_id)
            self.touch()
            return True

        return False

    def set_verdict(
        self,
        verdict: str,
        decision_state: Optional[str] = None,
    ) -> None:
        """Update the decision verdict and optionally its state."""

        verdict = str(verdict).strip()

        if not verdict:
            raise ValueError("verdict cannot be empty.")

        self.verdict = verdict

        if decision_state is not None:
            self.decision_state = str(decision_state).strip()

        self.touch()

    def with_metadata(
        self,
        key: str,
        value: Any,
    ) -> "DecisionRecord":
        """
        Return a copy containing additional metadata.

        The original record is not modified.
        """

        key = str(key).strip()

        if not key:
            raise ValueError("Metadata key cannot be empty.")

        copied_metadata = dict(self.metadata)
        copied_metadata[key] = value

        return DecisionRecord(
            decision_id=self.decision_id,
            timestamp=self.timestamp,
            decision_type=self.decision_type,
            decision_state=self.decision_state,
            verdict=self.verdict,
            market=self.market,
            instrument=self.instrument,
            venue=self.venue,
            mode=self.mode,
            timeframe=self.timeframe,
            direction=self.direction,
            confidence=self.confidence,
            score=self.score,
            evidence_ids=list(self.evidence_ids),
            risk_level=self.risk_level,
            risk_score=self.risk_score,
            entry_price=self.entry_price,
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
            user_id=self.user_id,
            session_id=self.session_id,
            request_id=self.request_id,
            metadata=copied_metadata,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


def create_decision_record(
    *,
    decision_type: str,
    decision_state: str,
    verdict: str,
    market: Optional[str] = None,
    instrument: Optional[str] = None,
    venue: Optional[str] = None,
    mode: Optional[str] = None,
    timeframe: Optional[str] = None,
    direction: Optional[str] = None,
    confidence: Optional[float] = None,
    score: Optional[float] = None,
    evidence_ids: Optional[list[str]] = None,
    risk_level: Optional[str] = None,
    risk_score: Optional[float] = None,
    entry_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    request_id: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> DecisionRecord:
    """Convenience factory for creating decision records."""

    return DecisionRecord(
        decision_type=decision_type,
        decision_state=decision_state,
        verdict=verdict,
        market=market,
        instrument=instrument,
        venue=venue,
        mode=mode,
        timeframe=timeframe,
        direction=direction,
        confidence=confidence,
        score=score,
        evidence_ids=list(evidence_ids or []),
        risk_level=risk_level,
        risk_score=risk_score,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        user_id=user_id,
        session_id=session_id,
        request_id=request_id,
        metadata=dict(metadata or {}),
    )


__all__ = [
    "DecisionRecord",
    "create_decision_record",
]