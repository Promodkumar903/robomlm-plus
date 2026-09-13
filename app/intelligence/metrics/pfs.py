"""
ROBOMLM_PLUS
PFS â€” Participation Flow Score / Participation Intelligence

V6 UPDATED IMPLEMENTATION
Driven by EQ-0004 mathematical foundation.

===============================================================
EQ-0004 â€” VERIFIED ORDER-FLOW FOUNDATION
===============================================================

Instantaneous Order Flow:

    OF(T) = B(T) - S(T)

Cumulative Order Flow:

    OFcum(T) = Î£ [B(t) - S(t)]

Normalized Order-Flow Imbalance:

    OI(T) = (B(T) - S(T)) / (B(T) + S(T))

Participation Magnitude:

    P(T) = B(T) + S(T)

Domains:

    B >= 0
    S >= 0
    -1 <= OI <= +1

Interpretation:

    OI > 0  -> buying participation dominates
    OI < 0  -> selling participation dominates
    OI = 0  -> balanced participation

===============================================================
V6 ENGINEERING RULES
===============================================================

1. EQ-0004 formulas are preserved.
2. No arbitrary 0..100 PFS score is created.
3. No fabricated confidence is created.
4. No BUY/SELL decision authority exists.
5. Current interval flow is separated from cumulative flow.
6. Temporal ordering is preserved when timestamps are available.
7. Persistence is represented from observable temporal evidence,
   but no invented numerical persistence score is created.
8. Participation quality is exposed as a contextual state/interface,
   not as an invented formula.
9. Participation regime is exposed as an evidence/state interface,
   not as an invented threshold system.
10. D13 receives a normalized PFSState object.
11. Market Memory is exposed through provenance/state fields only;
    this engine does not invent a memory model.
12. Missing context remains None rather than being fabricated.

===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping, Optional, Sequence


ENGINE_NAME = "PFS"
ENGINE_VERSION = "V6"
EQUATION_ID = "EQ-0004"


# =====================================================================
# STATUS
# =====================================================================

class PFSStatus(str, Enum):
    VALID = "VALID"
    INSUFFICIENT = "INSUFFICIENT"
    INVALID = "INVALID"


# =====================================================================
# PARTICIPATION DIRECTION
# =====================================================================

class ParticipationDirection(str, Enum):
    BUYING = "BUYING"
    SELLING = "SELLING"
    BALANCED = "BALANCED"


# =====================================================================
# PERSISTENCE STATE
#
# This is NOT an invented numerical persistence score.
# It is a descriptive temporal state derived from observed
# directional sequence.
# =====================================================================

class ParticipationPersistence(str, Enum):
    NONE = "NONE"
    BUYING = "BUYING"
    SELLING = "SELLING"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


# =====================================================================
# CONTEXT STATES
#
# These are interfaces/state containers only.
# No arbitrary numerical quality/regime score is fabricated.
# =====================================================================

class ParticipationQuality(str, Enum):
    UNKNOWN = "UNKNOWN"
    UNASSESSED = "UNASSESSED"


class ParticipationRegime(str, Enum):
    UNKNOWN = "UNKNOWN"
    UNASSESSED = "UNASSESSED"


# =====================================================================
# OBSERVATION
# =====================================================================

@dataclass(frozen=True)
class PFSObservation:
    """
    One observable aggressive participation observation.

    buy_volume:
        Aggressive buying volume B(T).

    sell_volume:
        Aggressive selling volume S(T).

    timestamp:
        Optional temporal ordering information.

    metadata:
        Optional source/context metadata.

    IMPORTANT:
        Passive liquidity is not interpreted as aggressive
        participation flow.
    """

    buy_volume: float
    sell_volume: float
    timestamp: Optional[Any] = None
    metadata: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:

        if isinstance(self.buy_volume, bool):
            raise TypeError("buy_volume cannot be boolean")

        if isinstance(self.sell_volume, bool):
            raise TypeError("sell_volume cannot be boolean")

        if not isinstance(self.buy_volume, (int, float)):
            raise TypeError("buy_volume must be numeric")

        if not isinstance(self.sell_volume, (int, float)):
            raise TypeError("sell_volume must be numeric")

        buy = float(self.buy_volume)
        sell = float(self.sell_volume)

        if not isfinite(buy):
            raise ValueError("buy_volume must be finite")

        if not isfinite(sell):
            raise ValueError("sell_volume must be finite")

        if buy < 0:
            raise ValueError("buy_volume must be >= 0")

        if sell < 0:
            raise ValueError("sell_volume must be >= 0")

        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


# =====================================================================
# D13 NORMALIZED STATE
# =====================================================================

@dataclass(frozen=True)
class PFSState:
    """
    D13-facing normalized PFS intelligence object.

    This object deliberately preserves raw evidence and descriptive
    states instead of collapsing everything into an arbitrary score.

    participation_strength:
        Raw participation magnitude B+S.

    participation_direction:
        Direction derived from sign(OF).

    participation_persistence:
        Temporal descriptive state derived from observed direction.

    participation_quality:
        Contextual quality state. No fabricated numerical score.

    participation_regime:
        Regime state. No fabricated threshold system.

    All contextual fields may remain UNKNOWN/UNASSESSED until the
    appropriate V6 context engines provide verified evidence.
    """

    participation_strength: Optional[float]
    participation_direction: Optional[ParticipationDirection]
    participation_persistence: ParticipationPersistence
    participation_quality: ParticipationQuality
    participation_regime: ParticipationRegime

    instantaneous_order_flow: Optional[float]
    normalized_order_imbalance: Optional[float]
    cumulative_order_flow: Optional[float]
    cumulative_order_imbalance: Optional[float]

    observation_count: int

    equation_id: str
    source_engine: str
    source_version: str

    market_memory_link: Optional[Mapping[str, Any]] = None
    provenance: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:

        if self.market_memory_link is None:
            object.__setattr__(
                self,
                "market_memory_link",
                {},
            )

        if self.provenance is None:
            object.__setattr__(
                self,
                "provenance",
                {},
            )

    def as_dict(self) -> dict[str, Any]:

        return {
            "participation_strength":
                self.participation_strength,

            "participation_direction":
                (
                    self.participation_direction.value
                    if self.participation_direction is not None
                    else None
                ),

            "participation_persistence":
                self.participation_persistence.value,

            "participation_quality":
                self.participation_quality.value,

            "participation_regime":
                self.participation_regime.value,

            "instantaneous_order_flow":
                self.instantaneous_order_flow,

            "normalized_order_imbalance":
                self.normalized_order_imbalance,

            "cumulative_order_flow":
                self.cumulative_order_flow,

            "cumulative_order_imbalance":
                self.cumulative_order_imbalance,

            "observation_count":
                self.observation_count,

            "equation_id":
                self.equation_id,

            "source_engine":
                self.source_engine,

            "source_version":
                self.source_version,

            "market_memory_link":
                dict(self.market_memory_link),

            "provenance":
                dict(self.provenance),
        }


# =====================================================================
# RESULT
# =====================================================================

@dataclass(frozen=True)
class PFSResult:
    """
    Complete V6 PFS mathematical + intelligence result.

    IMPORTANT SEMANTIC SEPARATION

    instantaneous_*:
        Represents the latest/current observation.

    cumulative_*:
        Represents Î£ across the supplied observation sequence.

    aggregate_*:
        Represents the complete supplied observation set when needed.

    This prevents the previous ambiguity where an aggregate of multiple
    observations was incorrectly labelled instantaneous.
    """

    status: PFSStatus

    direction: Optional[ParticipationDirection]

    buy_volume: float
    sell_volume: float
    total_volume: float

    # Current/latest observation
    current_buy_volume: Optional[float]
    current_sell_volume: Optional[float]
    current_total_volume: Optional[float]

    instantaneous_order_flow: Optional[float]
    normalized_order_imbalance: Optional[float]

    # Aggregate supplied observation set
    aggregate_order_flow: Optional[float]
    aggregate_participation: Optional[float]

    # Cumulative
    cumulative_order_flow: Optional[float]
    cumulative_buy_volume: Optional[float]
    cumulative_sell_volume: Optional[float]
    cumulative_total_volume: Optional[float]
    cumulative_order_imbalance: Optional[float]

    participation_magnitude: Optional[float]

    # Temporal intelligence
    participation_persistence: ParticipationPersistence
    directional_observation_count: int
    buying_observation_count: int
    selling_observation_count: int
    balanced_observation_count: int

    # Context interfaces
    participation_quality: ParticipationQuality
    participation_regime: ParticipationRegime

    observation_count: int

    equation: str
    equation_id: str

    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    engine: str = ENGINE_NAME
    version: str = ENGINE_VERSION

    metadata: Optional[Mapping[str, Any]] = None

    # D13 normalized state
    pfs_state: Optional[PFSState] = None

    def __post_init__(self) -> None:

        if self.metadata is None:
            object.__setattr__(
                self,
                "metadata",
                {},
            )

    @property
    def is_valid(self) -> bool:
        return self.status == PFSStatus.VALID

    @property
    def score(self) -> Optional[float]:
        """
        Deliberately None.

        No verified standalone PFS 0..100 transformation is
        introduced here.
        """
        return None

    def as_dict(self) -> dict[str, Any]:

        return {
            "status":
                self.status.value,

            "direction":
                (
                    self.direction.value
                    if self.direction is not None
                    else None
                ),

            "buy_volume":
                self.buy_volume,

            "sell_volume":
                self.sell_volume,

            "total_volume":
                self.total_volume,

            "current_buy_volume":
                self.current_buy_volume,

            "current_sell_volume":
                self.current_sell_volume,

            "current_total_volume":
                self.current_total_volume,

            "instantaneous_order_flow":
                self.instantaneous_order_flow,

            "normalized_order_imbalance":
                self.normalized_order_imbalance,

            "aggregate_order_flow":
                self.aggregate_order_flow,

            "aggregate_participation":
                self.aggregate_participation,

            "cumulative_order_flow":
                self.cumulative_order_flow,

            "cumulative_buy_volume":
                self.cumulative_buy_volume,

            "cumulative_sell_volume":
                self.cumulative_sell_volume,

            "cumulative_total_volume":
                self.cumulative_total_volume,

            "cumulative_order_imbalance":
                self.cumulative_order_imbalance,

            "participation_magnitude":
                self.participation_magnitude,

            "participation_persistence":
                self.participation_persistence.value,

            "directional_observation_count":
                self.directional_observation_count,

            "buying_observation_count":
                self.buying_observation_count,

            "selling_observation_count":
                self.selling_observation_count,

            "balanced_observation_count":
                self.balanced_observation_count,

            "participation_quality":
                self.participation_quality.value,

            "participation_regime":
                self.participation_regime.value,

            "score":
                self.score,

            "observation_count":
                self.observation_count,

            "equation":
                self.equation,

            "equation_id":
                self.equation_id,

            "errors":
                list(self.errors),

            "warnings":
                list(self.warnings),

            "engine":
                self.engine,

            "version":
                self.version,

            "metadata":
                dict(self.metadata),

            "pfs_state":
                (
                    self.pfs_state.as_dict()
                    if self.pfs_state is not None
                    else None
                ),
        }


# =====================================================================
# ENGINE
# =====================================================================

class PFSEngine:
    """
    V6 Participation Flow Engine.

    VERIFIED MATHEMATICAL FOUNDATION

        OF(T) = B(T) - S(T)

        OFcum(T) = Î£[B(t)-S(t)]

        OI(T) = (B(T)-S(T))/(B(T)+S(T))

        Participation(T) = B(T)+S(T)

    The engine preserves:

        magnitude
        direction
        temporal persistence
        cumulative pressure

    without creating an arbitrary composite score.
    """

    INSTANTANEOUS_EQUATION = (
        "OF(T) = B(T) - S(T)"
    )

    CUMULATIVE_EQUATION = (
        "OFcum(T) = Î£[B(t) - S(t)]"
    )

    IMBALANCE_EQUATION = (
        "OI(T) = "
        "(B(T) - S(T)) / "
        "(B(T) + S(T))"
    )

    PARTICIPATION_EQUATION = (
        "Participation(T) = B(T) + S(T)"
    )

    # -----------------------------------------------------------------
    # MAIN
    # -----------------------------------------------------------------

    def calculate(
        self,
        observations: Sequence[PFSObservation],
    ) -> PFSResult:

        if observations is None:
            return self._insufficient(
                count=0,
                reason="No participation observations supplied.",
            )

        observations = tuple(observations)

        if len(observations) == 0:
            return self._insufficient(
                count=0,
                reason=(
                    "At least one participation observation "
                    "is required."
                ),
            )

        errors: list[str] = []

        # -------------------------------------------------------------
        # Validate observation objects
        # -------------------------------------------------------------

        for index, observation in enumerate(observations):

            if not isinstance(
                observation,
                PFSObservation,
            ):
                errors.append(
                    f"observation[{index}] must be PFSObservation"
                )

        if errors:
            return self._invalid(
                count=len(observations),
                errors=errors,
            )

        # -------------------------------------------------------------
        # Preserve temporal order when timestamps are available.
        #
        # We only sort when every observation has a timestamp that
        # exposes timestamp().
        #
        # Otherwise original input order is preserved.
        # -------------------------------------------------------------

        ordered_observations = self._order_observations(
            observations
        )

        # -------------------------------------------------------------
        # Current/latest observation
        # -------------------------------------------------------------

        current = ordered_observations[-1]

        current_buy_volume = float(
            current.buy_volume
        )

        current_sell_volume = float(
            current.sell_volume
        )

        current_total_volume = (
            current_buy_volume
            + current_sell_volume
        )

        # -------------------------------------------------------------
        # EQ-0004 CURRENT / INSTANTANEOUS FLOW
        # -------------------------------------------------------------

        instantaneous_order_flow = (
            current_buy_volume
            - current_sell_volume
        )

        # -------------------------------------------------------------
        # CURRENT OI
        # -------------------------------------------------------------

        if current_total_volume == 0:

            normalized_order_imbalance = 0.0

            direction = (
                ParticipationDirection.BALANCED
            )

        else:

            normalized_order_imbalance = (
                instantaneous_order_flow
                / current_total_volume
            )

            if instantaneous_order_flow > 0:

                direction = (
                    ParticipationDirection.BUYING
                )

            elif instantaneous_order_flow < 0:

                direction = (
                    ParticipationDirection.SELLING
                )

            else:

                direction = (
                    ParticipationDirection.BALANCED
                )

        # -------------------------------------------------------------
        # AGGREGATE / CUMULATIVE
        #
        # Î£[B(t)-S(t)]
        # -------------------------------------------------------------

        buy_volume = sum(
            float(item.buy_volume)
            for item in ordered_observations
        )

        sell_volume = sum(
            float(item.sell_volume)
            for item in ordered_observations
        )

        total_volume = (
            buy_volume
            + sell_volume
        )

        aggregate_order_flow = (
            buy_volume
            - sell_volume
        )

        aggregate_participation = (
            total_volume
        )

        cumulative_buy_volume = buy_volume
        cumulative_sell_volume = sell_volume
        cumulative_total_volume = total_volume

        cumulative_order_flow = (
            cumulative_buy_volume
            - cumulative_sell_volume
        )

        if cumulative_total_volume == 0:

            cumulative_order_imbalance = 0.0

        else:

            cumulative_order_imbalance = (
                cumulative_order_flow
                / cumulative_total_volume
            )

        # -------------------------------------------------------------
        # PARTICIPATION MAGNITUDE
        #
        # Current interval magnitude, not cumulative.
        # -------------------------------------------------------------

        participation_magnitude = (
            current_total_volume
        )

        # -------------------------------------------------------------
        # TEMPORAL PARTICIPATION DIRECTION COUNTS
        # -------------------------------------------------------------

        buying_count = 0
        selling_count = 0
        balanced_count = 0

        for item in ordered_observations:

            flow = (
                float(item.buy_volume)
                - float(item.sell_volume)
            )

            if flow > 0:
                buying_count += 1

            elif flow < 0:
                selling_count += 1

            else:
                balanced_count += 1

        directional_count = (
            buying_count
            + selling_count
        )

        # -------------------------------------------------------------
        # PERSISTENCE
        #
        # No arbitrary numeric persistence score.
        #
        # A state is assigned only from the observed directional
        # sequence.
        # -------------------------------------------------------------

        persistence = self._derive_persistence(
            ordered_observations
        )

        # -------------------------------------------------------------
        # Contextual quality/regime remain unassessed here.
        #
        # These require verified contextual intelligence from the
        # appropriate V6 layers rather than invented PFS formulas.
        # -------------------------------------------------------------

        participation_quality = (
            ParticipationQuality.UNASSESSED
        )

        participation_regime = (
            ParticipationRegime.UNASSESSED
        )

        warnings: list[str] = []

        if current_total_volume == 0:
            warnings.append(
                "No aggressive participation in current observation; "
                "OI=0 by EQ-0004 zero-flow convention."
            )

        if len(ordered_observations) > 1:
            warnings.append(
                "Cumulative values represent the supplied observation "
                "sequence; instantaneous values represent the latest "
                "observation."
            )

        if persistence in (
            ParticipationPersistence.MIXED,
            ParticipationPersistence.UNKNOWN,
        ):
            warnings.append(
                "Temporal sequence does not establish a single "
                "directional persistence state."
            )

        # -------------------------------------------------------------
        # DOMAIN VALIDATION
        # -------------------------------------------------------------

        if not (
            -1.0
            <= normalized_order_imbalance
            <= 1.0
        ):
            return self._invalid(
                count=len(ordered_observations),
                errors=[
                    "Current normalized order imbalance "
                    "left the EQ-0004 [-1,+1] domain."
                ],
            )

        if not (
            -1.0
            <= cumulative_order_imbalance
            <= 1.0
        ):
            return self._invalid(
                count=len(ordered_observations),
                errors=[
                    "Cumulative order imbalance "
                    "left the EQ-0004 [-1,+1] domain."
                ],
            )

        # -------------------------------------------------------------
        # D13 STATE
        # -------------------------------------------------------------

        pfs_state = PFSState(
            participation_strength=(
                participation_magnitude
            ),

            participation_direction=direction,

            participation_persistence=persistence,

            participation_quality=(
                participation_quality
            ),

            participation_regime=(
                participation_regime
            ),

            instantaneous_order_flow=(
                instantaneous_order_flow
            ),

            normalized_order_imbalance=(
                normalized_order_imbalance
            ),

            cumulative_order_flow=(
                cumulative_order_flow
            ),

            cumulative_order_imbalance=(
                cumulative_order_imbalance
            ),

            observation_count=len(
                ordered_observations
            ),

            equation_id=EQUATION_ID,

            source_engine=ENGINE_NAME,

            source_version=ENGINE_VERSION,

            market_memory_link={
                "status": "INTERFACE_ONLY",
                "connected": False,
            },

            provenance={
                "equation_id": EQUATION_ID,
                "formula_foundation":
                    "EQ-0004",
                "score_normalization":
                    "NOT_APPLIED",
                "decision_authority":
                    "NONE",
            },
        )

        # -------------------------------------------------------------
        # RESULT
        # -------------------------------------------------------------

        return PFSResult(
            status=PFSStatus.VALID,

            direction=direction,

            buy_volume=buy_volume,
            sell_volume=sell_volume,
            total_volume=total_volume,

            current_buy_volume=current_buy_volume,
            current_sell_volume=current_sell_volume,
            current_total_volume=current_total_volume,

            instantaneous_order_flow=(
                instantaneous_order_flow
            ),

            normalized_order_imbalance=(
                normalized_order_imbalance
            ),

            aggregate_order_flow=(
                aggregate_order_flow
            ),

            aggregate_participation=(
                aggregate_participation
            ),

            cumulative_order_flow=(
                cumulative_order_flow
            ),

            cumulative_buy_volume=(
                cumulative_buy_volume
            ),

            cumulative_sell_volume=(
                cumulative_sell_volume
            ),

            cumulative_total_volume=(
                cumulative_total_volume
            ),

            cumulative_order_imbalance=(
                cumulative_order_imbalance
            ),

            participation_magnitude=(
                participation_magnitude
            ),

            participation_persistence=(
                persistence
            ),

            directional_observation_count=(
                directional_count
            ),

            buying_observation_count=(
                buying_count
            ),

            selling_observation_count=(
                selling_count
            ),

            balanced_observation_count=(
                balanced_count
            ),

            participation_quality=(
                participation_quality
            ),

            participation_regime=(
                participation_regime
            ),

            observation_count=len(
                ordered_observations
            ),

            equation=self.IMBALANCE_EQUATION,

            equation_id=EQUATION_ID,

            errors=(),

            warnings=tuple(warnings),

            metadata={
                "instantaneous_equation":
                    self.INSTANTANEOUS_EQUATION,

                "cumulative_equation":
                    self.CUMULATIVE_EQUATION,

                "participation_equation":
                    self.PARTICIPATION_EQUATION,

                "score_normalization":
                    "NOT_APPLIED",

                "customer_pfs_0_100":
                    None,

                "direction_source":
                    "sign(OF(T))",

                "cumulative_source":
                    "SUM_OF_OBSERVATION_FLOWS",

                "persistence_source":
                    "TEMPORAL_DIRECTION_SEQUENCE",

                "quality_source":
                    "NOT_ASSESSED",

                "regime_source":
                    "NOT_ASSESSED",

                "decision_authority":
                    "NONE",

                "d13_feed":
                    "PFSState",
            },

            pfs_state=pfs_state,
        )

    # -----------------------------------------------------------------
    # SINGLE INTERVAL API
    # -----------------------------------------------------------------

    def calculate_interval(
        self,
        buy_volume: float,
        sell_volume: float,
    ) -> PFSResult:

        try:

            observation = PFSObservation(
                buy_volume=buy_volume,
                sell_volume=sell_volume,
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            return self._invalid(
                count=0,
                errors=[str(exc)],
            )

        return self.calculate(
            [observation]
        )

    # -----------------------------------------------------------------
    # MAPPING API
    # -----------------------------------------------------------------

    def calculate_from_mapping(
        self,
        data: Mapping[str, Any],
    ) -> PFSResult:

        if not isinstance(
            data,
            Mapping,
        ):

            return self._invalid(
                count=0,
                errors=[
                    "Input must be a mapping."
                ],
            )

        raw_observations = data.get(
            "observations"
        )

        # -------------------------------------------------------------
        # Single observation
        # -------------------------------------------------------------

        if raw_observations is None:

            buy = self._first_present(
                data,
                "buy_volume",
                "buy",
                "aggressive_buy_volume",
                "B",
            )

            sell = self._first_present(
                data,
                "sell_volume",
                "sell",
                "aggressive_sell_volume",
                "S",
            )

            if buy is None:

                return self._invalid(
                    count=0,
                    errors=[
                        "buy_volume is required."
                    ],
                )

            if sell is None:

                return self._invalid(
                    count=0,
                    errors=[
                        "sell_volume is required."
                    ],
                )

            try:

                observation = PFSObservation(
                    buy_volume=buy,
                    sell_volume=sell,
                    timestamp=data.get(
                        "timestamp"
                    ),
                    metadata=data.get(
                        "metadata",
                        {},
                    ),
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                return self._invalid(
                    count=0,
                    errors=[str(exc)],
                )

            return self.calculate(
                [observation]
            )

        # -------------------------------------------------------------
        # Multiple observations
        # -------------------------------------------------------------

        if not isinstance(
            raw_observations,
            Iterable,
        ):

            return self._invalid(
                count=0,
                errors=[
                    "observations must be iterable."
                ],
            )

        observations: list[PFSObservation] = []
        errors: list[str] = []

        for index, item in enumerate(
            raw_observations
        ):

            if isinstance(
                item,
                PFSObservation,
            ):

                observations.append(item)
                continue

            if not isinstance(
                item,
                Mapping,
            ):

                errors.append(
                    f"observation[{index}] "
                    "must be mapping"
                )

                continue

            buy = self._first_present(
                item,
                "buy_volume",
                "buy",
                "aggressive_buy_volume",
                "B",
            )

            sell = self._first_present(
                item,
                "sell_volume",
                "sell",
                "aggressive_sell_volume",
                "S",
            )

            if buy is None:

                errors.append(
                    f"observation[{index}] "
                    "buy_volume missing"
                )

                continue

            if sell is None:

                errors.append(
                    f"observation[{index}] "
                    "sell_volume missing"
                )

                continue

            try:

                observations.append(
                    PFSObservation(
                        buy_volume=buy,
                        sell_volume=sell,
                        timestamp=item.get(
                            "timestamp"
                        ),
                        metadata=item.get(
                            "metadata",
                            {},
                        ),
                    )
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                errors.append(
                    f"observation[{index}]: {exc}"
                )

        if errors:

            return self._invalid(
                count=len(observations),
                errors=errors,
            )

        return self.calculate(
            observations
        )

    # -----------------------------------------------------------------
    # TEMPORAL ORDERING
    # -----------------------------------------------------------------

    @staticmethod
    def _order_observations(
        observations: Sequence[PFSObservation],
    ) -> tuple[PFSObservation, ...]:

        if not observations:
            return tuple()

        # Only sort when all timestamps are present and expose
        # timestamp().

        if not all(
            item.timestamp is not None
            and hasattr(
                item.timestamp,
                "timestamp",
            )
            for item in observations
        ):
            return tuple(observations)

        try:

            return tuple(
                sorted(
                    observations,
                    key=lambda item:
                        item.timestamp.timestamp()
                )
            )

        except Exception:

            # Preserve supplied order rather than guessing.
            return tuple(observations)

    # -----------------------------------------------------------------
    # PERSISTENCE DERIVATION
    # -----------------------------------------------------------------

    @staticmethod
    def _derive_persistence(
        observations: Sequence[PFSObservation],
    ) -> ParticipationPersistence:

        if not observations:
            return ParticipationPersistence.UNKNOWN

        directions: list[
            ParticipationDirection
        ] = []

        for item in observations:

            flow = (
                float(item.buy_volume)
                - float(item.sell_volume)
            )

            if flow > 0:

                directions.append(
                    ParticipationDirection.BUYING
                )

            elif flow < 0:

                directions.append(
                    ParticipationDirection.SELLING
                )

            else:

                directions.append(
                    ParticipationDirection.BALANCED
                )

        directional = [
            direction
            for direction in directions
            if direction
            != ParticipationDirection.BALANCED
        ]

        if not directional:

            return ParticipationPersistence.NONE

        if all(
            direction
            == ParticipationDirection.BUYING
            for direction in directional
        ):

            return ParticipationPersistence.BUYING

        if all(
            direction
            == ParticipationDirection.SELLING
            for direction in directional
        ):

            return ParticipationPersistence.SELLING

        return ParticipationPersistence.MIXED

    # -----------------------------------------------------------------
    # HELPER
    # -----------------------------------------------------------------

    @staticmethod
    def _first_present(
        data: Mapping[str, Any],
        *names: str,
    ) -> Any:

        for name in names:

            if name in data:
                return data[name]

        return None

    # -----------------------------------------------------------------
    # INVALID
    # -----------------------------------------------------------------

    def _invalid(
        self,
        count: int,
        errors: Iterable[str],
    ) -> PFSResult:

        return PFSResult(
            status=PFSStatus.INVALID,

            direction=None,

            buy_volume=0.0,
            sell_volume=0.0,
            total_volume=0.0,

            current_buy_volume=None,
            current_sell_volume=None,
            current_total_volume=None,

            instantaneous_order_flow=None,
            normalized_order_imbalance=None,

            aggregate_order_flow=None,
            aggregate_participation=None,

            cumulative_order_flow=None,
            cumulative_buy_volume=None,
            cumulative_sell_volume=None,
            cumulative_total_volume=None,
            cumulative_order_imbalance=None,

            participation_magnitude=None,

            participation_persistence=(
                ParticipationPersistence.UNKNOWN
            ),

            directional_observation_count=0,
            buying_observation_count=0,
            selling_observation_count=0,
            balanced_observation_count=0,

            participation_quality=(
                ParticipationQuality.UNKNOWN
            ),

            participation_regime=(
                ParticipationRegime.UNKNOWN
            ),

            observation_count=count,

            equation=self.IMBALANCE_EQUATION,

            equation_id=EQUATION_ID,

            errors=tuple(errors),

            warnings=(),
        )

    # -----------------------------------------------------------------
    # INSUFFICIENT
    # -----------------------------------------------------------------

    def _insufficient(
        self,
        count: int,
        reason: str,
    ) -> PFSResult:

        return PFSResult(
            status=PFSStatus.INSUFFICIENT,

            direction=None,

            buy_volume=0.0,
            sell_volume=0.0,
            total_volume=0.0,

            current_buy_volume=None,
            current_sell_volume=None,
            current_total_volume=None,

            instantaneous_order_flow=None,
            normalized_order_imbalance=None,

            aggregate_order_flow=None,
            aggregate_participation=None,

            cumulative_order_flow=None,
            cumulative_buy_volume=None,
            cumulative_sell_volume=None,
            cumulative_total_volume=None,
            cumulative_order_imbalance=None,

            participation_magnitude=None,

            participation_persistence=(
                ParticipationPersistence.UNKNOWN
            ),

            directional_observation_count=0,
            buying_observation_count=0,
            selling_observation_count=0,
            balanced_observation_count=0,

            participation_quality=(
                ParticipationQuality.UNKNOWN
            ),

            participation_regime=(
                ParticipationRegime.UNKNOWN
            ),

            observation_count=count,

            equation=self.IMBALANCE_EQUATION,

            equation_id=EQUATION_ID,

            errors=(),

            warnings=(reason,),
        )


# =====================================================================
# FUNCTIONAL API
# =====================================================================

def calculate_pfs(
    observations: Sequence[PFSObservation],
) -> PFSResult:

    return PFSEngine().calculate(
        observations
    )


def calculate_pfs_interval(
    buy_volume: float,
    sell_volume: float,
) -> PFSResult:

    return PFSEngine().calculate_interval(
        buy_volume=buy_volume,
        sell_volume=sell_volume,
    )


# =====================================================================
# SELF TESTS
# =====================================================================

def _run_self_tests() -> None:

    # -------------------------------------------------------------
    # TEST 1 â€” Pure buying
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        100.0,
        0.0,
    )

    assert result.status == PFSStatus.VALID

    assert result.instantaneous_order_flow == 100.0

    assert result.normalized_order_imbalance == 1.0

    assert (
        result.direction
        == ParticipationDirection.BUYING
    )

    assert (
        result.participation_magnitude
        == 100.0
    )

    # -------------------------------------------------------------
    # TEST 2 â€” Pure selling
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        0.0,
        100.0,
    )

    assert result.instantaneous_order_flow == -100.0

    assert result.normalized_order_imbalance == -1.0

    assert (
        result.direction
        == ParticipationDirection.SELLING
    )

    # -------------------------------------------------------------
    # TEST 3 â€” Balanced
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        100.0,
        100.0,
    )

    assert result.instantaneous_order_flow == 0.0

    assert result.normalized_order_imbalance == 0.0

    assert (
        result.direction
        == ParticipationDirection.BALANCED
    )

    # -------------------------------------------------------------
    # TEST 4 â€” Zero flow
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        0.0,
        0.0,
    )

    assert result.status == PFSStatus.VALID

    assert result.instantaneous_order_flow == 0.0

    assert result.normalized_order_imbalance == 0.0

    assert (
        result.direction
        == ParticipationDirection.BALANCED
    )

    assert (
        result.participation_persistence
        == ParticipationPersistence.NONE
    )

    # -------------------------------------------------------------
    # TEST 5 â€” Exact OI
    # B=75 S=25
    # OF=50
    # OI=0.5
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        75.0,
        25.0,
    )

    assert result.instantaneous_order_flow == 50.0

    assert abs(
        result.normalized_order_imbalance
        - 0.5
    ) < 1e-12

    # -------------------------------------------------------------
    # TEST 6 â€” Cumulative flow
    #
    # (100,50) -> +50
    # (20,80)  -> -60
    #
    # cumulative = -10
    # -------------------------------------------------------------

    result = calculate_pfs(
        [
            PFSObservation(
                buy_volume=100.0,
                sell_volume=50.0,
            ),
            PFSObservation(
                buy_volume=20.0,
                sell_volume=80.0,
            ),
        ]
    )

    assert result.cumulative_order_flow == -10.0

    assert result.cumulative_buy_volume == 120.0

    assert result.cumulative_sell_volume == 130.0

    assert result.cumulative_total_volume == 250.0

    assert abs(
        result.cumulative_order_imbalance
        - (-10.0 / 250.0)
    ) < 1e-12

    # Latest observation remains separate
    assert result.current_buy_volume == 20.0

    assert result.current_sell_volume == 80.0

    assert result.instantaneous_order_flow == -60.0

    assert result.normalized_order_imbalance == -0.6

    # -------------------------------------------------------------
    # TEST 7 â€” Aggregate flow
    # -------------------------------------------------------------

    assert result.aggregate_order_flow == -10.0

    assert result.aggregate_participation == 250.0

    # -------------------------------------------------------------
    # TEST 8 â€” Persistence: all buying
    # -------------------------------------------------------------

    result = calculate_pfs(
        [
            PFSObservation(
                buy_volume=100.0,
                sell_volume=50.0,
            ),
            PFSObservation(
                buy_volume=120.0,
                sell_volume=60.0,
            ),
            PFSObservation(
                buy_volume=150.0,
                sell_volume=50.0,
            ),
        ]
    )

    assert (
        result.participation_persistence
        == ParticipationPersistence.BUYING
    )

    assert result.buying_observation_count == 3

    assert result.selling_observation_count == 0

    # -------------------------------------------------------------
    # TEST 9 â€” Persistence: all selling
    # -------------------------------------------------------------

    result = calculate_pfs(
        [
            PFSObservation(
                buy_volume=50.0,
                sell_volume=100.0,
            ),
            PFSObservation(
                buy_volume=60.0,
                sell_volume=120.0,
            ),
        ]
    )

    assert (
        result.participation_persistence
        == ParticipationPersistence.SELLING
    )

    # -------------------------------------------------------------
    # TEST 10 â€” Persistence: mixed
    # -------------------------------------------------------------

    result = calculate_pfs(
        [
            PFSObservation(
                buy_volume=100.0,
                sell_volume=50.0,
            ),
            PFSObservation(
                buy_volume=40.0,
                sell_volume=80.0,
            ),
        ]
    )

    assert (
        result.participation_persistence
        == ParticipationPersistence.MIXED
    )

    # -------------------------------------------------------------
    # TEST 11 â€” Balanced observations excluded from directional
    # persistence determination
    # -------------------------------------------------------------

    result = calculate_pfs(
        [
            PFSObservation(
                buy_volume=100.0,
                sell_volume=50.0,
            ),
            PFSObservation(
                buy_volume=100.0,
                sell_volume=100.0,
            ),
            PFSObservation(
                buy_volume=120.0,
                sell_volume=60.0,
            ),
        ]
    )

    assert (
        result.participation_persistence
        == ParticipationPersistence.BUYING
    )

    assert result.buying_observation_count == 2

    assert result.balanced_observation_count == 1

    # -------------------------------------------------------------
    # TEST 12 â€” Negative B rejected
    # -------------------------------------------------------------

    failed = False

    try:

        PFSObservation(
            buy_volume=-1.0,
            sell_volume=10.0,
        )

    except ValueError:

        failed = True

    assert failed

    # -------------------------------------------------------------
    # TEST 13 â€” Negative S rejected
    # -------------------------------------------------------------

    failed = False

    try:

        PFSObservation(
            buy_volume=10.0,
            sell_volume=-1.0,
        )

    except ValueError:

        failed = True

    assert failed

    # -------------------------------------------------------------
    # TEST 14 â€” Non-finite values rejected
    # -------------------------------------------------------------

    failed = False

    try:

        PFSObservation(
            buy_volume=float("inf"),
            sell_volume=10.0,
        )

    except ValueError:

        failed = True

    assert failed

    # -------------------------------------------------------------
    # TEST 15 â€” Empty observations
    # -------------------------------------------------------------

    result = calculate_pfs([])

    assert (
        result.status
        == PFSStatus.INSUFFICIENT
    )

    # -------------------------------------------------------------
    # TEST 16 â€” Score remains None
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        60.0,
        40.0,
    )

    assert result.score is None

    # -------------------------------------------------------------
    # TEST 17 â€” Equation identity
    # -------------------------------------------------------------

    assert (
        result.equation_id
        == "EQ-0004"
    )

    assert (
        "B(T) - S(T)"
        in PFSEngine.INSTANTANEOUS_EQUATION
    )

    assert (
        "B(T) + S(T)"
        in PFSEngine.IMBALANCE_EQUATION
    )

    # -------------------------------------------------------------
    # TEST 18 â€” Mapping API
    # -------------------------------------------------------------

    result = PFSEngine().calculate_from_mapping(
        {
            "buy_volume": 80.0,
            "sell_volume": 20.0,
        }
    )

    assert result.status == PFSStatus.VALID

    assert (
        result.normalized_order_imbalance
        == 0.6
    )

    assert (
        result.current_buy_volume
        == 80.0
    )

    # -------------------------------------------------------------
    # TEST 19 â€” Multi-observation mapping
    # -------------------------------------------------------------

    result = PFSEngine().calculate_from_mapping(
        {
            "observations": [
                {
                    "buy_volume": 100.0,
                    "sell_volume": 50.0,
                },
                {
                    "buy_volume": 50.0,
                    "sell_volume": 100.0,
                },
            ]
        }
    )

    assert result.status == PFSStatus.VALID

    assert result.cumulative_order_flow == 0.0

    assert result.cumulative_order_imbalance == 0.0

    # Latest observation is separate
    assert result.instantaneous_order_flow == -50.0

    assert result.normalized_order_imbalance == -1.0 / 3.0

    # -------------------------------------------------------------
    # TEST 20 â€” Direction has no arbitrary threshold
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        50.0001,
        50.0,
    )

    assert (
        result.direction
        == ParticipationDirection.BUYING
    )

    # -------------------------------------------------------------
    # TEST 21 â€” High participation, balanced flow
    # -------------------------------------------------------------

    result = calculate_pfs_interval(
        1_000_000.0,
        1_000_000.0,
    )

    assert (
        result.participation_magnitude
        == 2_000_000.0
    )

    assert (
        result.normalized_order_imbalance
        == 0.0
    )

    assert (
        result.direction
        == ParticipationDirection.BALANCED
    )

    # -------------------------------------------------------------
    # TEST 22 â€” D13 state exists
    # -------------------------------------------------------------

    assert result.pfs_state is not None

    assert (
        result.pfs_state.equation_id
        == "EQ-0004"
    )

    assert (
        result.pfs_state.participation_quality
        == ParticipationQuality.UNASSESSED
    )

    assert (
        result.pfs_state.participation_regime
        == ParticipationRegime.UNASSESSED
    )

    # -------------------------------------------------------------
    # TEST 23 â€” No arbitrary customer score
    # -------------------------------------------------------------

    assert result.score is None

    assert (
        result.pfs_state.provenance[
            "score_normalization"
        ]
        == "NOT_APPLIED"
    )

    # -------------------------------------------------------------
    # TEST 24 â€” No decision authority
    # -------------------------------------------------------------

    assert (
        result.pfs_state.provenance[
            "decision_authority"
        ]
        == "NONE"
    )

    print(
        "PFS V6 EQ-0004 + Participation Intelligence "
        "self-tests: PASS"
    )


# =====================================================================
# EXPORTS
# =====================================================================

__all__ = [
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "EQUATION_ID",

    "PFSStatus",

    "ParticipationDirection",
    "ParticipationPersistence",
    "ParticipationQuality",
    "ParticipationRegime",

    "PFSObservation",
    "PFSState",
    "PFSResult",

    "PFSEngine",

    "calculate_pfs",
    "calculate_pfs_interval",
]


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _run_self_tests()
