from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp, isfinite
from typing import Any, Iterable, Mapping, Sequence

from schemas.evidence.evidence_item import EvidenceItem

try:
    from app.intelligence.evidence.evidence_engine_base import (
        EvidenceStatus,
    )
except ImportError:
    class EvidenceStatus:
        VALID = "VALID"
        PARTIAL = "PARTIAL"
        INSUFFICIENT = "INSUFFICIENT"
        INVALID = "INVALID"


class ConfidenceStatus:
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EvidenceConfidenceParameters:
    """
    Explicit parameters for EQ-0009.

    n0:
        Reference/minimum sample size used by the sample-size adjustment.

    lambda_w:
        Exponential evidence-decay rate.

    eta:
        Learning/update coefficient.

    All parameters are supplied explicitly. No production default
    intelligence constants are hidden inside the calculation.
    """

    n0: float
    lambda_w: float
    eta: float

    def validate(self) -> None:
        if not isfinite(self.n0) or self.n0 <= 0:
            raise ValueError("n0 must be finite and > 0")

        if not isfinite(self.lambda_w) or self.lambda_w < 0:
            raise ValueError("lambda_w must be finite and >= 0")

        if not isfinite(self.eta) or not 0 <= self.eta <= 1:
            raise ValueError("eta must be finite and within [0, 1]")


@dataclass(frozen=True)
class EvidenceConfidenceResult:
    status: str

    weight: float | None
    prior_weight: float | None
    posterior_weight: float | None
    sample_adjustment: float | None
    decay_factor: float | None
    evidence_contribution: float | None

    observation_count: int
    evidence_count: int

    observed_at: datetime | None
    evaluated_at: datetime

    calculation: Mapping[str, Any]
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def is_valid(self) -> bool:
        return (
            self.status == ConfidenceStatus.VALID
            and self.weight is not None
            and 0.0 <= self.weight <= 1.0
        )


class EvidenceConfidenceEngine:
    """
    EQ-0009 Evidence Weight / Confidence Engine.

    Mathematical foundation
    ------------------------
    Bayesian posterior:

        W_posterior =
            W_prior * L(E)
            ---------------------------------
            W_prior * L(E) + (1-W_prior) * L(~E)

    Decayed evidence contribution:

        W_decay =
            W_prior * exp(-lambda_w * T)
            +
            eta * sum(
                E_i * exp(-lambda_w * (T-T_i))
            )

    Sample-size adjustment:

        A_n = n / (n + n0)

    Final simplified weight:

        W =
            A_n * W_decay

    This engine deliberately keeps the Bayesian and decay/sample-size
    components explicit so downstream audit can inspect every term.
    """

    ENGINE_NAME = "EvidenceConfidenceEngine"
    ENGINE_VERSION = "1.0"
    EQUATION_ID = "EQ-0009"

    def calculate(
        self,
        *,
        prior_weight: float,
        evidence_strength: float | None = None,
        likelihood_evidence: float | None = None,
        likelihood_alternative: float | None = None,
        observations: int,
        parameters: EvidenceConfidenceParameters,
        elapsed_time: float = 0.0,
        evidence_events: Sequence[tuple[float, float]] = (),
    ) -> EvidenceConfidenceResult:
        """
        Calculate EQ-0009 for a single current evidence update.

        `evidence_events` contains:
            (evidence_strength, age)

        where:
            evidence_strength âˆˆ [0,1]
            age >= 0

        If likelihoods are supplied, Bayesian posterior is calculated.
        Otherwise the supplied prior is used as the base weight.

        The calculation never fabricates likelihoods or evidence strength.
        """

        evaluated_at = datetime.now(timezone.utc)
        errors: list[str] = []
        warnings: list[str] = []

        try:
            parameters.validate()
        except ValueError as exc:
            return self._invalid(
                evaluated_at,
                str(exc),
                observations,
                len(evidence_events),
            )

        if not self._bounded(prior_weight):
            return self._invalid(
                evaluated_at,
                "prior_weight must be within [0, 1]",
                observations,
                len(evidence_events),
            )

        if observations <= 0:
            return self._insufficient(
                evaluated_at,
                "observations must be > 0",
                observations,
                len(evidence_events),
            )

        if not isfinite(elapsed_time) or elapsed_time < 0:
            return self._invalid(
                evaluated_at,
                "elapsed_time must be finite and >= 0",
                observations,
                len(evidence_events),
            )

        # --------------------------------------------------------------
        # Step 1: Bayesian update
        # --------------------------------------------------------------

        if likelihood_evidence is not None or likelihood_alternative is not None:
            if likelihood_evidence is None or likelihood_alternative is None:
                return self._invalid(
                    evaluated_at,
                    "Both likelihood_evidence and likelihood_alternative "
                    "are required for Bayesian update.",
                    observations,
                    len(evidence_events),
                )

            if not self._probability(likelihood_evidence):
                return self._invalid(
                    evaluated_at,
                    "likelihood_evidence must be within [0, 1]",
                    observations,
                    len(evidence_events),
                )

            if not self._probability(likelihood_alternative):
                return self._invalid(
                    evaluated_at,
                    "likelihood_alternative must be within [0, 1]",
                    observations,
                    len(evidence_events),
                )

            denominator = (
                prior_weight * likelihood_evidence
                + (1.0 - prior_weight) * likelihood_alternative
            )

            if denominator <= 0:
                return self._invalid(
                    evaluated_at,
                    "Bayesian denominator is zero; posterior undefined.",
                    observations,
                    len(evidence_events),
                )

            posterior_weight = (
                prior_weight * likelihood_evidence
            ) / denominator

        else:
            posterior_weight = prior_weight
            warnings.append(
                "No likelihood pair supplied; Bayesian posterior equals "
                "the supplied prior weight."
            )

        # --------------------------------------------------------------
        # Step 2: Validate current evidence strength
        # --------------------------------------------------------------

        if evidence_strength is not None:
            if not self._bounded(evidence_strength):
                return self._invalid(
                    evaluated_at,
                    "evidence_strength must be within [0, 1]",
                    observations,
                    len(evidence_events),
                )

        # --------------------------------------------------------------
        # Step 3: Validate evidence events
        # --------------------------------------------------------------

        validated_events: list[tuple[float, float]] = []

        for index, event in enumerate(evidence_events):
            if len(event) != 2:
                return self._invalid(
                    evaluated_at,
                    f"evidence_events[{index}] must contain "
                    "(evidence_strength, age)",
                    observations,
                    len(evidence_events),
                )

            strength, age = event

            if not self._bounded(strength):
                return self._invalid(
                    evaluated_at,
                    f"evidence_events[{index}] strength must be within [0, 1]",
                    observations,
                    len(evidence_events),
                )

            if not isfinite(age) or age < 0:
                return self._invalid(
                    evaluated_at,
                    f"evidence_events[{index}] age must be finite and >= 0",
                    observations,
                    len(evidence_events),
                )

            validated_events.append((strength, age))

        # --------------------------------------------------------------
        # Step 4: Exponential decay
        # --------------------------------------------------------------

        decay_factor = exp(
            -parameters.lambda_w * elapsed_time
        )

        prior_decayed = posterior_weight * decay_factor

        evidence_contribution = 0.0

        for strength, age in validated_events:
            evidence_contribution += (
                parameters.eta
                * strength
                * exp(-parameters.lambda_w * age)
            )

        # Current evidence can be represented as an event at current time.
        if evidence_strength is not None:
            evidence_contribution += (
                parameters.eta * evidence_strength
            )

        decayed_weight = (
            prior_decayed
            + evidence_contribution
        )

        # --------------------------------------------------------------
        # Step 5: Sample-size adjustment
        # --------------------------------------------------------------

        sample_adjustment = (
            observations
            / (observations + parameters.n0)
        )

        final_weight = (
            sample_adjustment
            * decayed_weight
        )

        # EQ-0009 domain requires [0,1].
        # This is a domain boundary, not an intelligence threshold.
        final_weight = self._bounded_domain(final_weight)

        if len(validated_events) == 0 and evidence_strength is None:
            warnings.append(
                "No new evidence event supplied; only prior decay and "
                "sample-size adjustment were applied."
            )

        if observations < parameters.n0:
            warnings.append(
                "Observation count is below the reference sample size; "
                "sample-size adjustment is therefore below 0.5."
            )

        calculation = {
            "equation_id": self.EQUATION_ID,
            "prior_weight": prior_weight,
            "posterior_weight": posterior_weight,
            "likelihood_evidence": likelihood_evidence,
            "likelihood_alternative": likelihood_alternative,
            "elapsed_time": elapsed_time,
            "lambda_w": parameters.lambda_w,
            "decay_factor": decay_factor,
            "evidence_strength": evidence_strength,
            "evidence_event_count": len(validated_events),
            "evidence_contribution": evidence_contribution,
            "observations": observations,
            "n0": parameters.n0,
            "sample_adjustment": sample_adjustment,
            "eta": parameters.eta,
            "decayed_weight": decayed_weight,
            "final_weight": final_weight,
        }

        return EvidenceConfidenceResult(
            status=ConfidenceStatus.VALID,
            weight=final_weight,
            prior_weight=prior_weight,
            posterior_weight=posterior_weight,
            sample_adjustment=sample_adjustment,
            decay_factor=decay_factor,
            evidence_contribution=evidence_contribution,
            observation_count=observations,
            evidence_count=len(validated_events)
            + (1 if evidence_strength is not None else 0),
            observed_at=None,
            evaluated_at=evaluated_at,
            calculation=calculation,
            errors=tuple(errors),
            warnings=tuple(warnings),
        )

    # ------------------------------------------------------------------
    # EvidenceItem integration
    # ------------------------------------------------------------------

    def calculate_from_items(
        self,
        items: Iterable[EvidenceItem],
        *,
        prior_weight: float,
        observations: int | None = None,
        parameters: EvidenceConfidenceParameters,
        evaluation_time: datetime | None = None,
    ) -> EvidenceConfidenceResult:
        """
        Calculate evidence weight from canonical EvidenceItem objects.

        Important:
        EvidenceItem.confidence is treated as an already supplied
        evidence strength only when explicitly present.

        Missing confidence is NOT converted to zero and is NOT guessed.
        """

        materialized = tuple(items)

        if not materialized:
            return self._insufficient(
                datetime.now(timezone.utc),
                "No evidence items supplied.",
                0,
                0,
            )

        invalid_items = [
            item
            for item in materialized
            if not isinstance(item, EvidenceItem) or not item.is_valid()
        ]

        if invalid_items:
            return self._invalid(
                datetime.now(timezone.utc),
                "One or more EvidenceItems failed structural validation.",
                len(materialized),
                0,
            )

        reference_time = (
            evaluation_time.astimezone(timezone.utc)
            if evaluation_time is not None
            else datetime.now(timezone.utc)
        )

        strengths: list[tuple[float, float]] = []
        missing_strength = 0

        for item in materialized:
            if item.confidence is None:
                missing_strength += 1
                continue

            strength = item.confidence / 100.0

            age = (
                reference_time
                - item.observed_at.astimezone(timezone.utc)
            ).total_seconds()

            if age < 0:
                return self._invalid(
                    datetime.now(timezone.utc),
                    "Evidence item observed_at is in the future "
                    "relative to evaluation_time.",
                    len(materialized),
                    len(strengths),
                )

            strengths.append((strength, age))

        if not strengths:
            return self._insufficient(
                datetime.now(timezone.utc),
                "No EvidenceItem contains explicit confidence/evidence "
                "strength. Confidence cannot be invented.",
                observations or len(materialized),
                0,
            )

        result = self.calculate(
            prior_weight=prior_weight,
            observations=(
                observations
                if observations is not None
                else len(materialized)
            ),
            parameters=parameters,
            elapsed_time=0.0,
            evidence_events=tuple(strengths),
        )

        if missing_strength:
            return EvidenceConfidenceResult(
                status=(
                    ConfidenceStatus.PARTIAL
                    if result.status == ConfidenceStatus.VALID
                    else result.status
                ),
                weight=result.weight,
                prior_weight=result.prior_weight,
                posterior_weight=result.posterior_weight,
                sample_adjustment=result.sample_adjustment,
                decay_factor=result.decay_factor,
                evidence_contribution=result.evidence_contribution,
                observation_count=result.observation_count,
                evidence_count=result.evidence_count,
                observed_at=result.observed_at,
                evaluated_at=result.evaluated_at,
                calculation=result.calculation,
                errors=result.errors,
                warnings=result.warnings
                + (
                    f"{missing_strength} evidence item(s) had no explicit "
                    "confidence and were excluded from strength aggregation.",
                ),
            )

        return result

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    @staticmethod
    def _bounded(value: float) -> bool:
        return isfinite(value) and 0.0 <= value <= 1.0

    @staticmethod
    def _probability(value: float) -> bool:
        return isfinite(value) and 0.0 <= value <= 1.0

    @staticmethod
    def _bounded_domain(value: float) -> float:
        if not isfinite(value):
            raise ValueError("Calculated evidence weight is non-finite.")

        return max(0.0, min(1.0, value))

    def _invalid(
        self,
        evaluated_at: datetime,
        reason: str,
        observations: int,
        evidence_count: int,
    ) -> EvidenceConfidenceResult:
        return EvidenceConfidenceResult(
            status=ConfidenceStatus.INVALID,
            weight=None,
            prior_weight=None,
            posterior_weight=None,
            sample_adjustment=None,
            decay_factor=None,
            evidence_contribution=None,
            observation_count=observations,
            evidence_count=evidence_count,
            observed_at=None,
            evaluated_at=evaluated_at,
            calculation={"equation_id": self.EQUATION_ID},
            errors=(reason,),
        )

    def _insufficient(
        self,
        evaluated_at: datetime,
        reason: str,
        observations: int,
        evidence_count: int,
    ) -> EvidenceConfidenceResult:
        return EvidenceConfidenceResult(
            status=ConfidenceStatus.INSUFFICIENT,
            weight=None,
            prior_weight=None,
            posterior_weight=None,
            sample_adjustment=None,
            decay_factor=None,
            evidence_contribution=None,
            observation_count=observations,
            evidence_count=evidence_count,
            observed_at=None,
            evaluated_at=evaluated_at,
            calculation={"equation_id": self.EQUATION_ID},
            warnings=(reason,),
        )


def calculate_evidence_confidence(
    *,
    prior_weight: float,
    observations: int,
    parameters: EvidenceConfidenceParameters,
    evidence_strength: float | None = None,
    likelihood_evidence: float | None = None,
    likelihood_alternative: float | None = None,
    elapsed_time: float = 0.0,
    evidence_events: Sequence[tuple[float, float]] = (),
) -> EvidenceConfidenceResult:
    return EvidenceConfidenceEngine().calculate(
        prior_weight=prior_weight,
        evidence_strength=evidence_strength,
        likelihood_evidence=likelihood_evidence,
        likelihood_alternative=likelihood_alternative,
        observations=observations,
        parameters=parameters,
        elapsed_time=elapsed_time,
        evidence_events=evidence_events,
    )


__all__ = [
    "ConfidenceStatus",
    "EvidenceConfidenceParameters",
    "EvidenceConfidenceResult",
    "EvidenceConfidenceEngine",
    "calculate_evidence_confidence",
]
