from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping, Optional


def _utc(dt: datetime) -> datetime:
    if not isinstance(dt, datetime):
        raise TypeError("timestamp must be a datetime")

    if dt.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")

    return dt.astimezone(timezone.utc)


def _decimal(
    value: Decimal | int | float | str | None,
    *,
    field_name: str,
    allow_none: bool = True,
) -> Optional[Decimal]:
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field_name} is required")

    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValueError(
            f"{field_name} must be numeric"
        ) from exc

    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")

    return result


@dataclass(frozen=True)
class RiskLevel:
    """
    Normalized qualitative risk classification.

    This schema describes risk.
    It does not make a trading decision.
    """

    level: str

    def __post_init__(self) -> None:
        value = self.level.strip().upper()

        allowed = {
            "VERY_LOW",
            "LOW",
            "MODERATE",
            "HIGH",
            "VERY_HIGH",
            "UNKNOWN",
        }

        if value not in allowed:
            raise ValueError(
                f"Unsupported risk level: {self.level}"
            )

        object.__setattr__(self, "level", value)


@dataclass(frozen=True)
class RiskRange:
    """
    Numeric risk range.

    Values are descriptive measurements only.
    """

    minimum: Decimal
    maximum: Decimal

    def __post_init__(self) -> None:
        minimum = _decimal(
            self.minimum,
            field_name="minimum",
            allow_none=False,
        )
        maximum = _decimal(
            self.maximum,
            field_name="maximum",
            allow_none=False,
        )

        assert minimum is not None
        assert maximum is not None

        if minimum < Decimal("0"):
            raise ValueError("minimum cannot be negative")

        if maximum < Decimal("0"):
            raise ValueError("maximum cannot be negative")

        if minimum > maximum:
            raise ValueError(
                "minimum cannot be greater than maximum"
            )

        object.__setattr__(self, "minimum", minimum)
        object.__setattr__(self, "maximum", maximum)


@dataclass(frozen=True)
class RiskResult:
    """
    Canonical risk assessment schema.

    RiskResult is an output contract for risk intelligence.
    It must not contain BUY/SELL decisions, opportunity rankings,
    execution commands, or trade recommendations.
    """

    instrument: str
    assessed_at: datetime

    risk_level: RiskLevel

    risk_score: Decimal

    volatility_risk: Optional[Decimal] = None
    liquidity_risk: Optional[Decimal] = None
    market_structure_risk: Optional[Decimal] = None
    timing_risk: Optional[Decimal] = None
    event_risk: Optional[Decimal] = None
    derivative_risk: Optional[Decimal] = None
    data_quality_risk: Optional[Decimal] = None

    expected_loss: Optional[Decimal] = None
    maximum_loss: Optional[Decimal] = None

    risk_range: Optional[RiskRange] = None

    source_ids: tuple[str, ...] = field(default_factory=tuple)

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        instrument = self.instrument.strip()

        if not instrument:
            raise ValueError("instrument is required")

        object.__setattr__(self, "instrument", instrument)

        assessed_at = _utc(self.assessed_at)
        object.__setattr__(self, "assessed_at", assessed_at)

        score = _decimal(
            self.risk_score,
            field_name="risk_score",
            allow_none=False,
        )

        assert score is not None

        if score < Decimal("0") or score > Decimal("100"):
            raise ValueError(
                "risk_score must be between 0 and 100"
            )

        object.__setattr__(self, "risk_score", score)

        component_names = (
            "volatility_risk",
            "liquidity_risk",
            "market_structure_risk",
            "timing_risk",
            "event_risk",
            "derivative_risk",
            "data_quality_risk",
            "expected_loss",
            "maximum_loss",
        )

        for name in component_names:
            value = _decimal(
                getattr(self, name),
                field_name=name,
            )

            if value is not None and value < Decimal("0"):
                raise ValueError(
                    f"{name} cannot be negative"
                )

            object.__setattr__(self, name, value)

        normalized_sources: list[str] = []

        for source_id in self.source_ids:
            source = str(source_id).strip()

            if source:
                normalized_sources.append(source)

        object.__setattr__(
            self,
            "source_ids",
            tuple(dict.fromkeys(normalized_sources)),
        )

        object.__setattr__(
            self,
            "metadata",
            dict(self.metadata),
        )

    @property
    def is_high_risk(self) -> bool:
        return self.risk_level.level in {
            "HIGH",
            "VERY_HIGH",
        }

    @property
    def is_low_risk(self) -> bool:
        return self.risk_level.level in {
            "VERY_LOW",
            "LOW",
        }

    @property
    def normalized_safety_score(self) -> Decimal:
        """
        Converts risk score into an inverse safety score.

        100 risk -> 0 safety
        0 risk -> 100 safety
        """

        return Decimal("100") - self.risk_score

    def to_dict(self) -> dict[str, Any]:
        def serialize(value: Any) -> Any:
            if isinstance(value, Decimal):
                return str(value)

            if isinstance(value, datetime):
                return value.isoformat()

            if isinstance(value, RiskLevel):
                return value.level

            if isinstance(value, RiskRange):
                return {
                    "minimum": str(value.minimum),
                    "maximum": str(value.maximum),
                }

            if isinstance(value, Mapping):
                return {
                    str(k): serialize(v)
                    for k, v in value.items()
                }

            if isinstance(value, (tuple, list)):
                return [
                    serialize(item)
                    for item in value
                ]

            return value

        return {
            "instrument": self.instrument,
            "assessed_at": self.assessed_at.isoformat(),
            "risk_level": self.risk_level.level,
            "risk_score": str(self.risk_score),
            "volatility_risk": serialize(
                self.volatility_risk
            ),
            "liquidity_risk": serialize(
                self.liquidity_risk
            ),
            "market_structure_risk": serialize(
                self.market_structure_risk
            ),
            "timing_risk": serialize(
                self.timing_risk
            ),
            "event_risk": serialize(
                self.event_risk
            ),
            "derivative_risk": serialize(
                self.derivative_risk
            ),
            "data_quality_risk": serialize(
                self.data_quality_risk
            ),
            "expected_loss": serialize(
                self.expected_loss
            ),
            "maximum_loss": serialize(
                self.maximum_loss
            ),
            "risk_range": serialize(
                self.risk_range
            ),
            "source_ids": list(self.source_ids),
            "metadata": serialize(self.metadata),
        }


__all__ = [
    "RiskLevel",
    "RiskRange",
    "RiskResult",
]