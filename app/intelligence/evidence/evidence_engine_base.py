"""
ROBOMLM_PLUS
Evidence Cortex
----------------
Common mathematical/validation foundation for all Evidence engines.

Engineering contract:

RAW INPUT
    ↓
VALIDATION
    ↓
CALCULATION
    ↓
EVIDENCE
    ↓
TRACE / LINEAGE
    ↓
VALIDATED OUTPUT

This module deliberately does NOT:
- invent confidence
- invent market scores
- hide missing data
- convert missing observations into neutral values
- make trading decisions
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Mapping, Optional, Sequence


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class EvidenceStatus(str, Enum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class EvidenceKind(str, Enum):
    OBSERVATION = "OBSERVATION"
    DERIVED = "DERIVED"
    RELATIONSHIP = "RELATIONSHIP"
    VALIDATION = "VALIDATION"


# ---------------------------------------------------------------------------
# CALCULATION TRACE
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CalculationStep:
    """
    One deterministic calculation step.

    Example:
        NED = aggressive_buy_volume - aggressive_sell_volume
    """

    name: str
    formula: str
    inputs: Mapping[str, Any]
    output: Any


# ---------------------------------------------------------------------------
# EVIDENCE OBJECT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Evidence:
    """
    Internal Evidence Cortex representation.

    Important:
    Evidence is not a decision.
    Evidence is not a signal.
    Evidence is not a confidence claim.

    It records:
        what was observed/derived,
        how it was calculated,
        from which engine,
        using which inputs,
        and whether the result is valid.
    """

    evidence_id: str
    engine: str
    layer: str
    metric: str

    value: Any
    unit: Optional[str]

    status: EvidenceStatus

    observed_at: datetime
    generated_at: datetime

    source: Optional[str] = None
    source_type: Optional[str] = None

    inputs: Mapping[str, Any] = field(default_factory=dict)
    calculation: tuple[CalculationStep, ...] = ()

    lineage: tuple[str, ...] = ()

    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id cannot be empty")

        if not self.engine:
            raise ValueError("engine cannot be empty")

        if not self.layer:
            raise ValueError("layer cannot be empty")

        if not self.metric:
            raise ValueError("metric cannot be empty")

        if not isinstance(self.status, EvidenceStatus):
            raise TypeError("status must be EvidenceStatus")

        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")

        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at must be timezone-aware")


# ---------------------------------------------------------------------------
# BASE ENGINE
# ---------------------------------------------------------------------------

class EvidenceEngineBase(ABC):
    """
    Base contract for every Evidence Cortex engine.

    Universal processing contract:

        INPUT
          ↓
        VALIDATE
          ↓
        PROCESS
          ↓
        EVIDENCE

    Subclasses implement only their domain calculation.
    Common validation and evidence construction remain centralized.
    """

    ENGINE_NAME: str = "UNDEFINED"
    LAYER: str = "L000"

    def __init__(self) -> None:
        self._sequence: int = 0

    # ------------------------------------------------------------------
    # PUBLIC ENGINE CONTRACT
    # ------------------------------------------------------------------

    def process(self, data: Mapping[str, Any]) -> Evidence | tuple[Evidence, ...]:
        """
        Public processing boundary.

        Missing/invalid inputs are never silently converted into values.
        """

        self.validate_input(data)
        result = self.calculate(data)

        if isinstance(result, Evidence):
            return result

        return tuple(result)

    # ------------------------------------------------------------------
    # REQUIRED SUBCLASS METHODS
    # ------------------------------------------------------------------

    @abstractmethod
    def calculate(
        self,
        data: Mapping[str, Any],
    ) -> Evidence | tuple[Evidence, ...]:
        """
        Domain-specific mathematical calculation.

        Subclasses must return Evidence objects.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------------------

    def validate_input(self, data: Mapping[str, Any]) -> None:
        if not isinstance(data, Mapping):
            raise TypeError(
                f"{self.ENGINE_NAME}: input must be a Mapping, "
                f"got {type(data).__name__}"
            )

    def require(
        self,
        data: Mapping[str, Any],
        *fields: str,
    ) -> None:
        """
        Require fields to exist and not be None.
        """

        missing = [
            field
            for field in fields
            if field not in data or data[field] is None
        ]

        if missing:
            raise ValueError(
                f"{self.ENGINE_NAME}: missing required input(s): "
                f"{', '.join(missing)}"
            )

    # ------------------------------------------------------------------
    # NUMERIC VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def numeric(
        value: Any,
        *,
        name: str,
        allow_negative: bool = True,
    ) -> float:
        """
        Convert and validate a finite numeric value.
        """

        if isinstance(value, bool):
            raise TypeError(f"{name} must be numeric, not bool")

        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"{name} must be numeric; got {value!r}"
            ) from exc

        if not isfinite(number):
            raise ValueError(
                f"{name} must be finite; got {number!r}"
            )

        if not allow_negative and number < 0:
            raise ValueError(
                f"{name} cannot be negative; got {number}"
            )

        return number

    @classmethod
    def non_negative(
        cls,
        value: Any,
        *,
        name: str,
    ) -> float:
        return cls.numeric(
            value,
            name=name,
            allow_negative=False,
        )

    @classmethod
    def positive(
        cls,
        value: Any,
        *,
        name: str,
    ) -> float:
        number = cls.numeric(
            value,
            name=name,
            allow_negative=False,
        )

        if number <= 0:
            raise ValueError(
                f"{name} must be greater than zero; got {number}"
            )

        return number

    # ------------------------------------------------------------------
    # RANGE VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def bounded(
        value: float,
        *,
        lower: float,
        upper: float,
        name: str,
    ) -> float:
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")

        if lower > upper:
            raise ValueError(
                f"Invalid bounds for {name}: {lower} > {upper}"
            )

        if not lower <= value <= upper:
            raise ValueError(
                f"{name}={value} outside [{lower}, {upper}]"
            )

        return value

    @staticmethod
    def ratio(
        numerator: float,
        denominator: float,
        *,
        name: str,
    ) -> Optional[float]:
        """
        Safe ratio.

        denominator == 0 does NOT become an invented 0.

        It returns None because the ratio is mathematically undefined.
        """

        if not isfinite(numerator):
            raise ValueError(f"{name}: numerator must be finite")

        if not isfinite(denominator):
            raise ValueError(f"{name}: denominator must be finite")

        if denominator == 0:
            return None

        return numerator / denominator

    @staticmethod
    def unit_ratio(
        numerator: float,
        denominator: float,
        *,
        name: str,
    ) -> Optional[float]:
        """
        Ratio constrained to [0, 1].

        Used only where the underlying quantity is mathematically
        defined as a bounded fraction.
        """

        result = EvidenceEngineBase.ratio(
            numerator,
            denominator,
            name=name,
        )

        if result is None:
            return None

        return EvidenceEngineBase.bounded(
            result,
            lower=0.0,
            upper=1.0,
            name=name,
        )

    # ------------------------------------------------------------------
    # TIME VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def validate_timestamp(
        timestamp: datetime,
        *,
        name: str = "timestamp",
    ) -> datetime:
        if not isinstance(timestamp, datetime):
            raise TypeError(
                f"{name} must be datetime"
            )

        if timestamp.tzinfo is None:
            raise ValueError(
                f"{name} must be timezone-aware"
            )

        return timestamp

    @staticmethod
    def elapsed_seconds(
        start: datetime,
        end: datetime,
    ) -> float:
        """
        Calculate elapsed time.

        Negative time is invalid because it represents a chronology
        violation rather than a legitimate zero-duration event.
        """

        EvidenceEngineBase.validate_timestamp(start, name="start")
        EvidenceEngineBase.validate_timestamp(end, name="end")

        seconds = (end - start).total_seconds()

        if seconds < 0:
            raise ValueError(
                f"Chronology violation: end={end} precedes start={start}"
            )

        return seconds

    # ------------------------------------------------------------------
    # EVIDENCE ID
    # ------------------------------------------------------------------

    def _next_evidence_id(self) -> str:
        self._sequence += 1

        return (
            f"{self.ENGINE_NAME}-"
            f"{self._sequence:08d}"
        )

    # ------------------------------------------------------------------
    # EVIDENCE FACTORY
    # ------------------------------------------------------------------

    def make_evidence(
        self,
        *,
        metric: str,
        value: Any,
        observed_at: datetime,
        unit: Optional[str] = None,
        status: EvidenceStatus = EvidenceStatus.VALID,
        source: Optional[str] = None,
        source_type: Optional[str] = None,
        inputs: Optional[Mapping[str, Any]] = None,
        calculation: Optional[Sequence[CalculationStep]] = None,
        lineage: Optional[Sequence[str]] = None,
        reason: Optional[str] = None,
    ) -> Evidence:
        """
        Central Evidence construction.

        Notice:
        There is intentionally NO confidence=95 or confidence=100
        default. Confidence belongs to the Evidence Confidence layer.
        """

        observed_at = self.validate_timestamp(
            observed_at,
            name="observed_at",
        )

        generated_at = datetime.now(timezone.utc)

        return Evidence(
            evidence_id=self._next_evidence_id(),
            engine=self.ENGINE_NAME,
            layer=self.LAYER,
            metric=metric,
            value=value,
            unit=unit,
            status=status,
            observed_at=observed_at,
            generated_at=generated_at,
            source=source,
            source_type=source_type,
            inputs=dict(inputs or {}),
            calculation=tuple(calculation or ()),
            lineage=tuple(lineage or ()),
            reason=reason,
        )

    # ------------------------------------------------------------------
    # FAILURE STATES
    # ------------------------------------------------------------------

    def insufficient(
        self,
        *,
        metric: str,
        observed_at: datetime,
        reason: str,
        inputs: Optional[Mapping[str, Any]] = None,
    ) -> Evidence:
        """
        Explicit insufficient-evidence result.

        This is preferable to fabricating a numerical value.
        """

        return self.make_evidence(
            metric=metric,
            value=None,
            observed_at=observed_at,
            status=EvidenceStatus.INSUFFICIENT,
            inputs=inputs,
            reason=reason,
        )

    def partial(
        self,
        *,
        metric: str,
        value: Any,
        observed_at: datetime,
        reason: str,
        inputs: Optional[Mapping[str, Any]] = None,
    ) -> Evidence:
        return self.make_evidence(
            metric=metric,
            value=value,
            observed_at=observed_at,
            status=EvidenceStatus.PARTIAL,
            inputs=inputs,
            reason=reason,
        )

    def invalid(
        self,
        *,
        metric: str,
        observed_at: datetime,
        reason: str,
        inputs: Optional[Mapping[str, Any]] = None,
    ) -> Evidence:
        return self.make_evidence(
            metric=metric,
            value=None,
            observed_at=observed_at,
            status=EvidenceStatus.INVALID,
            inputs=inputs,
            reason=reason,
        )

    # ------------------------------------------------------------------
    # EVIDENCE VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def validate_evidence(
        evidence: Evidence,
    ) -> Evidence:
        if not isinstance(evidence, Evidence):
            raise TypeError(
                "Expected Evidence object"
            )

        EvidenceEngineBase.validate_timestamp(
            evidence.observed_at,
            name="evidence.observed_at",
        )

        EvidenceEngineBase.validate_timestamp(
            evidence.generated_at,
            name="evidence.generated_at",
        )

        return evidence

    @classmethod
    def validate_results(
        cls,
        results: Evidence | Sequence[Evidence],
    ) -> tuple[Evidence, ...]:
        if isinstance(results, Evidence):
            results = (results,)

        validated: list[Evidence] = []

        for evidence in results:
            validated.append(
                cls.validate_evidence(evidence)
            )

        return tuple(validated)


__all__ = [
    "EvidenceStatus",
    "EvidenceKind",
    "CalculationStep",
    "Evidence",
    "EvidenceEngineBase",
]