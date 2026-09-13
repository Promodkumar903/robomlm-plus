"""
ROBOMLM PLUS
Decision Cortex — D4 Relationships

V6 Decision Layer:
    D1 Market Identity
        ↓
    D2 Data Contract
        ↓
    D3 Trust
        ↓
    D4 Relationships
        ↓
    D5 Structure
        ↓
    D6 Flow
        ...

IMPORTANT
---------
This module intentionally does NOT invent a V6 proprietary weighted score.

D4's job is to identify and represent relationships between validated
market variables / instruments / markets while preserving:

    - direction
    - strength
    - relationship type
    - temporal alignment
    - source provenance
    - observation vs derivation
    - conflicts
    - missing/stale data
    - market/instrument identity

The output is designed to be consumed by D5+.

No BUY/SELL decision is generated here.
No future information is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class D4Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class RelationshipType(str, Enum):
    DIRECT = "DIRECT"
    INVERSE = "INVERSE"
    LEAD_LAG = "LEAD_LAG"
    CONDITIONAL = "CONDITIONAL"
    CROSS_MARKET = "CROSS_MARKET"
    CROSS_INSTRUMENT = "CROSS_INSTRUMENT"
    DERIVATIVE_UNDERLYING = "DERIVATIVE_UNDERLYING"
    MICROSTRUCTURE = "MICROSTRUCTURE"
    TEMPORAL = "TEMPORAL"
    UNKNOWN = "UNKNOWN"


class RelationshipDirection(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"


class ConflictStatus(str, Enum):
    NONE = "NONE"
    PRESENT = "PRESENT"


# ---------------------------------------------------------------------------
# EXCEPTIONS
# ---------------------------------------------------------------------------

class D4ValidationError(ValueError):
    """Raised when D4 receives structurally invalid input."""


# ---------------------------------------------------------------------------
# DATA OBJECTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class D4Observation:
    """
    A single validated observation.

    Example:
        NIFTY return and BANKNIFTY return observed over the same interval.
    """

    variable: str
    value: float
    timestamp: datetime

    market_id: Optional[str] = None
    instrument_id: Optional[str] = None
    source_id: Optional[str] = None

    # Freshness / quality metadata
    age_seconds: Optional[float] = None
    valid: bool = True

    # Provenance
    evidence_kind: EvidenceKind = EvidenceKind.OBSERVED
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.variable:
            raise D4ValidationError("variable cannot be empty")

        if not isinstance(self.value, (int, float)) or not isfinite(
            float(self.value)
        ):
            raise D4ValidationError(
                f"Invalid numeric value for {self.variable}: {self.value}"
            )

        if self.timestamp.tzinfo is None:
            raise D4ValidationError(
                f"{self.variable}: timestamp must be timezone-aware"
            )


@dataclass(frozen=True)
class D4Relationship:
    """
    Immutable relationship representation.

    strength is an empirical relationship magnitude, normally [-1, +1]
    when supplied by the caller.

    D4 does NOT interpret a high magnitude as a trading probability.
    """

    left_variable: str
    right_variable: str

    relationship_type: RelationshipType
    direction: RelationshipDirection

    strength: Optional[float]

    timestamp: datetime

    left_market_id: Optional[str] = None
    right_market_id: Optional[str] = None

    left_instrument_id: Optional[str] = None
    right_instrument_id: Optional[str] = None

    lag_seconds: Optional[float] = None

    evidence_kind: EvidenceKind = EvidenceKind.DERIVED
    source_ids: Tuple[str, ...] = ()

    conflict_status: ConflictStatus = ConflictStatus.NONE

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.strength is not None:
            if not isfinite(float(self.strength)):
                raise D4ValidationError("Relationship strength must be finite")

            if not -1.0 <= float(self.strength) <= 1.0:
                raise D4ValidationError(
                    "Relationship strength must be within [-1, +1]"
                )


@dataclass
class D4Result:
    """
    D4 output contract.

    This object is deliberately richer than a single score.
    """

    status: D4Status

    relationships: List[D4Relationship]

    missing_inputs: List[str]
    stale_inputs: List[str]
    conflicts: List[Dict[str, Any]]

    identity: Dict[str, Any]
    contract_version: str

    generated_at: datetime

    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "d4": "RELATIONSHIPS",
            "status": self.status.value,
            "relationships": [
                {
                    **asdict(rel),
                    "relationship_type": rel.relationship_type.value,
                    "direction": rel.direction.value,
                    "evidence_kind": rel.evidence_kind.value,
                    "conflict_status": rel.conflict_status.value,
                }
                for rel in self.relationships
            ],
            "missing_inputs": list(self.missing_inputs),
            "stale_inputs": list(self.stale_inputs),
            "conflicts": list(self.conflicts),
            "identity": dict(self.identity),
            "contract_version": self.contract_version,
            "generated_at": self.generated_at.isoformat(),
            "warnings": list(self.warnings),
        }


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _direction_from_strength(
    strength: Optional[float],
    tolerance: float = 1e-12,
) -> RelationshipDirection:

    if strength is None:
        return RelationshipDirection.UNKNOWN

    if strength > tolerance:
        return RelationshipDirection.POSITIVE

    if strength < -tolerance:
        return RelationshipDirection.NEGATIVE

    return RelationshipDirection.NEUTRAL


def _validate_identity(identity: Mapping[str, Any]) -> List[str]:
    """
    D1/D2 dependency guard.

    D4 must not silently manufacture market identity.
    """

    required = (
        "category",
        "underlying",
        "instrument",
        "contract",
        "venue",
    )

    missing = []

    for key in required:
        value = identity.get(key)

        if value is None or value == "":
            missing.append(key)

    return missing


def _validate_pair_identity(identity: Mapping[str, Any]) -> List[str]:
    """
    Base/quote is mandatory for pair-type identities.

    Explicit N/A is accepted where the dimension does not apply.
    """

    instrument = str(identity.get("instrument", "")).lower()

    pair_like = {
        "forex",
        "fx",
        "spot_fx",
        "crypto_spot",
        "crypto_perpetual",
    }

    category = str(identity.get("category", "")).lower()

    if instrument in pair_like or category in {"forex", "fx"}:
        missing = []

        if identity.get("base_currency") in (None, ""):
            missing.append("base_currency")

        if identity.get("quote_currency") in (None, ""):
            missing.append("quote_currency")

        return missing

    return []


def _same_temporal_window(
    left: D4Observation,
    right: D4Observation,
    max_difference_seconds: float,
) -> bool:

    delta = abs(
        (left.timestamp - right.timestamp).total_seconds()
    )

    return delta <= max_difference_seconds


# ---------------------------------------------------------------------------
# RELATIONSHIP ENGINE
# ---------------------------------------------------------------------------

class D4RelationshipEngine:
    """
    D4 Relationship Mapping Engine.

    Responsibilities
    ----------------
    1. Validate D1 identity dependency.
    2. Validate D2 data availability dependency.
    3. Preserve D3 trust/provenance metadata.
    4. Build relationship objects.
    5. Detect contradictory relationship observations.
    6. Distinguish observed vs derived relationships.
    7. Prevent accidental cross-market contamination.
    8. Prevent future-data leakage.

    Non-responsibilities
    --------------------
    - no directional trade decision
    - no risk score
    - no execution
    - no target/SL/TP
    - no invented confidence
    """

    VERSION = "D4_RELATIONSHIPS_1.0"

    def __init__(
        self,
        *,
        temporal_tolerance_seconds: float = 1.0,
        stale_after_seconds: Optional[float] = None,
        minimum_relationship_strength: float = 0.0,
    ) -> None:

        if temporal_tolerance_seconds < 0:
            raise ValueError(
                "temporal_tolerance_seconds cannot be negative"
            )

        if stale_after_seconds is not None and stale_after_seconds < 0:
            raise ValueError(
                "stale_after_seconds cannot be negative"
            )

        if not 0.0 <= minimum_relationship_strength <= 1.0:
            raise ValueError(
                "minimum_relationship_strength must be within [0, 1]"
            )

        self.temporal_tolerance_seconds = temporal_tolerance_seconds
        self.stale_after_seconds = stale_after_seconds
        self.minimum_relationship_strength = (
            minimum_relationship_strength
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        *,
        identity: Mapping[str, Any],
        observations: Sequence[D4Observation],
        relationships: Optional[Sequence[D4Relationship]] = None,
        now: Optional[datetime] = None,
        missing_inputs: Optional[Iterable[str]] = None,
        conflicts: Optional[Sequence[Mapping[str, Any]]] = None,
    ) -> D4Result:

        evaluation_time = now or _utc_now()

        if evaluation_time.tzinfo is None:
            raise D4ValidationError(
                "now must be timezone-aware"
            )

        # --------------------------------------------------------------
        # D1 IDENTITY GUARD
        # --------------------------------------------------------------

        identity_missing = _validate_identity(identity)

        pair_identity_missing = _validate_pair_identity(identity)

        all_identity_missing = (
            identity_missing + pair_identity_missing
        )

        if all_identity_missing:
            return D4Result(
                status=D4Status.BLOCKED,
                relationships=[],
                missing_inputs=[
                    f"identity.{x}"
                    for x in all_identity_missing
                ],
                stale_inputs=[],
                conflicts=list(conflicts or []),
                identity=dict(identity),
                contract_version=self.VERSION,
                generated_at=evaluation_time,
                warnings=[
                    "D4 blocked: market/instrument identity is incomplete."
                ],
            )

        # --------------------------------------------------------------
        # OBSERVATION VALIDATION
        # --------------------------------------------------------------

        invalid = [
            obs.variable
            for obs in observations
            if not obs.valid
        ]

        if invalid:
            return D4Result(
                status=D4Status.BLOCKED,
                relationships=[],
                missing_inputs=[
                    f"invalid_observation:{x}"
                    for x in invalid
                ],
                stale_inputs=[],
                conflicts=list(conflicts or []),
                identity=dict(identity),
                contract_version=self.VERSION,
                generated_at=evaluation_time,
                warnings=[
                    "D4 blocked: invalid observations supplied."
                ],
            )

        # --------------------------------------------------------------
        # FUTURE DATA GUARD
        # --------------------------------------------------------------

        future_observations = [
            obs.variable
            for obs in observations
            if obs.timestamp > evaluation_time
        ]

        if future_observations:
            return D4Result(
                status=D4Status.BLOCKED,
                relationships=[],
                missing_inputs=[
                    f"future_data:{x}"
                    for x in future_observations
                ],
                stale_inputs=[],
                conflicts=list(conflicts or []),
                identity=dict(identity),
                contract_version=self.VERSION,
                generated_at=evaluation_time,
                warnings=[
                    "D4 blocked: future information detected."
                ],
            )

        # --------------------------------------------------------------
        # STALENESS
        # --------------------------------------------------------------

        stale_inputs = []

        if self.stale_after_seconds is not None:
            for obs in observations:
                age = (
                    obs.age_seconds
                    if obs.age_seconds is not None
                    else (
                        evaluation_time - obs.timestamp
                    ).total_seconds()
                )

                if age > self.stale_after_seconds:
                    stale_inputs.append(obs.variable)

        # --------------------------------------------------------------
        # EXPLICIT MISSING INPUTS
        # --------------------------------------------------------------

        missing = list(missing_inputs or [])

        # --------------------------------------------------------------
        # ACCEPT PRECOMPUTED RELATIONSHIPS
        # --------------------------------------------------------------

        output_relationships = []

        for relationship in relationships or []:

            # Never allow future relationship timestamps.
            if relationship.timestamp > evaluation_time:
                return D4Result(
                    status=D4Status.BLOCKED,
                    relationships=[],
                    missing_inputs=[
                        "future_relationship"
                    ],
                    stale_inputs=stale_inputs,
                    conflicts=list(conflicts or []),
                    identity=dict(identity),
                    contract_version=self.VERSION,
                    generated_at=evaluation_time,
                    warnings=[
                        "D4 blocked: relationship contains future timestamp."
                    ],
                )

            if relationship.strength is not None:
                if abs(float(relationship.strength)) < (
                    self.minimum_relationship_strength
                ):
                    continue

            output_relationships.append(relationship)

        # --------------------------------------------------------------
        # DETECT CONFLICTS
        # --------------------------------------------------------------

        detected_conflicts = self._detect_relationship_conflicts(
            output_relationships
        )

        all_conflicts = list(conflicts or []) + detected_conflicts

        # --------------------------------------------------------------
        # STATUS
        # --------------------------------------------------------------

        if not output_relationships:
            status = D4Status.LIMITED

        elif all_conflicts:
            status = D4Status.LIMITED

        elif missing or stale_inputs:
            status = D4Status.LIMITED

        else:
            status = D4Status.READY

        warnings = []

        if missing:
            warnings.append(
                "Some relationship inputs were explicitly unavailable."
            )

        if stale_inputs:
            warnings.append(
                "Some relationship inputs are stale."
            )

        if all_conflicts:
            warnings.append(
                "Conflicting relationship evidence preserved; "
                "no silent resolution performed."
            )

        return D4Result(
            status=status,
            relationships=output_relationships,
            missing_inputs=missing,
            stale_inputs=stale_inputs,
            conflicts=all_conflicts,
            identity=dict(identity),
            contract_version=self.VERSION,
            generated_at=evaluation_time,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # RELATIONSHIP CONSTRUCTORS
    # ------------------------------------------------------------------

    def build_relationship(
        self,
        *,
        left: D4Observation,
        right: D4Observation,
        relationship_type: RelationshipType,
        strength: Optional[float],
        timestamp: Optional[datetime] = None,
        lag_seconds: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> D4Relationship:

        if timestamp is None:
            timestamp = max(
                left.timestamp,
                right.timestamp,
            )

        if timestamp.tzinfo is None:
            raise D4ValidationError(
                "relationship timestamp must be timezone-aware"
            )

        direction = _direction_from_strength(strength)

        source_ids = tuple(
            source
            for source in (
                left.source_id,
                right.source_id,
            )
            if source
        )

        return D4Relationship(
            left_variable=left.variable,
            right_variable=right.variable,
            relationship_type=relationship_type,
            direction=direction,
            strength=strength,
            timestamp=timestamp,
            left_market_id=left.market_id,
            right_market_id=right.market_id,
            left_instrument_id=left.instrument_id,
            right_instrument_id=right.instrument_id,
            lag_seconds=lag_seconds,
            evidence_kind=EvidenceKind.DERIVED,
            source_ids=source_ids,
            metadata=dict(metadata or {}),
        )

    # ------------------------------------------------------------------
    # PEARSON-LIKE EMPIRICAL RELATIONSHIP
    # ------------------------------------------------------------------

    @staticmethod
    def empirical_linear_relationship(
        left_values: Sequence[float],
        right_values: Sequence[float],
    ) -> Optional[float]:
        """
        Pearson correlation coefficient.

        This is a generic statistical primitive, NOT a proprietary
        ROBOMLM D4 score.

        Returns:
            [-1, +1], or None when mathematically undefined.
        """

        if len(left_values) != len(right_values):
            raise D4ValidationError(
                "left_values and right_values must have equal length"
            )

        if len(left_values) < 2:
            return None

        x = [float(v) for v in left_values]
        y = [float(v) for v in right_values]

        if any(not isfinite(v) for v in x + y):
            raise D4ValidationError(
                "relationship series contains non-finite value"
            )

        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum(
            (a - mean_x) * (b - mean_y)
            for a, b in zip(x, y)
        )

        denom_x = sum(
            (a - mean_x) ** 2
            for a in x
        )

        denom_y = sum(
            (b - mean_y) ** 2
            for b in y
        )

        denominator = (denom_x * denom_y) ** 0.5

        if denominator == 0:
            return None

        return numerator / denominator

    # ------------------------------------------------------------------
    # CROSS-MARKET PROTECTION
    # ------------------------------------------------------------------

    @staticmethod
    def validate_cross_market_pair(
        left: D4Observation,
        right: D4Observation,
    ) -> None:

        if left.market_id is None or right.market_id is None:
            raise D4ValidationError(
                "Cross-market relationship requires market_id "
                "on both observations."
            )

        if left.market_id == right.market_id:
            raise D4ValidationError(
                "Observations belong to the same market; "
                "use same-market relationship type."
            )

    # ------------------------------------------------------------------
    # TEMPORAL ALIGNMENT
    # ------------------------------------------------------------------

    def validate_temporal_alignment(
        self,
        left: D4Observation,
        right: D4Observation,
    ) -> bool:

        return _same_temporal_window(
            left,
            right,
            self.temporal_tolerance_seconds,
        )

    # ------------------------------------------------------------------
    # CONFLICT DETECTION
    # ------------------------------------------------------------------

    @staticmethod
    def _relationship_key(
        relationship: D4Relationship,
    ) -> Tuple[str, str]:

        return tuple(
            sorted(
                (
                    relationship.left_variable,
                    relationship.right_variable,
                )
            )
        )

    def _detect_relationship_conflicts(
        self,
        relationships: Sequence[D4Relationship],
    ) -> List[Dict[str, Any]]:

        grouped: Dict[
            Tuple[str, str],
            List[D4Relationship]
        ] = {}

        for relationship in relationships:
            key = self._relationship_key(relationship)

            grouped.setdefault(key, []).append(
                relationship
            )

        conflicts = []

        for key, group in grouped.items():

            directions = {
                rel.direction
                for rel in group
                if rel.direction
                not in {
                    RelationshipDirection.UNKNOWN,
                    RelationshipDirection.NEUTRAL,
                }
            }

            if (
                RelationshipDirection.POSITIVE in directions
                and RelationshipDirection.NEGATIVE in directions
            ):
                conflicts.append(
                    {
                        "relationship": key,
                        "type": "DIRECTION_CONFLICT",
                        "directions": sorted(
                            direction.value
                            for direction in directions
                        ),
                        "resolution": "PRESERVE_CONFLICT",
                    }
                )

        return conflicts


# ---------------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------------------------------

def evaluate_d4_relationships(
    *,
    identity: Mapping[str, Any],
    observations: Sequence[D4Observation],
    relationships: Optional[Sequence[D4Relationship]] = None,
    now: Optional[datetime] = None,
    missing_inputs: Optional[Iterable[str]] = None,
    conflicts: Optional[Sequence[Mapping[str, Any]]] = None,
    temporal_tolerance_seconds: float = 1.0,
    stale_after_seconds: Optional[float] = None,
) -> D4Result:

    engine = D4RelationshipEngine(
        temporal_tolerance_seconds=temporal_tolerance_seconds,
        stale_after_seconds=stale_after_seconds,
    )

    return engine.evaluate(
        identity=identity,
        observations=observations,
        relationships=relationships,
        now=now,
        missing_inputs=missing_inputs,
        conflicts=conflicts,
    )


# ---------------------------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------------------------

def _self_test() -> None:

    now = datetime(
        2026,
        9,
        4,
        9,
        30,
        tzinfo=timezone.utc,
    )

    identity = {
        "category": "Index",
        "underlying": "NIFTY",
        "instrument": "Index Reference",
        "contract": "N/A",
        "venue": "NSE",
    }

    price = D4Observation(
        variable="NIFTY_RETURN",
        value=0.012,
        timestamp=now,
        market_id="NIFTY",
        instrument_id="NIFTY_INDEX",
        source_id="TEST_PRICE",
    )

    banknifty = D4Observation(
        variable="BANKNIFTY_RETURN",
        value=0.015,
        timestamp=now,
        market_id="BANKNIFTY",
        instrument_id="BANKNIFTY_INDEX",
        source_id="TEST_BANK",
    )

    engine = D4RelationshipEngine()

    # Empirical primitive
    correlation = engine.empirical_linear_relationship(
        [1, 2, 3, 4, 5],
        [2, 4, 6, 8, 10],
    )

    assert correlation is not None
    assert abs(correlation - 1.0) < 1e-12

    relationship = engine.build_relationship(
        left=price,
        right=banknifty,
        relationship_type=RelationshipType.CROSS_MARKET,
        strength=correlation,
    )

    result = engine.evaluate(
        identity=identity,
        observations=[price, banknifty],
        relationships=[relationship],
        now=now,
    )

    assert result.status == D4Status.READY
    assert len(result.relationships) == 1
    assert (
        result.relationships[0].direction
        == RelationshipDirection.POSITIVE
    )

    # Future-data attack
    future_obs = D4Observation(
        variable="FUTURE_VALUE",
        value=100.0,
        timestamp=now.replace(hour=10),
        market_id="NIFTY",
        instrument_id="NIFTY_INDEX",
    )

    future_result = engine.evaluate(
        identity=identity,
        observations=[future_obs],
        now=now,
    )

    assert future_result.status == D4Status.BLOCKED

    # Incomplete identity attack
    bad_identity = {
        "category": "Index",
        "underlying": "NIFTY",
        "instrument": "",
        "contract": "N/A",
        "venue": "NSE",
    }

    blocked = engine.evaluate(
        identity=bad_identity,
        observations=[price],
        now=now,
    )

    assert blocked.status == D4Status.BLOCKED

    print("D4 SELF-TEST: PASS")


if __name__ == "__main__":
    _self_test()