from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence

from schemas.evidence.evidence_item import EvidenceItem
from schemas.evidence.evidence_package import EvidencePackage


class ReliabilityStatus(str, Enum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


class ReliabilityState(str, Enum):
    """
    Interpretable state of source reliability.

    No state is assigned from source name alone.
    """

    ESTABLISHED = "ESTABLISHED"
    SUPPORTED = "SUPPORTED"
    MIXED = "MIXED"
    WEAK = "WEAK"
    UNASSESSED = "UNASSESSED"


@dataclass(frozen=True)
class SourceReliabilityObservation:
    """
    Historical validation observation for one source.

    The observation represents measurable source behaviour.  It does not
    represent a manually assigned reputation.
    """

    source: str

    total_observations: int
    validated_observations: int
    correct_observations: int

    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        if not self.source:
            return False

        if self.total_observations < 0:
            return False

        if self.validated_observations < 0:
            return False

        if self.correct_observations < 0:
            return False

        if self.validated_observations > self.total_observations:
            return False

        if self.correct_observations > self.validated_observations:
            return False

        if self.evaluated_at.tzinfo is None:
            return False

        return True

    @property
    def validation_rate(self) -> float | None:
        if self.total_observations == 0:
            return None

        return (
            self.validated_observations
            / self.total_observations
        )

    @property
    def accuracy_rate(self) -> float | None:
        if self.validated_observations == 0:
            return None

        return (
            self.correct_observations
            / self.validated_observations
        )


@dataclass(frozen=True)
class SourceReliabilityResult:
    """
    Deterministic reliability assessment for one source.
    """

    status: ReliabilityStatus

    source: str

    state: ReliabilityState

    reliability: float | None

    validation_rate: float | None
    accuracy_rate: float | None

    total_observations: int
    validated_observations: int
    correct_observations: int

    effective_sample_size: int

    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    calculation: tuple[Mapping[str, Any], ...] = field(
        default_factory=tuple
    )

    reason: str = ""

    evaluated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    engine: str = "SourceReliabilityEngine"
    version: str = "1.0"

    def is_valid(self) -> bool:
        if not self.source:
            return False

        if self.total_observations < 0:
            return False

        if self.validated_observations < 0:
            return False

        if self.correct_observations < 0:
            return False

        if self.effective_sample_size < 0:
            return False

        if self.reliability is not None:
            if not 0.0 <= self.reliability <= 1.0:
                return False

        for value in (
            self.validation_rate,
            self.accuracy_rate,
        ):
            if value is not None:
                if not 0.0 <= value <= 1.0:
                    return False

        if self.evaluated_at.tzinfo is None:
            return False

        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "source": self.source,
            "state": self.state.value,
            "reliability": self.reliability,
            "validation_rate": self.validation_rate,
            "accuracy_rate": self.accuracy_rate,
            "total_observations": self.total_observations,
            "validated_observations": self.validated_observations,
            "correct_observations": self.correct_observations,
            "effective_sample_size": self.effective_sample_size,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "calculation": [
                dict(step)
                for step in self.calculation
            ],
            "reason": self.reason,
            "evaluated_at": self.evaluated_at.isoformat(),
            "engine": self.engine,
            "version": self.version,
        }


class SourceReliabilityEngine:
    """
    Source Reliability Engine.

    Core principle
    --------------
    Reliability must be evidence-based.

    A source name, provider name, venue name, or hardcoded reputation
    cannot by itself establish reliability.

    The engine therefore supports two paths:

    1. Historical validation observations:
       reliability is derived from observed correctness.

    2. Evidence-package analysis:
       reliability can only be assessed when explicit source validation
       information is present in metadata.

    Mathematical foundation
    ------------------------
    Validation rate:

        V = N_validated / N_total

    Accuracy among validated observations:

        A = N_correct / N_validated

    Reliability:

        R = A

    when validated observations exist.

    If validation coverage is incomplete, reliability is not silently
    treated as perfect.  The result remains PARTIAL and carries the
    measured validation rate separately.

    Optional Bayesian smoothing
    ----------------------------
    If `prior_alpha` and `prior_beta` are explicitly supplied:

        R = (correct + alpha)
            / (validated + alpha + beta)

    This is a declared statistical prior, not an arbitrary score.

    The default path uses the directly observed empirical accuracy:

        R = correct / validated

    No confidence is manufactured from reliability.
    """

    VERSION = "1.0"

    def evaluate(
        self,
        observation: SourceReliabilityObservation,
        *,
        prior_alpha: float | None = None,
        prior_beta: float | None = None,
    ) -> SourceReliabilityResult:
        """
        Evaluate one source from explicit historical validation data.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not isinstance(
            observation,
            SourceReliabilityObservation,
        ):
            return self._invalid(
                source="",
                error=(
                    "observation must be a "
                    "SourceReliabilityObservation"
                ),
            )

        if not observation.is_valid():
            return self._invalid(
                source=observation.source,
                error="Source reliability observation is invalid.",
            )

        prior_enabled = (
            prior_alpha is not None
            or prior_beta is not None
        )

        if prior_enabled:
            if prior_alpha is None or prior_beta is None:
                return self._invalid(
                    source=observation.source,
                    error=(
                        "prior_alpha and prior_beta must be "
                        "provided together."
                    ),
                )

            if (
                not isfinite(float(prior_alpha))
                or not isfinite(float(prior_beta))
                or float(prior_alpha) <= 0.0
                or float(prior_beta) <= 0.0
            ):
                return self._invalid(
                    source=observation.source,
                    error=(
                        "prior_alpha and prior_beta must be "
                        "finite and strictly positive."
                    ),
                )

        validation_rate = observation.validation_rate
        accuracy_rate = observation.accuracy_rate

        if observation.total_observations == 0:
            return SourceReliabilityResult(
                status=ReliabilityStatus.INSUFFICIENT,
                source=observation.source,
                state=ReliabilityState.UNASSESSED,
                reliability=None,
                validation_rate=None,
                accuracy_rate=None,
                total_observations=0,
                validated_observations=0,
                correct_observations=0,
                effective_sample_size=0,
                warnings=(
                    "No source observations are available.",
                ),
                reason=(
                    "Reliability cannot be calculated without "
                    "observations."
                ),
                evaluated_at=observation.evaluated_at,
                version=self.VERSION,
            )

        if observation.validated_observations == 0:
            return SourceReliabilityResult(
                status=ReliabilityStatus.PARTIAL,
                source=observation.source,
                state=ReliabilityState.UNASSESSED,
                reliability=None,
                validation_rate=validation_rate,
                accuracy_rate=None,
                total_observations=observation.total_observations,
                validated_observations=0,
                correct_observations=0,
                effective_sample_size=0,
                warnings=(
                    "Observations exist, but none have been "
                    "validated."
                ),
                reason=(
                    "Source reliability is not estimable because "
                    "validated observations are absent."
                ),
                evaluated_at=observation.evaluated_at,
                version=self.VERSION,
            )

        calculation: list[Mapping[str, Any]] = []

        if prior_enabled:
            alpha = float(prior_alpha)
            beta = float(prior_beta)

            reliability = (
                observation.correct_observations + alpha
            ) / (
                observation.validated_observations
                + alpha
                + beta
            )

            calculation.append(
                {
                    "name": "bayesian_reliability",
                    "formula": (
                        "(correct + alpha) / "
                        "(validated + alpha + beta)"
                    ),
                    "inputs": {
                        "correct": observation.correct_observations,
                        "validated": (
                            observation.validated_observations
                        ),
                        "alpha": alpha,
                        "beta": beta,
                    },
                    "output": reliability,
                }
            )

        else:
            reliability = accuracy_rate

            calculation.append(
                {
                    "name": "empirical_accuracy",
                    "formula": (
                        "correct_observations / "
                        "validated_observations"
                    ),
                    "inputs": {
                        "correct": observation.correct_observations,
                        "validated": (
                            observation.validated_observations
                        ),
                    },
                    "output": reliability,
                }
            )

        if reliability is None:
            return SourceReliabilityResult(
                status=ReliabilityStatus.INSUFFICIENT,
                source=observation.source,
                state=ReliabilityState.UNASSESSED,
                reliability=None,
                validation_rate=validation_rate,
                accuracy_rate=accuracy_rate,
                total_observations=observation.total_observations,
                validated_observations=(
                    observation.validated_observations
                ),
                correct_observations=observation.correct_observations,
                effective_sample_size=(
                    observation.validated_observations
                ),
                calculation=tuple(calculation),
                reason="Reliability could not be calculated.",
                evaluated_at=observation.evaluated_at,
                version=self.VERSION,
            )

        state = self._state_from_observation(
            reliability=reliability,
            validated=observation.validated_observations,
            total=observation.total_observations,
        )

        status = ReliabilityStatus.VALID

        if observation.validated_observations < (
            observation.total_observations
        ):
            status = ReliabilityStatus.PARTIAL

            warnings.append(
                "Validation coverage is incomplete; "
                "reliability is based only on validated observations."
            )

        calculation.append(
            {
                "name": "validation_rate",
                "formula": "validated_observations / total_observations",
                "inputs": {
                    "validated": observation.validated_observations,
                    "total": observation.total_observations,
                },
                "output": validation_rate,
            }
        )

        return SourceReliabilityResult(
            status=status,
            source=observation.source,
            state=state,
            reliability=reliability,
            validation_rate=validation_rate,
            accuracy_rate=accuracy_rate,
            total_observations=observation.total_observations,
            validated_observations=observation.validated_observations,
            correct_observations=observation.correct_observations,
            effective_sample_size=(
                observation.validated_observations
            ),
            errors=tuple(errors),
            warnings=tuple(warnings),
            calculation=tuple(calculation),
            reason=(
                "Source reliability calculated from explicit "
                "historical validation evidence."
            ),
            evaluated_at=observation.evaluated_at,
            version=self.VERSION,
        )

    def evaluate_package(
        self,
        package: EvidencePackage,
    ) -> dict[str, SourceReliabilityResult]:
        """
        Evaluate source reliability using explicit validation metadata
        contained in EvidenceItems.

        Expected metadata fields:

            validation_total
            validation_count
            correct_count

        The engine deliberately does not infer correctness merely from
        agreement between sources.
        """
        if not isinstance(package, EvidencePackage):
            return {}

        if not package.is_valid():
            return {}

        grouped: dict[
            str,
            list[EvidenceItem],
        ] = {}

        for item in package.items:
            grouped.setdefault(item.source, []).append(item)

        results: dict[str, SourceReliabilityResult] = {}

        for source in sorted(grouped):
            observations = grouped[source]

            observation = self._observation_from_items(
                source,
                observations,
            )

            if observation is None:
                results[source] = SourceReliabilityResult(
                    status=ReliabilityStatus.INSUFFICIENT,
                    source=source,
                    state=ReliabilityState.UNASSESSED,
                    reliability=None,
                    validation_rate=None,
                    accuracy_rate=None,
                    total_observations=0,
                    validated_observations=0,
                    correct_observations=0,
                    effective_sample_size=0,
                    warnings=(
                        "No explicit source validation metadata "
                        "was available.",
                    ),
                    reason=(
                        "Package evidence alone cannot establish "
                        "historical source reliability."
                    ),
                    version=self.VERSION,
                )
                continue

            results[source] = self.evaluate(observation)

        return results

    def aggregate(
        self,
        observations: Iterable[SourceReliabilityObservation],
    ) -> dict[str, SourceReliabilityObservation]:
        """
        Aggregate independently recorded source-validation observations.

        Counts are additive because each observation is assumed to
        represent a distinct evaluation batch.
        """
        grouped: dict[
            str,
            list[SourceReliabilityObservation],
        ] = {}

        for observation in observations:
            if not isinstance(
                observation,
                SourceReliabilityObservation,
            ):
                raise TypeError(
                    "All observations must be "
                    "SourceReliabilityObservation instances."
                )

            if not observation.is_valid():
                raise ValueError(
                    "Cannot aggregate an invalid source observation."
                )

            grouped.setdefault(
                observation.source,
                [],
            ).append(observation)

        aggregated: dict[
            str,
            SourceReliabilityObservation,
        ] = {}

        for source in sorted(grouped):
            source_observations = grouped[source]

            latest = max(
                source_observations,
                key=lambda item: item.evaluated_at,
            )

            aggregated[source] = SourceReliabilityObservation(
                source=source,
                total_observations=sum(
                    item.total_observations
                    for item in source_observations
                ),
                validated_observations=sum(
                    item.validated_observations
                    for item in source_observations
                ),
                correct_observations=sum(
                    item.correct_observations
                    for item in source_observations
                ),
                evaluated_at=latest.evaluated_at,
                metadata={
                    "aggregated_batches": len(
                        source_observations
                    ),
                },
            )

        return aggregated

    # ------------------------------------------------------------------
    # Explicit package validation metadata
    # ------------------------------------------------------------------

    def _observation_from_items(
        self,
        source: str,
        items: Sequence[EvidenceItem],
    ) -> SourceReliabilityObservation | None:
        totals: list[int] = []
        validated: list[int] = []
        correct: list[int] = []

        latest_timestamp: datetime | None = None

        for item in items:
            metadata = item.metadata

            total = self._read_nonnegative_int(
                metadata,
                (
                    "validation_total",
                    "total_observations",
                ),
            )

            valid = self._read_nonnegative_int(
                metadata,
                (
                    "validation_count",
                    "validated_observations",
                ),
            )

            correct_count = self._read_nonnegative_int(
                metadata,
                (
                    "correct_count",
                    "correct_observations",
                ),
            )

            if (
                total is None
                or valid is None
                or correct_count is None
            ):
                continue

            if valid > total or correct_count > valid:
                continue

            totals.append(total)
            validated.append(valid)
            correct.append(correct_count)

            if (
                latest_timestamp is None
                or item.observed_at > latest_timestamp
            ):
                latest_timestamp = item.observed_at

        if not totals:
            return None

        return SourceReliabilityObservation(
            source=source,
            total_observations=sum(totals),
            validated_observations=sum(validated),
            correct_observations=sum(correct),
            evaluated_at=(
                latest_timestamp
                if latest_timestamp is not None
                else datetime.now(timezone.utc)
            ),
        )

    # ------------------------------------------------------------------
    # State classification
    # ------------------------------------------------------------------

    @staticmethod
    def _state_from_observation(
        *,
        reliability: float,
        validated: int,
        total: int,
    ) -> ReliabilityState:
        """
        State classification is intentionally structural rather than
        based on arbitrary reliability percentage bands.

        Reliability remains the numeric result.  State primarily conveys
        evidence support depth.
        """
        if validated <= 0:
            return ReliabilityState.UNASSESSED

        if validated < total:
            if reliability >= 0.5:
                return ReliabilityState.SUPPORTED

            return ReliabilityState.MIXED

        if reliability >= 0.5:
            return ReliabilityState.ESTABLISHED

        if reliability > 0.0:
            return ReliabilityState.WEAK

        return ReliabilityState.MIXED

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_nonnegative_int(
        metadata: Mapping[str, Any],
        keys: Sequence[str],
    ) -> int | None:
        for key in keys:
            if key not in metadata:
                continue

            value = metadata[key]

            if isinstance(value, bool):
                return None

            if isinstance(value, int):
                if value >= 0:
                    return value

                return None

            if isinstance(value, float):
                if isfinite(value) and value.is_integer() and value >= 0:
                    return int(value)

                return None

            return None

        return None

    def _invalid(
        self,
        *,
        source: str,
        error: str,
    ) -> SourceReliabilityResult:
        return SourceReliabilityResult(
            status=ReliabilityStatus.INVALID,
            source=source,
            state=ReliabilityState.UNASSESSED,
            reliability=None,
            validation_rate=None,
            accuracy_rate=None,
            total_observations=0,
            validated_observations=0,
            correct_observations=0,
            effective_sample_size=0,
            errors=(error,),
            reason="Invalid source reliability input.",
            version=self.VERSION,
        )


# ----------------------------------------------------------------------
# Convenience functions
# ----------------------------------------------------------------------

def evaluate_source_reliability(
    observation: SourceReliabilityObservation,
    *,
    prior_alpha: float | None = None,
    prior_beta: float | None = None,
) -> SourceReliabilityResult:
    return SourceReliabilityEngine().evaluate(
        observation,
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
    )


def evaluate_package_source_reliability(
    package: EvidencePackage,
) -> dict[str, SourceReliabilityResult]:
    return SourceReliabilityEngine().evaluate_package(package)


# ----------------------------------------------------------------------
# Deterministic self-test
# ----------------------------------------------------------------------

def _self_test() -> None:
    timestamp = datetime(
        2026,
        1,
        1,
        10,
        0,
        tzinfo=timezone.utc,
    )

    observation = SourceReliabilityObservation(
        source="feed_A",
        total_observations=100,
        validated_observations=80,
        correct_observations=72,
        evaluated_at=timestamp,
    )

    engine = SourceReliabilityEngine()

    result = engine.evaluate(observation)

    assert result.status == ReliabilityStatus.PARTIAL

    assert result.validation_rate == 0.8
    assert result.accuracy_rate == 0.9
    assert result.reliability == 0.9

    assert result.effective_sample_size == 80
    assert result.is_valid()

    # Fully validated source.
    full = SourceReliabilityObservation(
        source="feed_B",
        total_observations=50,
        validated_observations=50,
        correct_observations=45,
        evaluated_at=timestamp,
    )

    full_result = engine.evaluate(full)

    assert full_result.status == ReliabilityStatus.VALID
    assert full_result.reliability == 0.9
    assert full_result.state == ReliabilityState.ESTABLISHED

    # No validation => no fabricated reliability.
    unvalidated = SourceReliabilityObservation(
        source="feed_C",
        total_observations=50,
        validated_observations=0,
        correct_observations=0,
        evaluated_at=timestamp,
    )

    unvalidated_result = engine.evaluate(unvalidated)

    assert (
        unvalidated_result.status
        == ReliabilityStatus.PARTIAL
    )
    assert unvalidated_result.reliability is None
    assert (
        unvalidated_result.state
        == ReliabilityState.UNASSESSED
    )

    # Bayesian calculation must be explicit.
    bayesian_result = engine.evaluate(
        observation,
        prior_alpha=1.0,
        prior_beta=1.0,
    )

    expected = (72.0 + 1.0) / (80.0 + 1.0 + 1.0)

    assert bayesian_result.reliability == expected
    assert bayesian_result.is_valid()

    # Aggregation is count-based, not average-of-percentages.
    batch_1 = SourceReliabilityObservation(
        source="feed_D",
        total_observations=10,
        validated_observations=10,
        correct_observations=8,
        evaluated_at=timestamp,
    )

    batch_2 = SourceReliabilityObservation(
        source="feed_D",
        total_observations=90,
        validated_observations=90,
        correct_observations=63,
        evaluated_at=timestamp,
    )

    aggregated = engine.aggregate(
        (batch_1, batch_2)
    )

    assert aggregated["feed_D"].total_observations == 100
    assert aggregated["feed_D"].validated_observations == 100
    assert aggregated["feed_D"].correct_observations == 71

    aggregate_result = engine.evaluate(
        aggregated["feed_D"]
    )

    assert aggregate_result.reliability == 0.71

    # Package path must not infer reliability from source names or
    # source agreement.
    item = EvidenceItem(
        evidence_id="E-001",
        evidence_type="price",
        source="feed_A",
        value=100.0,
        observed_at=timestamp,
        market="NSE",
        instrument_id="NIFTY",
        timeframe="1m",
    )

    package = EvidencePackage(
        package_id="PKG-001",
        items=(item,),
    )

    package_results = engine.evaluate_package(package)

    assert "feed_A" in package_results
    assert package_results["feed_A"].reliability is None
    assert (
        package_results["feed_A"].state
        == ReliabilityState.UNASSESSED
    )


__all__ = [
    "ReliabilityStatus",
    "ReliabilityState",
    "SourceReliabilityObservation",
    "SourceReliabilityResult",
    "SourceReliabilityEngine",
    "evaluate_source_reliability",
    "evaluate_package_source_reliability",
]