from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True)
class OpportunityAssessment:
    symbol: str
    opportunity_score: float
    state: str
    directional_bias: str

    evidence_component: float
    context_component: float
    intelligence_component: float
    magnitude_component: float
    timing_component: float
    risk_component: float
    liquidity_component: float
    alignment_component: float

    evidence_quality_score: float
    component_coverage_pct: float

    contradiction: bool
    decision_ready: bool

    flags: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()
    evidence: tuple[tuple[str, Any], ...] = ()
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "opportunity_score": self.opportunity_score,
            "state": self.state,
            "directional_bias": self.directional_bias,
            "evidence_component": self.evidence_component,
            "context_component": self.context_component,
            "intelligence_component": self.intelligence_component,
            "magnitude_component": self.magnitude_component,
            "timing_component": self.timing_component,
            "risk_component": self.risk_component,
            "liquidity_component": self.liquidity_component,
            "alignment_component": self.alignment_component,
            "evidence_quality_score": self.evidence_quality_score,
            "component_coverage_pct": self.component_coverage_pct,
            "contradiction": self.contradiction,
            "decision_ready": self.decision_ready,
            "flags": list(self.flags),
            "rationale": list(self.rationale),
            "evidence": [
                {"key": key, "value": value}
                for key, value in self.evidence
            ],
            "timestamp": self.timestamp,
        }


class OpportunityIntelligence:
    """
    ROBOMLM Opportunity Intelligence Engine.

    PURPOSE
    -------
    Convert upstream market intelligence into an opportunity-quality
    assessment.

    This engine does not independently create a trade signal.

    It evaluates:

        Evidence
        Market Context
        Intelligence
        Magnitude
        Timing
        Risk
        Liquidity
        Cross-layer Alignment

    CORE OPPORTUNITY FORMULA
    ------------------------
        O =
            0.15E
          + 0.15C
          + 0.20I
          + 0.10M
          + 0.10T
          + 0.10R
          + 0.05L
          + 0.15A

    where every component is [0,100].

    The engine also applies hard gates:

        - minimum evidence quality
        - minimum context
        - minimum intelligence
        - minimum magnitude
        - minimum timing
        - minimum risk quality
        - minimum liquidity
        - minimum alignment
        - no material directional contradiction

    Opportunity score alone is therefore NOT sufficient for
    decision readiness.

    It does not:
        - execute orders
        - authorize orders
        - bypass risk
        - bypass permissions
        - bypass kill switch
        - replace Decision Cortex
    """

    VERSION = "ROBOMLM-OPPORTUNITY-2.0"

    WEIGHTS = {
        "evidence": 0.15,
        "context": 0.15,
        "intelligence": 0.20,
        "magnitude": 0.10,
        "timing": 0.10,
        "risk": 0.10,
        "liquidity": 0.05,
        "alignment": 0.15,
    }

    STATES = {
        "INSUFFICIENT",
        "LOW_QUALITY",
        "DEVELOPING",
        "ACTIONABLE",
        "STRONG",
        "CONFLICTED",
    }

    BIASES = {
        "BUY",
        "SELL",
        "NEUTRAL",
    }

    def __init__(
        self,
        developing_threshold: float = 50.0,
        actionable_threshold: float = 70.0,
        strong_threshold: float = 85.0,
        minimum_evidence: float = 40.0,
        minimum_context: float = 40.0,
        minimum_intelligence: float = 50.0,
        minimum_magnitude: float = 35.0,
        minimum_timing: float = 40.0,
        minimum_risk: float = 40.0,
        minimum_liquidity: float = 30.0,
        minimum_alignment: float = 50.0,
    ) -> None:

        values = {
            "developing_threshold": developing_threshold,
            "actionable_threshold": actionable_threshold,
            "strong_threshold": strong_threshold,
            "minimum_evidence": minimum_evidence,
            "minimum_context": minimum_context,
            "minimum_intelligence": minimum_intelligence,
            "minimum_magnitude": minimum_magnitude,
            "minimum_timing": minimum_timing,
            "minimum_risk": minimum_risk,
            "minimum_liquidity": minimum_liquidity,
            "minimum_alignment": minimum_alignment,
        }

        for name, value in values.items():
            number = self._finite(value)

            if number is None:
                raise ValueError(
                    f"{name} must be numeric"
                )

            if not 0.0 <= number <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )

        if not (
            developing_threshold
            <= actionable_threshold
            <= strong_threshold
        ):
            raise ValueError(
                "opportunity thresholds must be ascending"
            )

        self.developing_threshold = float(
            developing_threshold
        )
        self.actionable_threshold = float(
            actionable_threshold
        )
        self.strong_threshold = float(
            strong_threshold
        )

        self.minimum_evidence = float(
            minimum_evidence
        )
        self.minimum_context = float(
            minimum_context
        )
        self.minimum_intelligence = float(
            minimum_intelligence
        )
        self.minimum_magnitude = float(
            minimum_magnitude
        )
        self.minimum_timing = float(
            minimum_timing
        )
        self.minimum_risk = float(
            minimum_risk
        )
        self.minimum_liquidity = float(
            minimum_liquidity
        )
        self.minimum_alignment = float(
            minimum_alignment
        )

        self._history: list[OpportunityAssessment] = []
        self._lock = RLock()

    # ------------------------------------------------------------------
    # BASIC UTILITIES
    # ------------------------------------------------------------------

    @staticmethod
    def _finite(value: Any) -> float | None:
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if not isfinite(number):
            return None

        return number

    @classmethod
    def _normalize(
        cls,
        value: Any,
        default: float = 0.0,
    ) -> float:
        number = cls._finite(value)

        if number is None:
            return default

        return max(
            0.0,
            min(100.0, number),
        )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    @classmethod
    def _bias(cls, value: Any) -> str:
        normalized = str(value).strip().upper()

        aliases = {
            "BUY": "BUY",
            "BULLISH": "BUY",
            "LONG": "BUY",

            "SELL": "SELL",
            "BEARISH": "SELL",
            "SHORT": "SELL",

            "NEUTRAL": "NEUTRAL",
            "HOLD": "NEUTRAL",
            "NONE": "NEUTRAL",
            "FLAT": "NEUTRAL",
        }

        if normalized not in aliases:
            raise ValueError(
                "directional_bias must resolve to "
                f"{sorted(cls.BIASES)}"
            )

        return aliases[normalized]

    # ------------------------------------------------------------------
    # INPUT EXTRACTION
    # ------------------------------------------------------------------

    @classmethod
    def _raw(
        cls,
        data: Mapping[str, Any],
        *keys: str,
    ) -> tuple[float | None, str | None]:
        for key in keys:
            if key not in data:
                continue

            value = data[key]

            if isinstance(value, Mapping):
                found = False

                for nested in (
                    "score",
                    "strength",
                    "value",
                    "normalized",
                ):
                    if nested in value:
                        value = value[nested]
                        found = True
                        break

                if not found:
                    continue

            number = cls._finite(value)

            if number is not None:
                return number, key

        return None, None

    @classmethod
    def _score(
        cls,
        data: Mapping[str, Any],
        *keys: str,
    ) -> tuple[float | None, str | None]:
        value, source = cls._raw(
            data,
            *keys,
        )

        if value is None:
            return None, None

        return (
            cls._normalize(value),
            source,
        )

    # ------------------------------------------------------------------
    # COMPONENT EXTRACTION
    # ------------------------------------------------------------------

    def _component(
        self,
        data: Mapping[str, Any],
        *keys: str,
    ) -> tuple[float, str | None]:
        value, source = self._score(
            data,
            *keys,
        )

        if value is None:
            return 0.0, None

        return value, source

    def evidence_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "evidence_score",
            "evidence_quality_score",
            "evidence_strength",
            "evidence_quality",
        )

    def context_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "context_score",
            "mci_score",
            "market_context_score",
            "context_quality_score",
        )

    def intelligence_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "intelligence_score",
            "intelligence_quality",
            "intelligence_strength",
        )

    def magnitude_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "magnitude_score",
            "magnitude_strength",
            "magnitude_quality",
        )

    def timing_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "timing_score",
            "timing_quality",
            "timing_strength",
        )

    def risk_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Risk component is always interpreted as RISK QUALITY:

            100 = favorable risk condition
              0 = poor risk condition

        If raw risk is supplied, it is inverted.
        """

        value, source = self._score(
            data,
            "risk_quality_score",
            "risk_context_score",
            "risk_adjusted_score",
        )

        if value is not None:
            return value, source

        raw, raw_source = self._score(
            data,
            "raw_risk_score",
            "risk_exposure",
            "risk_level",
        )

        if raw is not None:
            return (
                100.0 - raw,
                (
                    f"inverse({raw_source})"
                    if raw_source
                    else None
                ),
            )

        return 0.0, None

    def liquidity_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        return self._component(
            data,
            "liquidity_score",
            "liquidity_quality",
            "liquidity_strength",
        )

    # ------------------------------------------------------------------
    # ALIGNMENT
    # ------------------------------------------------------------------

    @classmethod
    def _direction_from_value(
        cls,
        value: Any,
    ) -> str:
        try:
            return cls._bias(value)
        except ValueError:
            return "NEUTRAL"

    def _extract_direction(
        self,
        data: Mapping[str, Any],
        *keys: str,
    ) -> str:
        for key in keys:
            if key not in data:
                continue

            value = data[key]

            if isinstance(value, Mapping):
                value = value.get(
                    "directional_bias",
                    value.get(
                        "direction",
                        value.get(
                            "bias",
                            "NEUTRAL",
                        ),
                    ),
                )

            return self._direction_from_value(
                value
            )

        return "NEUTRAL"

    def calculate_alignment(
        self,
        *,
        directional_bias: str,
        context_bias: str,
        intelligence_bias: str,
        timing_bias: str,
        magnitude_bias: str,
    ) -> tuple[float, bool, tuple[str, ...]]:
        """
        Cross-layer directional alignment.

        A supplied upstream directional bias is compared against
        available directional layers.

        Alignment is based on agreement among available directional
        evidence.

        Returns:
            score
            contradiction
            flags
        """

        target = self._bias(
            directional_bias
        )

        directions = [
            context_bias,
            intelligence_bias,
            timing_bias,
            magnitude_bias,
        ]

        available = [
            self._bias(item)
            for item in directions
            if item in self.BIASES
            and item != "NEUTRAL"
        ]

        if target == "NEUTRAL":
            if not available:
                return (
                    0.0,
                    False,
                    ("NO_DIRECTIONAL_ALIGNMENT",),
                )

            buy = sum(
                1 for item in available
                if item == "BUY"
            )
            sell = sum(
                1 for item in available
                if item == "SELL"
            )

            if buy and sell:
                return (
                    50.0,
                    True,
                    ("DIRECTIONAL_CONFLICT",),
                )

            return (
                70.0,
                False,
                ("UPSTREAM_DIRECTION_NEUTRAL",),
            )

        if not available:
            return (
                0.0,
                False,
                ("NO_DIRECTIONAL_CONFIRMATION",),
            )

        agreements = sum(
            1
            for item in available
            if item == target
        )

        conflicts = sum(
            1
            for item in available
            if item != target
        )

        score = (
            agreements / len(available)
        ) * 100.0

        contradiction = conflicts > agreements

        flags: list[str] = []

        if conflicts:
            flags.append(
                "DIRECTIONAL_DIVERGENCE"
            )

        if contradiction:
            flags.append(
                "DIRECTIONAL_CONFLICT"
            )

        return (
            round(score, 4),
            contradiction,
            tuple(flags),
        )

    # ------------------------------------------------------------------
    # CORE FORMULA
    # ------------------------------------------------------------------

    def calculate_opportunity(
        self,
        *,
        evidence: float,
        context: float,
        intelligence: float,
        magnitude: float,
        timing: float,
        risk: float,
        liquidity: float,
        alignment: float,
    ) -> float:
        """
        Core opportunity formula:

            O =
                0.15E
              + 0.15C
              + 0.20I
              + 0.10M
              + 0.10T
              + 0.10R
              + 0.05L
              + 0.15A
        """

        components = {
            "evidence": self._normalize(evidence),
            "context": self._normalize(context),
            "intelligence": self._normalize(
                intelligence
            ),
            "magnitude": self._normalize(
                magnitude
            ),
            "timing": self._normalize(timing),
            "risk": self._normalize(risk),
            "liquidity": self._normalize(
                liquidity
            ),
            "alignment": self._normalize(
                alignment
            ),
        }

        score = sum(
            components[name]
            * self.WEIGHTS[name]
            for name in self.WEIGHTS
        )

        return round(
            self._normalize(score),
            4,
        )

    # ------------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------------

    def classify(
        self,
        score: float,
        *,
        contradiction: bool = False,
    ) -> str:
        score = self._normalize(score)

        if contradiction:
            return "CONFLICTED"

        if score >= self.strong_threshold:
            return "STRONG"

        if score >= self.actionable_threshold:
            return "ACTIONABLE"

        if score >= self.developing_threshold:
            return "DEVELOPING"

        if score > 0.0:
            return "LOW_QUALITY"

        return "INSUFFICIENT"

    # ------------------------------------------------------------------
    # ASSESSMENT
    # ------------------------------------------------------------------

    def assess(
        self,
        *,
        symbol: str,
        data: Mapping[str, Any],
        directional_bias: str = "NEUTRAL",
    ) -> OpportunityAssessment:

        symbol = str(symbol).strip()

        if not symbol:
            raise ValueError(
                "symbol must not be empty"
            )

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping"
            )

        bias = self._bias(
            directional_bias
        )

        evidence, evidence_source = (
            self.evidence_score(data)
        )

        context, context_source = (
            self.context_score(data)
        )

        intelligence, intelligence_source = (
            self.intelligence_score(data)
        )

        magnitude, magnitude_source = (
            self.magnitude_score(data)
        )

        timing, timing_source = (
            self.timing_score(data)
        )

        risk, risk_source = (
            self.risk_score(data)
        )

        liquidity, liquidity_source = (
            self.liquidity_score(data)
        )

        context_bias = self._extract_direction(
            data,
            "context",
            "market_context",
            "context_intelligence",
            "context_bias",
        )

        intelligence_bias = self._extract_direction(
            data,
            "intelligence",
            "intelligence_result",
            "intelligence_bias",
        )

        timing_bias = self._extract_direction(
            data,
            "timing",
            "timing_intelligence",
            "timing_bias",
        )

        magnitude_bias = self._extract_direction(
            data,
            "magnitude",
            "magnitude_intelligence",
            "magnitude_bias",
        )

        alignment, directional_conflict, alignment_flags = (
            self.calculate_alignment(
                directional_bias=bias,
                context_bias=context_bias,
                intelligence_bias=intelligence_bias,
                timing_bias=timing_bias,
                magnitude_bias=magnitude_bias,
            )
        )

        components = {
            "evidence": evidence,
            "context": context,
            "intelligence": intelligence,
            "magnitude": magnitude,
            "timing": timing,
            "risk": risk,
            "liquidity": liquidity,
            "alignment": alignment,
        }

        sources = {
            "evidence": evidence_source,
            "context": context_source,
            "intelligence": intelligence_source,
            "magnitude": magnitude_source,
            "timing": timing_source,
            "risk": risk_source,
            "liquidity": liquidity_source,
            "alignment": (
                "cross_layer_directional_alignment"
                if alignment > 0.0
                else None
            ),
        }

        opportunity_score = self.calculate_opportunity(
            evidence=evidence,
            context=context,
            intelligence=intelligence,
            magnitude=magnitude,
            timing=timing,
            risk=risk,
            liquidity=liquidity,
            alignment=alignment,
        )

        flags: list[str] = list(
            alignment_flags
        )

        rationale: list[str] = []

        # --------------------------------------------------------------
        # HARD GATES
        # --------------------------------------------------------------

        gates = {
            "evidence": (
                evidence,
                self.minimum_evidence,
            ),
            "context": (
                context,
                self.minimum_context,
            ),
            "intelligence": (
                intelligence,
                self.minimum_intelligence,
            ),
            "magnitude": (
                magnitude,
                self.minimum_magnitude,
            ),
            "timing": (
                timing,
                self.minimum_timing,
            ),
            "risk": (
                risk,
                self.minimum_risk,
            ),
            "liquidity": (
                liquidity,
                self.minimum_liquidity,
            ),
            "alignment": (
                alignment,
                self.minimum_alignment,
            ),
        }

        failed_gates = [
            name
            for name, (
                value,
                minimum,
            ) in gates.items()
            if value < minimum
        ]

        if failed_gates:
            flags.append(
                "OPPORTUNITY_GATE_FAILURE"
            )

            rationale.append(
                "Opportunity gates below minimum: "
                + ", ".join(failed_gates)
            )

        if directional_conflict:
            flags.append(
                "DIRECTIONAL_CONTRADICTION"
            )

            rationale.append(
                "Directional layers contain a material "
                "cross-layer contradiction."
            )

        # --------------------------------------------------------------
        # COMPONENT COVERAGE
        # --------------------------------------------------------------

        available = sum(
            1
            for name in (
                "evidence",
                "context",
                "intelligence",
                "magnitude",
                "timing",
                "risk",
                "liquidity",
            )
            if sources[name] is not None
        )

        coverage = round(
            (
                available / 7.0
            ) * 100.0,
            4,
        )

        if available == 0:
            flags.append(
                "NO_OPPORTUNITY_EVIDENCE"
            )

        elif available < 4:
            flags.append(
                "LOW_COMPONENT_COVERAGE"
            )

        elif available < 7:
            flags.append(
                "PARTIAL_COMPONENT_COVERAGE"
            )

        # --------------------------------------------------------------
        # SPECIAL WARNINGS
        # --------------------------------------------------------------

        if evidence < 40.0:
            flags.append(
                "WEAK_EVIDENCE"
            )

        if context < 40.0:
            flags.append(
                "WEAK_CONTEXT"
            )

        if intelligence < 50.0:
            flags.append(
                "WEAK_INTELLIGENCE"
            )

        if magnitude < 35.0:
            flags.append(
                "WEAK_MAGNITUDE"
            )

        if timing < 40.0:
            flags.append(
                "WEAK_TIMING"
            )

        if risk < 40.0:
            flags.append(
                "POOR_RISK_CONTEXT"
            )

        if liquidity < 30.0:
            flags.append(
                "LIQUIDITY_CONSTRAINT"
            )

        if alignment < 50.0:
            flags.append(
                "WEAK_ALIGNMENT"
            )

        # --------------------------------------------------------------
        # DECISION READY
        # --------------------------------------------------------------

        decision_ready = (
            opportunity_score
            >= self.actionable_threshold
            and evidence
            >= self.minimum_evidence
            and context
            >= self.minimum_context
            and intelligence
            >= self.minimum_intelligence
            and magnitude
            >= self.minimum_magnitude
            and timing
            >= self.minimum_timing
            and risk
            >= self.minimum_risk
            and liquidity
            >= self.minimum_liquidity
            and alignment
            >= self.minimum_alignment
            and not directional_conflict
            and bias in {"BUY", "SELL"}
        )

        if not decision_ready:
            flags.append(
                "NOT_DECISION_READY"
            )

        # --------------------------------------------------------------
        # STATE
        # --------------------------------------------------------------

        state = self.classify(
            opportunity_score,
            contradiction=directional_conflict,
        )

        # A high score with failed hard gates cannot become
        # actionable merely because of the weighted composite.
        if (
            state in {"ACTIONABLE", "STRONG"}
            and not decision_ready
            and not directional_conflict
        ):
            state = "DEVELOPING"

        # --------------------------------------------------------------
        # RATIONALE
        # --------------------------------------------------------------

        if state == "STRONG":
            rationale.append(
                f"Opportunity quality is STRONG at "
                f"{opportunity_score:.2f}."
            )

        elif state == "ACTIONABLE":
            rationale.append(
                f"Opportunity quality is ACTIONABLE at "
                f"{opportunity_score:.2f}."
            )

        elif state == "DEVELOPING":
            rationale.append(
                "Opportunity is developing but one or more "
                "readiness conditions remain incomplete."
            )

        elif state == "LOW_QUALITY":
            rationale.append(
                "Opportunity quality is weak."
            )

        elif state == "CONFLICTED":
            rationale.append(
                "Opportunity contains a directional contradiction."
            )

        else:
            rationale.append(
                "Insufficient evidence exists to classify "
                "a meaningful opportunity."
            )

        if decision_ready:
            rationale.append(
                "All opportunity readiness gates passed and "
                "directional bias is actionable."
            )

        else:
            rationale.append(
                "Opportunity assessment does not authorize execution."
            )

        # --------------------------------------------------------------
        # AUDIT EVIDENCE
        # --------------------------------------------------------------

        evidence = (
            ("evidence_source", evidence_source),
            ("context_source", context_source),
            ("intelligence_source", intelligence_source),
            ("magnitude_source", magnitude_source),
            ("timing_source", timing_source),
            ("risk_source", risk_source),
            ("liquidity_source", liquidity_source),
            ("alignment_source", sources["alignment"]),
            ("context_bias", context_bias),
            ("intelligence_bias", intelligence_bias),
            ("timing_bias", timing_bias),
            ("magnitude_bias", magnitude_bias),
            (
                "formula",
                (
                    "O=0.15E+0.15C+0.20I+0.10M+"
                    "0.10T+0.10R+0.05L+0.15A"
                ),
            ),
            ("version", self.VERSION),
        )

        assessment = OpportunityAssessment(
            symbol=symbol,
            opportunity_score=opportunity_score,
            state=state,
            directional_bias=bias,
            evidence_component=round(
                evidence if isinstance(evidence, (int, float))
                else components["evidence"],
                4,
            ),
            context_component=round(
                components["context"],
                4,
            ),
            intelligence_component=round(
                components["intelligence"],
                4,
            ),
            magnitude_component=round(
                components["magnitude"],
                4,
            ),
            timing_component=round(
                components["timing"],
                4,
            ),
            risk_component=round(
                components["risk"],
                4,
            ),
            liquidity_component=round(
                components["liquidity"],
                4,
            ),
            alignment_component=round(
                components["alignment"],
                4,
            ),
            evidence_quality_score=round(
                components["evidence"],
                4,
            ),
            component_coverage_pct=coverage,
            contradiction=directional_conflict,
            decision_ready=decision_ready,
            flags=tuple(
                dict.fromkeys(flags)
            ),
            rationale=tuple(
                dict.fromkeys(rationale)
            ),
            evidence=(
                ("evidence_source", evidence_source),
                ("context_source", context_source),
                ("intelligence_source", intelligence_source),
                ("magnitude_source", magnitude_source),
                ("timing_source", timing_source),
                ("risk_source", risk_source),
                ("liquidity_source", liquidity_source),
                ("alignment_source", sources["alignment"]),
                ("context_bias", context_bias),
                ("intelligence_bias", intelligence_bias),
                ("timing_bias", timing_bias),
                ("magnitude_bias", magnitude_bias),
                (
                    "formula",
                    (
                        "O=0.15E+0.15C+0.20I+0.10M+"
                        "0.10T+0.10R+0.05L+0.15A"
                    ),
                ),
                ("version", self.VERSION),
            ),
            timestamp=self._timestamp(),
        )

        with self._lock:
            self._history.append(
                assessment
            )

        return assessment

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------

    def latest(
        self,
        symbol: str | None = None,
    ) -> OpportunityAssessment | None:

        with self._lock:
            history = list(
                self._history
            )

        if symbol is not None:
            target = str(symbol).strip()

            history = [
                item
                for item in history
                if item.symbol == target
            ]

        return (
            history[-1]
            if history
            else None
        )

    def history(
        self,
        symbol: str | None = None,
    ) -> list[OpportunityAssessment]:

        with self._lock:
            history = list(
                self._history
            )

        if symbol is None:
            return history

        target = str(symbol).strip()

        return [
            item
            for item in history
            if item.symbol == target
        ]

    def average_score(
        self,
        symbol: str | None = None,
    ) -> float:

        items = self.history(
            symbol
        )

        if not items:
            return 0.0

        return round(
            sum(
                item.opportunity_score
                for item in items
            ) / len(items),
            4,
        )

    def clear(self) -> None:
        with self._lock:
            self._history.clear()

    # ------------------------------------------------------------------
    # HEALTH
    # ------------------------------------------------------------------

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            count = len(
                self._history
            )

        weight_sum = sum(
            self.WEIGHTS.values()
        )

        weights_valid = (
            abs(weight_sum - 1.0)
            < 1e-9
        )

        thresholds_valid = (
            0.0
            <= self.developing_threshold
            <= self.actionable_threshold
            <= self.strong_threshold
            <= 100.0
        )

        minimums = {
            "evidence": self.minimum_evidence,
            "context": self.minimum_context,
            "intelligence": self.minimum_intelligence,
            "magnitude": self.minimum_magnitude,
            "timing": self.minimum_timing,
            "risk": self.minimum_risk,
            "liquidity": self.minimum_liquidity,
            "alignment": self.minimum_alignment,
        }

        minimums_valid = all(
            0.0 <= value <= 100.0
            for value in minimums.values()
        )

        return {
            "healthy": (
                weights_valid
                and thresholds_valid
                and minimums_valid
            ),
            "engine": self.__class__.__name__,
            "version": self.VERSION,
            "assessment_count": count,
            "weights": dict(self.WEIGHTS),
            "weights_sum": round(
                weight_sum,
                6,
            ),
            "weights_valid": weights_valid,
            "thresholds_valid": thresholds_valid,
            "minimums_valid": minimums_valid,
            "thresholds": {
                "developing": self.developing_threshold,
                "actionable": self.actionable_threshold,
                "strong": self.strong_threshold,
            },
            "minimum_gates": minimums,
            "execution_authorized": False,
            "risk_bypass": False,
            "authorization_bypass": False,
        }


__all__ = [
    "OpportunityAssessment",
    "OpportunityIntelligence",
]