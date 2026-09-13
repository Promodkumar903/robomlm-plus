from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any, Mapping


@dataclass(frozen=True)
class MagnitudeAssessment:
    """
    Immutable output of ROBOMLM Magnitude Intelligence.

    The engine evaluates the potential size/expansion quality of an
    already identified directional market condition.

    Important:
        Magnitude is NOT direction.
        Magnitude is NOT a trade decision.
        Magnitude is NOT execution authorization.

    All component scores are normalized to [0, 100].
    """

    symbol: str

    # Final magnitude intelligence.
    magnitude_score: float
    state: str

    # Estimated measurable movement.
    expected_move_pct: float
    expected_move_source: str

    # Component scores.
    volatility_component: float
    momentum_component: float
    volume_component: float
    liquidity_component: float
    participation_component: float

    # Direction supplied by upstream intelligence.
    directional_bias: str

    # Data / evidence quality.
    component_count: int
    component_coverage_pct: float
    data_quality_score: float

    # Audit information.
    flags: tuple[str, ...] = ()
    rationale: tuple[str, ...] = ()
    evidence: tuple[tuple[str, Any], ...] = ()
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "magnitude_score": self.magnitude_score,
            "state": self.state,
            "expected_move_pct": self.expected_move_pct,
            "expected_move_source": self.expected_move_source,
            "volatility_component": self.volatility_component,
            "momentum_component": self.momentum_component,
            "volume_component": self.volume_component,
            "liquidity_component": self.liquidity_component,
            "participation_component": self.participation_component,
            "directional_bias": self.directional_bias,
            "component_count": self.component_count,
            "component_coverage_pct": self.component_coverage_pct,
            "data_quality_score": self.data_quality_score,
            "flags": list(self.flags),
            "rationale": list(self.rationale),
            "evidence": [
                {"key": key, "value": value}
                for key, value in self.evidence
            ],
            "timestamp": self.timestamp,
        }


class MagnitudeEngine:
    """
    ROBOMLM Magnitude Intelligence Engine.

    PURPOSE
    -------
    Determine whether the market currently has measurable potential for
    a meaningful price expansion/move.

    MAGNITUDE IS MULTI-DIMENSIONAL
    ------------------------------
        Volatility
        Momentum
        Volume
        Liquidity
        Participation

    No single component is allowed to represent the entire magnitude
    condition.

    CORE COMPOSITE
    --------------
        M =

            0.25 * V
          + 0.25 * Mo
          + 0.20 * Vo
          + 0.15 * L
          + 0.15 * P

    where:

        V  = volatility potential
        Mo = momentum strength
        Vo = volume confirmation
        L  = liquidity quality
        P  = participation strength

    All components are [0,100].

    IMPORTANT ENGINE BOUNDARIES
    ----------------------------
    1. Does not create direction.
    2. Does not issue BUY/SELL.
    3. Does not execute orders.
    4. Does not bypass risk.
    5. Does not fabricate expected movement when no measurable
       volatility reference exists.
    6. Explicit inputs take precedence over derived inputs.
    7. Invalid numeric inputs are not silently treated as strong evidence.
    8. Missing components are recorded in the audit output.
    """

    VERSION = "ROBOMLM-MAGNITUDE-2.0"

    WEIGHTS = {
        "volatility": 0.25,
        "momentum": 0.25,
        "volume": 0.20,
        "liquidity": 0.15,
        "participation": 0.15,
    }

    STATES = {
        "INSUFFICIENT",
        "LOW",
        "MODERATE",
        "HIGH",
        "EXTREME",
    }

    BIASES = {
        "BUY",
        "SELL",
        "NEUTRAL",
    }

    # Component values at/below this level are treated as unavailable
    # when determining whether a component was actually supplied.
    MIN_MEASURABLE = 0.0

    def __init__(
        self,
        low_threshold: float = 35.0,
        moderate_threshold: float = 55.0,
        high_threshold: float = 75.0,
        extreme_threshold: float = 90.0,
    ) -> None:

        thresholds = {
            "low_threshold": low_threshold,
            "moderate_threshold": moderate_threshold,
            "high_threshold": high_threshold,
            "extreme_threshold": extreme_threshold,
        }

        for name, value in thresholds.items():
            numeric = self._finite_float(value)

            if numeric is None:
                raise ValueError(f"{name} must be numeric")

            if not 0.0 <= numeric <= 100.0:
                raise ValueError(
                    f"{name} must be between 0 and 100"
                )

        if not (
            low_threshold
            <= moderate_threshold
            <= high_threshold
            <= extreme_threshold
        ):
            raise ValueError(
                "magnitude thresholds must be ascending"
            )

        self.low_threshold = float(low_threshold)
        self.moderate_threshold = float(moderate_threshold)
        self.high_threshold = float(high_threshold)
        self.extreme_threshold = float(extreme_threshold)

        self._history: list[MagnitudeAssessment] = []
        self._lock = RLock()

    # ------------------------------------------------------------------
    # BASIC VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _finite_float(value: Any) -> float | None:
        """
        Convert to finite float.

        NaN and infinity are rejected because they cannot represent
        reliable market evidence.
        """
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            return None

        if not isfinite(result):
            return None

        return result

    @classmethod
    def _normalize(
        cls,
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Normalize any numeric score into [0,100].
        """
        number = cls._finite_float(value)

        if number is None:
            return default

        return max(
            0.0,
            min(100.0, number),
        )

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

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
    def _raw_value(
        cls,
        source: Mapping[str, Any],
        *keys: str,
    ) -> tuple[float | None, str | None]:
        """
        Return the first valid numeric value and its source key.

        Supports scalar values and common structured values:

            {"score": 80}
            {"strength": 80}
            {"value": 80}
            {"normalized": 80}
        """

        for key in keys:
            if key not in source:
                continue

            value = source[key]

            if isinstance(value, Mapping):
                found = False

                for nested_key in (
                    "score",
                    "strength",
                    "value",
                    "normalized",
                ):
                    if nested_key in value:
                        value = value[nested_key]
                        found = True
                        break

                if not found:
                    continue

            number = cls._finite_float(value)

            if number is not None:
                return number, key

        return None, None

    @classmethod
    def _extract_score(
        cls,
        source: Mapping[str, Any],
        *keys: str,
    ) -> tuple[float | None, str | None]:
        """
        Extract a direct score and normalize it.
        """
        value, key = cls._raw_value(
            source,
            *keys,
        )

        if value is None:
            return None, None

        return cls._normalize(value), key

    # ------------------------------------------------------------------
    # RELATIVE METRICS
    # ------------------------------------------------------------------

    @classmethod
    def _relative_ratio_score(
        cls,
        value: float,
        reference: float,
    ) -> float:
        """
        Convert current/reference ratio into [0,100].

        Reference ratio:

            1.0 -> 50

        Above reference increases the score.
        Below reference decreases the score.

        The transformation is intentionally bounded.
        """

        if value < 0.0 or reference <= 0.0:
            return 0.0

        ratio = value / reference

        return cls._normalize(
            ratio * 50.0
        )

    @classmethod
    def _absolute_magnitude_score(
        cls,
        value: float,
        *,
        scale: float,
    ) -> float:
        """
        Convert an absolute percentage-style measurement into
        a bounded magnitude score.

        Example:
            scale=2 means 2% -> 100.

        This is only used when the caller supplies an explicit
        percentage measurement without a reference series.
        """

        if value < 0.0 or scale <= 0.0:
            return 0.0

        return cls._normalize(
            (value / scale) * 100.0
        )

    # ------------------------------------------------------------------
    # VOLATILITY
    # ------------------------------------------------------------------

    def volatility_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Determine volatility potential.

        Priority:

            1. explicit volatility score
            2. ATR vs reference ATR
            3. realized volatility vs reference volatility
            4. explicit volatility score-like value

        Returns:
            (score, source)
        """

        explicit, source = self._extract_score(
            data,
            "volatility_score",
            "volatility_strength",
            "volatility_potential",
        )

        if explicit is not None:
            return explicit, source

        atr, atr_source = self._raw_value(
            data,
            "atr_pct",
            "atr_percent",
            "atr_percentage",
        )

        reference_atr, reference_source = self._raw_value(
            data,
            "historical_atr_pct",
            "avg_atr_pct",
            "reference_atr_pct",
        )

        if (
            atr is not None
            and reference_atr is not None
            and atr > 0.0
            and reference_atr > 0.0
        ):
            return (
                self._relative_ratio_score(
                    atr,
                    reference_atr,
                ),
                f"{atr_source}/{reference_source}",
            )

        realized, realized_source = self._raw_value(
            data,
            "realized_volatility",
            "realized_vol",
        )

        reference_vol, reference_vol_source = self._raw_value(
            data,
            "reference_volatility",
            "historical_volatility",
            "avg_volatility",
        )

        if (
            realized is not None
            and reference_vol is not None
            and realized > 0.0
            and reference_vol > 0.0
        ):
            return (
                self._relative_ratio_score(
                    realized,
                    reference_vol,
                ),
                f"{realized_source}/{reference_vol_source}",
            )

        volatility, volatility_source = self._raw_value(
            data,
            "volatility",
        )

        if volatility is not None:
            return (
                self._normalize(volatility),
                volatility_source,
            )

        return 0.0, None

    # ------------------------------------------------------------------
    # MOMENTUM
    # ------------------------------------------------------------------

    def momentum_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Determine momentum strength.

        Priority:

            1. explicit momentum score
            2. explicit normalized momentum
            3. percentage return / price change
            4. generic momentum value

        Direction is NOT inferred here.
        Magnitude uses absolute momentum strength.
        """

        explicit, source = self._extract_score(
            data,
            "momentum_score",
            "momentum_strength",
            "momentum_potential",
        )

        if explicit is not None:
            return explicit, source

        momentum_pct, momentum_source = self._raw_value(
            data,
            "momentum_pct",
            "price_change_pct",
            "return_pct",
        )

        if momentum_pct is not None:
            return (
                self._absolute_magnitude_score(
                    abs(momentum_pct),
                    scale=10.0,
                ),
                momentum_source,
            )

        momentum, generic_source = self._raw_value(
            data,
            "momentum",
        )

        if momentum is not None:
            return (
                self._normalize(abs(momentum)),
                generic_source,
            )

        return 0.0, None

    # ------------------------------------------------------------------
    # VOLUME
    # ------------------------------------------------------------------

    def volume_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Determine volume expansion/confirmation.

        Priority:

            1. explicit volume score
            2. relative volume vs normal
            3. normalized volume score/value
        """

        explicit, source = self._extract_score(
            data,
            "volume_score",
            "volume_strength",
            "volume_confirmation",
        )

        if explicit is not None:
            return explicit, source

        relative_volume, rv_source = self._raw_value(
            data,
            "relative_volume",
            "volume_ratio",
            "rv",
        )

        if relative_volume is not None and relative_volume > 0.0:
            return (
                self._relative_ratio_score(
                    relative_volume,
                    1.0,
                ),
                rv_source,
            )

        volume, volume_source = self._raw_value(
            data,
            "volume",
        )

        if volume is not None:
            return (
                self._normalize(volume),
                volume_source,
            )

        return 0.0, None

    # ------------------------------------------------------------------
    # LIQUIDITY
    # ------------------------------------------------------------------

    def liquidity_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Determine liquidity quality.

        Liquidity is a quality/feasibility dimension of magnitude.

        Available sub-dimensions:

            depth
            spread quality
            execution quality

        Only supplied sub-dimensions are aggregated.
        """

        explicit, source = self._extract_score(
            data,
            "liquidity_score",
            "liquidity_strength",
            "liquidity_quality",
        )

        if explicit is not None:
            return explicit, source

        values: list[float] = []
        sources: list[str] = []

        depth, depth_source = self._extract_score(
            data,
            "depth_score",
            "market_depth_score",
        )

        if depth is not None:
            values.append(depth)
            if depth_source:
                sources.append(depth_source)

        spread, spread_source = self._extract_score(
            data,
            "spread_score",
            "spread_quality",
        )

        if spread is not None:
            values.append(spread)
            if spread_source:
                sources.append(spread_source)

        execution, execution_source = self._extract_score(
            data,
            "execution_quality",
            "execution_quality_score",
        )

        if execution is not None:
            values.append(execution)
            if execution_source:
                sources.append(execution_source)

        if values:
            return (
                round(
                    sum(values) / len(values),
                    4,
                ),
                "+".join(sources),
            )

        generic, generic_source = self._extract_score(
            data,
            "liquidity",
        )

        if generic is not None:
            return generic, generic_source

        return 0.0, None

    # ------------------------------------------------------------------
    # PARTICIPATION
    # ------------------------------------------------------------------

    def participation_score(
        self,
        data: Mapping[str, Any],
    ) -> tuple[float, str | None]:
        """
        Determine breadth/participation confirmation.

        Available sub-dimensions:

            breadth
            participation
            confirmation

        Only supplied sub-dimensions are aggregated.
        """

        explicit, source = self._extract_score(
            data,
            "participation_score",
            "participation_strength",
            "participation_quality",
        )

        if explicit is not None:
            return explicit, source

        values: list[float] = []
        sources: list[str] = []

        breadth, breadth_source = self._extract_score(
            data,
            "breadth_score",
            "market_breadth",
        )

        if breadth is not None:
            values.append(breadth)
            if breadth_source:
                sources.append(breadth_source)

        participation, participation_source = self._extract_score(
            data,
            "participation",
            "market_participation",
        )

        if participation is not None:
            values.append(participation)
            if participation_source:
                sources.append(participation_source)

        confirmation, confirmation_source = self._extract_score(
            data,
            "confirmation_score",
            "participation_confirmation",
        )

        if confirmation is not None:
            values.append(confirmation)
            if confirmation_source:
                sources.append(confirmation_source)

        if values:
            return (
                round(
                    sum(values) / len(values),
                    4,
                ),
                "+".join(sources),
            )

        generic, generic_source = self._extract_score(
            data,
            "participation",
        )

        if generic is not None:
            return generic, generic_source

        return 0.0, None

    # ------------------------------------------------------------------
    # CORE MAGNITUDE FORMULA
    # ------------------------------------------------------------------

    def calculate_magnitude(
        self,
        *,
        volatility: float,
        momentum: float,
        volume: float,
        liquidity: float,
        participation: float,
    ) -> float:
        """
        Core ROBOMLM magnitude composite.

            M =
                0.25V
              + 0.25Mo
              + 0.20Vo
              + 0.15L
              + 0.15P

        Every input is normalized to [0,100].
        """

        components = {
            "volatility": self._normalize(volatility),
            "momentum": self._normalize(momentum),
            "volume": self._normalize(volume),
            "liquidity": self._normalize(liquidity),
            "participation": self._normalize(participation),
        }

        score = sum(
            components[name] * weight
            for name, weight in self.WEIGHTS.items()
        )

        return round(
            self._normalize(score),
            4,
        )

    # ------------------------------------------------------------------
    # EXPECTED MOVE
    # ------------------------------------------------------------------

    def estimate_expected_move_pct(
        self,
        data: Mapping[str, Any],
        magnitude_score: float,
    ) -> tuple[float, str]:
        """
        Estimate measurable expected movement.

        Priority:

            1. explicit expected_move_pct
            2. ATR percentage
            3. volatility percentage
            4. no estimate

        The engine deliberately does not manufacture a target when
        there is no measurable movement reference.

        For ATR/volatility based estimates, magnitude acts as a
        bounded expansion factor:

            multiplier =
                0.50 + M/100

        This preserves a measurable volatility reference instead of
        generating a price target from the magnitude score alone.
        """

        explicit, source = self._raw_value(
            data,
            "expected_move_pct",
            "expected_move_percent",
        )

        if explicit is not None and explicit > 0.0:
            return (
                round(
                    explicit,
                    6,
                ),
                source or "expected_move_pct",
            )

        atr, atr_source = self._raw_value(
            data,
            "atr_pct",
            "atr_percent",
            "atr_percentage",
        )

        if atr is not None and atr > 0.0:
            multiplier = (
                0.50
                + (
                    self._normalize(magnitude_score)
                    / 100.0
                )
            )

            return (
                round(
                    atr * multiplier,
                    6,
                ),
                atr_source or "atr_pct",
            )

        volatility_pct, volatility_source = self._raw_value(
            data,
            "volatility_pct",
            "volatility_percent",
        )

        if (
            volatility_pct is not None
            and volatility_pct > 0.0
        ):
            multiplier = (
                0.50
                + (
                    self._normalize(magnitude_score)
                    / 100.0
                )
            )

            return (
                round(
                    volatility_pct * multiplier,
                    6,
                ),
                volatility_source or "volatility_pct",
            )

        return 0.0, "UNAVAILABLE"

    # ------------------------------------------------------------------
    # CLASSIFICATION
    # ------------------------------------------------------------------

    def classify(
        self,
        score: float,
    ) -> str:
        """
        Classify magnitude strength.

            >= extreme -> EXTREME
            >= high    -> HIGH
            >= moderate-> MODERATE
            >= low     -> LOW
            otherwise  -> INSUFFICIENT
        """

        score = self._normalize(score)

        if score >= self.extreme_threshold:
            return "EXTREME"

        if score >= self.high_threshold:
            return "HIGH"

        if score >= self.moderate_threshold:
            return "MODERATE"

        if score >= self.low_threshold:
            return "LOW"

        return "INSUFFICIENT"

    # ------------------------------------------------------------------
    # DATA QUALITY
    # ------------------------------------------------------------------

    @staticmethod
    def _component_quality(
        components: Mapping[str, float],
        sources: Mapping[str, str | None],
    ) -> tuple[int, float]:
        """
        Calculate coverage from measurable components.

        A component is considered available when it has a valid source
        and a score > 0.

        This is a coverage metric, not an independent market signal.
        """

        total = len(components)

        if total == 0:
            return 0, 0.0

        available = sum(
            1
            for name, value in components.items()
            if sources.get(name) is not None
            and value > 0.0
        )

        coverage = (
            available / total
        ) * 100.0

        return (
            available,
            round(coverage, 4),
        )

    @staticmethod
    def _data_quality(
        component_count: int,
        coverage_pct: float,
    ) -> float:
        """
        Component coverage quality.

        Coverage is deliberately transparent:
            5/5 -> 100
            4/5 -> 80
            3/5 -> 60
            2/5 -> 40
            1/5 -> 20
            0/5 -> 0
        """

        if component_count <= 0:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                coverage_pct,
            ),
        )

    # ------------------------------------------------------------------
    # ASSESSMENT
    # ------------------------------------------------------------------

    def assess(
        self,
        *,
        symbol: str,
        data: Mapping[str, Any],
        directional_bias: str = "NEUTRAL",
    ) -> MagnitudeAssessment:
        """
        Produce one complete auditable magnitude assessment.
        """

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

        # --------------------------------------------------------------
        # COMPONENT EXTRACTION
        # --------------------------------------------------------------

        volatility, volatility_source = (
            self.volatility_score(data)
        )

        momentum, momentum_source = (
            self.momentum_score(data)
        )

        volume, volume_source = (
            self.volume_score(data)
        )

        liquidity, liquidity_source = (
            self.liquidity_score(data)
        )

        participation, participation_source = (
            self.participation_score(data)
        )

        components = {
            "volatility": volatility,
            "momentum": momentum,
            "volume": volume,
            "liquidity": liquidity,
            "participation": participation,
        }

        sources = {
            "volatility": volatility_source,
            "momentum": momentum_source,
            "volume": volume_source,
            "liquidity": liquidity_source,
            "participation": participation_source,
        }

        # --------------------------------------------------------------
        # COMPOSITE
        # --------------------------------------------------------------

        magnitude_score = self.calculate_magnitude(
            volatility=volatility,
            momentum=momentum,
            volume=volume,
            liquidity=liquidity,
            participation=participation,
        )

        # --------------------------------------------------------------
        # COVERAGE
        # --------------------------------------------------------------

        component_count, coverage_pct = (
            self._component_quality(
                components,
                sources,
            )
        )

        data_quality = self._data_quality(
            component_count,
            coverage_pct,
        )

        # --------------------------------------------------------------
        # EXPECTED MOVE
        # --------------------------------------------------------------

        expected_move, expected_move_source = (
            self.estimate_expected_move_pct(
                data,
                magnitude_score,
            )
        )

        # --------------------------------------------------------------
        # STATE
        # --------------------------------------------------------------

        state = self.classify(
            magnitude_score
        )

        flags: list[str] = []
        rationale: list[str] = []

        # --------------------------------------------------------------
        # MISSING COMPONENTS
        # --------------------------------------------------------------

        missing = [
            name
            for name, source in sources.items()
            if source is None
        ]

        if missing:
            flags.append(
                "MISSING_MAGNITUDE_COMPONENTS"
            )

            rationale.append(
                "Magnitude evidence is incomplete: "
                + ", ".join(missing)
            )

        # --------------------------------------------------------------
        # LOW QUALITY / COVERAGE
        # --------------------------------------------------------------

        if component_count == 0:
            flags.append(
                "NO_MEASURABLE_MAGNITUDE_EVIDENCE"
            )

            rationale.append(
                "No measurable magnitude component was supplied."
            )

        elif component_count < 3:
            flags.append(
                "LOW_COMPONENT_COVERAGE"
            )

            rationale.append(
                "Fewer than three independent magnitude "
                "components are measurable."
            )

        elif component_count < 5:
            flags.append(
                "PARTIAL_COMPONENT_COVERAGE"
            )

        # --------------------------------------------------------------
        # LIQUIDITY
        # --------------------------------------------------------------

        if liquidity < 30.0:
            flags.append(
                "LIQUIDITY_CONSTRAINT"
            )

            rationale.append(
                "Liquidity quality is low and may constrain "
                "the executable quality of a large move."
            )

        # --------------------------------------------------------------
        # VOLUME
        # --------------------------------------------------------------

        if volume < 30.0:
            flags.append(
                "WEAK_VOLUME_CONFIRMATION"
            )

            rationale.append(
                "Volume does not strongly confirm magnitude expansion."
            )

        # --------------------------------------------------------------
        # PARTICIPATION
        # --------------------------------------------------------------

        if participation < 30.0:
            flags.append(
                "WEAK_PARTICIPATION"
            )

            rationale.append(
                "Participation does not strongly confirm "
                "broad magnitude expansion."
            )

        # --------------------------------------------------------------
        # VOLATILITY
        # --------------------------------------------------------------

        if volatility < 30.0:
            flags.append(
                "LOW_VOLATILITY_SUPPORT"
            )

            rationale.append(
                "Volatility evidence does not strongly support "
                "a large expansion."
            )

        # --------------------------------------------------------------
        # MOMENTUM
        # --------------------------------------------------------------

        if momentum < 30.0:
            flags.append(
                "WEAK_MOMENTUM"
            )

            rationale.append(
                "Momentum does not strongly support expansion."
            )

        # --------------------------------------------------------------
        # EXPECTED MOVE
        # --------------------------------------------------------------

        if expected_move <= 0.0:
            flags.append(
                "EXPECTED_MOVE_UNAVAILABLE"
            )

            rationale.append(
                "No measurable volatility reference was available "
                "for expected-move estimation."
            )

        # --------------------------------------------------------------
        # MAGNITUDE STATE
        # --------------------------------------------------------------

        if state == "EXTREME":
            rationale.append(
                "Magnitude conditions are extremely strong "
                f"with a composite score of {magnitude_score:.2f}."
            )

        elif state == "HIGH":
            rationale.append(
                "Magnitude conditions are strong "
                f"with a composite score of {magnitude_score:.2f}."
            )

        elif state == "MODERATE":
            rationale.append(
                "Magnitude potential is developing but is not "
                "yet at a high expansion level."
            )

        elif state == "LOW":
            rationale.append(
                "Magnitude potential is present but weak."
            )

        else:
            rationale.append(
                "Magnitude evidence is insufficient for a meaningful "
                "expansion classification."
            )

        # --------------------------------------------------------------
        # DIRECTIONAL SEPARATION
        # --------------------------------------------------------------

        if bias == "NEUTRAL":
            rationale.append(
                "Directional bias is neutral; magnitude remains "
                "direction-independent."
            )
        else:
            rationale.append(
                f"Magnitude assessment is associated with upstream "
                f"{bias} directional bias."
            )

        # --------------------------------------------------------------
        # AUDIT EVIDENCE
        # --------------------------------------------------------------

        evidence: tuple[tuple[str, Any], ...] = (
            (
                "volatility_source",
                volatility_source,
            ),
            (
                "momentum_source",
                momentum_source,
            ),
            (
                "volume_source",
                volume_source,
            ),
            (
                "liquidity_source",
                liquidity_source,
            ),
            (
                "participation_source",
                participation_source,
            ),
            (
                "expected_move_source",
                expected_move_source,
            ),
            (
                "formula",
                (
                    "M=0.25V+0.25Mo+0.20Vo+"
                    "0.15L+0.15P"
                ),
            ),
            (
                "version",
                self.VERSION,
            ),
        )

        assessment = MagnitudeAssessment(
            symbol=symbol,
            magnitude_score=magnitude_score,
            state=state,
            expected_move_pct=expected_move,
            expected_move_source=expected_move_source,
            volatility_component=round(
                volatility,
                4,
            ),
            momentum_component=round(
                momentum,
                4,
            ),
            volume_component=round(
                volume,
                4,
            ),
            liquidity_component=round(
                liquidity,
                4,
            ),
            participation_component=round(
                participation,
                4,
            ),
            directional_bias=bias,
            component_count=component_count,
            component_coverage_pct=coverage_pct,
            data_quality_score=round(
                data_quality,
                4,
            ),
            flags=tuple(
                dict.fromkeys(flags)
            ),
            rationale=tuple(
                dict.fromkeys(rationale)
            ),
            evidence=evidence,
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
    ) -> MagnitudeAssessment | None:

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
    ) -> list[MagnitudeAssessment]:

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
                item.magnitude_score
                for item in items
            ) / len(items),
            4,
        )

    # ------------------------------------------------------------------
    # HISTORY MANAGEMENT
    # ------------------------------------------------------------------

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
            <= self.low_threshold
            <= self.moderate_threshold
            <= self.high_threshold
            <= self.extreme_threshold
            <= 100.0
        )

        healthy = (
            weights_valid
            and thresholds_valid
        )

        return {
            "healthy": healthy,
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
            "thresholds": {
                "low": self.low_threshold,
                "moderate": self.moderate_threshold,
                "high": self.high_threshold,
                "extreme": self.extreme_threshold,
            },
            "states": sorted(
                self.STATES
            ),
            "directional_biases": sorted(
                self.BIASES
            ),
            "execution_authorized": False,
            "risk_bypass": False,
        }


__all__ = [
    "MagnitudeAssessment",
    "MagnitudeEngine",
]