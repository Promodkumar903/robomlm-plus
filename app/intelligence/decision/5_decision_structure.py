"""
ROBOMLM_PLUS
Decision Layer — D5 Structure

D5 = STRUCTURE

Purpose
-------
Determine and represent market/instrument structure evidence without
inventing a proprietary score.

Engineering principles
----------------------
1. Identity must be canonical before structure is evaluated.
2. Observed and derived structure are explicitly separated.
3. Missing data is never silently converted to zero.
4. Future observations are rejected.
5. Stale observations may degrade the result.
6. Structural conflicts are preserved and surfaced.
7. No arbitrary 0-100 proprietary score.
8. Structure is evidence for downstream D6+, not a trading decision itself.

D5 conceptual position:
D1 Identity
D2 Data Contract
D3 Trust
D4 Relationships
D5 Structure
D6 Flow
...

This module is intentionally traceable so that BlackBox/live replay can
later replace generic structural primitives with calibrated V6 structure
models without changing the contract.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------

class D5Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class StructureType(str, Enum):
    TREND = "TREND"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    BREAKDOWN = "BREAKDOWN"
    SWING_HIGH = "SWING_HIGH"
    SWING_LOW = "SWING_LOW"
    HIGHER_HIGH = "HIGHER_HIGH"
    HIGHER_LOW = "HIGHER_LOW"
    LOWER_HIGH = "LOWER_HIGH"
    LOWER_LOW = "LOWER_LOW"
    SUPPORT = "SUPPORT"
    RESISTANCE = "RESISTANCE"
    GAP = "GAP"
    CONSOLIDATION = "CONSOLIDATION"
    UNKNOWN = "UNKNOWN"


class StructureDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"


class ConflictStatus(str, Enum):
    NONE = "NONE"
    PRESENT = "PRESENT"


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _age_seconds(observed_at: datetime, evaluation_time: datetime) -> float:
    return max(
        0.0,
        (
            _ensure_utc(evaluation_time)
            - _ensure_utc(observed_at)
        ).total_seconds(),
    )


# ---------------------------------------------------------------------
# DATA CONTRACTS
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class D5Identity:
    """
    Canonical market/instrument identity.

    Required:
        category
        underlying
        instrument
        contract
        venue

    Pair-like instruments additionally require:
        base_currency
        quote_currency
    """

    category: str
    underlying: str
    instrument: str
    contract: str
    venue: str

    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None

    market_profile_version: Optional[str] = None
    instrument_profile_version: Optional[str] = None
    contract_version: Optional[str] = None

    def validate(self) -> List[str]:
        errors: List[str] = []

        required = {
            "category": self.category,
            "underlying": self.underlying,
            "instrument": self.instrument,
            "contract": self.contract,
            "venue": self.venue,
        }

        for name, value in required.items():
            if value is None or str(value).strip() == "":
                errors.append(f"MISSING_IDENTITY:{name}")

        category = str(self.category).upper()
        instrument = str(self.instrument).upper()

        pair_like = (
            "FX" in category
            or "FOREX" in category
            or "FX" in instrument
            or "FOREX" in instrument
            or "PAIR" in instrument
        )

        if pair_like:
            if not self.base_currency:
                errors.append("MISSING_IDENTITY:base_currency")
            if not self.quote_currency:
                errors.append("MISSING_IDENTITY:quote_currency")

        return errors


@dataclass(frozen=True)
class D5Observation:
    """
    Atomic structure observation.

    value is deliberately Any because structural evidence may be:
        - numeric
        - categorical
        - boolean
        - dictionary/object-like metadata

    No automatic coercion to zero is performed.
    """

    name: str
    value: Any
    observed_at: datetime

    market_id: str
    instrument_id: str
    source_id: str

    evidence_kind: EvidenceKind = EvidenceKind.OBSERVED

    valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def age_seconds(self, evaluation_time: datetime) -> float:
        return _age_seconds(self.observed_at, evaluation_time)


@dataclass(frozen=True)
class D5Structure:
    """
    One identified structural feature.
    """

    structure_type: StructureType
    direction: StructureDirection

    name: str

    value: Any

    observed_at: datetime
    market_id: str
    instrument_id: str

    evidence_kind: EvidenceKind = EvidenceKind.DERIVED

    source_ids: Tuple[str, ...] = ()

    strength: Optional[float] = None

    conflict_status: ConflictStatus = ConflictStatus.NONE

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class D5Result:
    status: D5Status

    structures: List[D5Structure] = field(default_factory=list)

    missing_inputs: List[str] = field(default_factory=list)
    stale_inputs: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    identity_errors: List[str] = field(default_factory=list)

    market_id: Optional[str] = None
    instrument_id: Optional[str] = None

    contract_version: Optional[str] = None

    evaluation_time: datetime = field(default_factory=_utc_now)

    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "structures": [
                {
                    "structure_type": s.structure_type.value,
                    "direction": s.direction.value,
                    "name": s.name,
                    "value": s.value,
                    "observed_at": s.observed_at.isoformat(),
                    "market_id": s.market_id,
                    "instrument_id": s.instrument_id,
                    "evidence_kind": s.evidence_kind.value,
                    "source_ids": list(s.source_ids),
                    "strength": s.strength,
                    "conflict_status": s.conflict_status.value,
                    "metadata": dict(s.metadata),
                }
                for s in self.structures
            ],
            "missing_inputs": list(self.missing_inputs),
            "stale_inputs": list(self.stale_inputs),
            "conflicts": list(self.conflicts),
            "identity_errors": list(self.identity_errors),
            "market_id": self.market_id,
            "instrument_id": self.instrument_id,
            "contract_version": self.contract_version,
            "evaluation_time": self.evaluation_time.isoformat(),
            "warnings": list(self.warnings),
        }


# ---------------------------------------------------------------------
# D5 ENGINE
# ---------------------------------------------------------------------

class D5StructureEngine:
    """
    D5 Structure engine.

    This engine does not make a BUY/SELL decision.

    It establishes structural evidence and its validity so downstream
    decision stages can consume it.
    """

    def __init__(
        self,
        *,
        max_age_seconds: Optional[float] = None,
    ) -> None:
        if max_age_seconds is not None and max_age_seconds < 0:
            raise ValueError("max_age_seconds must be >= 0")

        self.max_age_seconds = max_age_seconds

    # -----------------------------------------------------------------
    # MAIN EVALUATION
    # -----------------------------------------------------------------

    def evaluate(
        self,
        *,
        identity: D5Identity,
        observations: Sequence[D5Observation],
        structures: Sequence[D5Structure],
        evaluation_time: Optional[datetime] = None,
        required_inputs: Optional[Sequence[str]] = None,
    ) -> D5Result:

        evaluation_time = _ensure_utc(
            evaluation_time or _utc_now()
        )

        identity_errors = identity.validate()

        result = D5Result(
            status=D5Status.READY,
            market_id=self._canonical_market_id(identity),
            instrument_id=self._canonical_instrument_id(identity),
            contract_version=identity.contract_version,
            evaluation_time=evaluation_time,
            identity_errors=identity_errors,
        )

        # -------------------------------------------------------------
        # Identity guard
        # -------------------------------------------------------------

        if identity_errors:
            result.status = D5Status.BLOCKED
            result.warnings.append(
                "D5_BLOCKED_IDENTITY_NOT_RESOLVED"
            )
            return result

        # -------------------------------------------------------------
        # Required input guard
        # -------------------------------------------------------------

        available_names = {
            str(o.name).strip()
            for o in observations
            if o.valid
        }

        if required_inputs:
            for required in required_inputs:
                if required not in available_names:
                    result.missing_inputs.append(required)

        # -------------------------------------------------------------
        # Observation validation
        # -------------------------------------------------------------

        valid_observations: List[D5Observation] = []

        for obs in observations:

            observed_at = _ensure_utc(obs.observed_at)

            # Future data leakage guard
            if observed_at > evaluation_time:
                result.status = D5Status.BLOCKED
                result.warnings.append(
                    f"FUTURE_DATA_REJECTED:{obs.name}"
                )
                continue

            if not obs.valid:
                result.missing_inputs.append(
                    f"INVALID:{obs.name}"
                )
                continue

            age = obs.age_seconds(evaluation_time)

            if (
                self.max_age_seconds is not None
                and age > self.max_age_seconds
            ):
                result.stale_inputs.append(obs.name)

            valid_observations.append(obs)

        # -------------------------------------------------------------
        # Structural evidence validation
        # -------------------------------------------------------------

        valid_structures: List[D5Structure] = []

        for structure in structures:

            observed_at = _ensure_utc(structure.observed_at)

            # Future structure guard
            if observed_at > evaluation_time:
                result.status = D5Status.BLOCKED
                result.warnings.append(
                    f"FUTURE_STRUCTURE_REJECTED:{structure.name}"
                )
                continue

            # Identity contamination guard
            if (
                structure.market_id != result.market_id
                or structure.instrument_id != result.instrument_id
            ):
                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + structure.name
                )
                continue

            valid_structures.append(structure)

        result.structures.extend(valid_structures)

        # -------------------------------------------------------------
        # Conflict detection
        # -------------------------------------------------------------

        detected_conflicts = self._detect_conflicts(
            valid_structures
        )

        result.conflicts.extend(detected_conflicts)

        if detected_conflicts:
            result.status = D5Status.LIMITED
            result.warnings.append(
                "STRUCTURAL_CONFLICT_PRESENT"
            )

        # -------------------------------------------------------------
        # Missing data
        # -------------------------------------------------------------

        if result.missing_inputs:
            if result.status != D5Status.BLOCKED:
                result.status = D5Status.LIMITED

        # -------------------------------------------------------------
        # Stale data
        # -------------------------------------------------------------

        if result.stale_inputs:
            if result.status != D5Status.BLOCKED:
                result.status = D5Status.LIMITED

        # -------------------------------------------------------------
        # No structural evidence
        # -------------------------------------------------------------

        if not valid_structures:
            if result.status != D5Status.BLOCKED:
                result.status = D5Status.LIMITED

            result.warnings.append(
                "NO_VALID_STRUCTURAL_EVIDENCE"
            )

        return result

    # -----------------------------------------------------------------
    # STRUCTURE BUILDER
    # -----------------------------------------------------------------

    @staticmethod
    def build_structure(
        *,
        structure_type: StructureType,
        direction: StructureDirection,
        name: str,
        value: Any,
        observed_at: datetime,
        market_id: str,
        instrument_id: str,
        evidence_kind: EvidenceKind = EvidenceKind.DERIVED,
        source_ids: Sequence[str] = (),
        strength: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> D5Structure:

        if strength is not None:
            if strength < -1.0 or strength > 1.0:
                raise ValueError(
                    "strength must be between -1 and +1"
                )

        return D5Structure(
            structure_type=structure_type,
            direction=direction,
            name=name,
            value=value,
            observed_at=_ensure_utc(observed_at),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=evidence_kind,
            source_ids=tuple(source_ids),
            strength=strength,
            metadata=dict(metadata or {}),
        )

    # -----------------------------------------------------------------
    # BASIC PRICE-STRUCTURE PRIMITIVES
    # -----------------------------------------------------------------

    @staticmethod
    def classify_swing_sequence(
        *,
        previous_high: float,
        current_high: float,
        previous_low: float,
        current_low: float,
    ) -> Tuple[StructureType, StructureDirection]:

        """
        Deterministic structural primitive.

        HH + HL -> bullish
        LH + LL -> bearish

        Mixed combinations remain MIXED.

        This is a structural classification primitive, NOT a proprietary
        V6 score.
        """

        if current_high > previous_high and current_low > previous_low:
            return (
                StructureType.HIGHER_HIGH,
                StructureDirection.BULLISH,
            )

        if current_high < previous_high and current_low < previous_low:
            return (
                StructureType.LOWER_LOW,
                StructureDirection.BEARISH,
            )

        if (
            current_high > previous_high
            and current_low < previous_low
        ):
            return (
                StructureType.BREAKOUT,
                StructureDirection.MIXED,
            )

        if (
            current_high < previous_high
            and current_low > previous_low
        ):
            return (
                StructureType.RANGE,
                StructureDirection.NEUTRAL,
            )

        return (
            StructureType.UNKNOWN,
            StructureDirection.UNKNOWN,
        )

    # -----------------------------------------------------------------
    # BREAK DETECTION
    # -----------------------------------------------------------------

    @staticmethod
    def detect_level_break(
        *,
        previous_level: float,
        current_price: float,
        level_type: StructureType,
    ) -> Tuple[StructureType, StructureDirection]:

        if level_type == StructureType.RESISTANCE:
            if current_price > previous_level:
                return (
                    StructureType.BREAKOUT,
                    StructureDirection.BULLISH,
                )

        if level_type == StructureType.SUPPORT:
            if current_price < previous_level:
                return (
                    StructureType.BREAKDOWN,
                    StructureDirection.BEARISH,
                )

        return (
            StructureType.UNKNOWN,
            StructureDirection.UNKNOWN,
        )

    # -----------------------------------------------------------------
    # CONFLICT DETECTION
    # -----------------------------------------------------------------

    @staticmethod
    def _detect_conflicts(
        structures: Sequence[D5Structure],
    ) -> List[str]:

        conflicts: List[str] = []

        grouped: Dict[str, List[D5Structure]] = {}

        for structure in structures:
            grouped.setdefault(
                structure.name,
                [],
            ).append(structure)

        for name, items in grouped.items():

            directions = {
                item.direction
                for item in items
                if item.direction
                in {
                    StructureDirection.BULLISH,
                    StructureDirection.BEARISH,
                }
            }

            if (
                StructureDirection.BULLISH in directions
                and StructureDirection.BEARISH in directions
            ):
                conflicts.append(
                    f"DIRECTION_CONFLICT:{name}"
                )

        return conflicts

    # -----------------------------------------------------------------
    # ID HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _canonical_market_id(
        identity: D5Identity,
    ) -> str:

        return "|".join(
            [
                identity.category,
                identity.underlying,
                identity.venue,
            ]
        )

    @staticmethod
    def _canonical_instrument_id(
        identity: D5Identity,
    ) -> str:

        parts = [
            identity.category,
            identity.underlying,
            identity.instrument,
            identity.contract,
            identity.venue,
        ]

        if identity.base_currency:
            parts.append(identity.base_currency)

        if identity.quote_currency:
            parts.append(identity.quote_currency)

        return "|".join(parts)


# ---------------------------------------------------------------------
# CONVENIENCE FUNCTION
# ---------------------------------------------------------------------

def evaluate_d5_structure(
    *,
    identity: D5Identity,
    observations: Sequence[D5Observation],
    structures: Sequence[D5Structure],
    evaluation_time: Optional[datetime] = None,
    required_inputs: Optional[Sequence[str]] = None,
    max_age_seconds: Optional[float] = None,
) -> D5Result:

    engine = D5StructureEngine(
        max_age_seconds=max_age_seconds
    )

    return engine.evaluate(
        identity=identity,
        observations=observations,
        structures=structures,
        evaluation_time=evaluation_time,
        required_inputs=required_inputs,
    )


# ---------------------------------------------------------------------
# SELF TEST
# ---------------------------------------------------------------------

def _self_test() -> None:

    evaluation_time = datetime(
        2026,
        9,
        4,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )

    identity = D5Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="SPOT",
        contract="INDEX",
        venue="NSE",
        market_profile_version="V6",
        instrument_profile_version="V6",
        contract_version="V6",
    )

    # -------------------------------------------------------------
    # Test 1 — identity
    # -------------------------------------------------------------

    assert identity.validate() == []

    # -------------------------------------------------------------
    # Test 2 — deterministic bullish structure
    # -------------------------------------------------------------

    structure_type, direction = (
        D5StructureEngine.classify_swing_sequence(
            previous_high=25000.0,
            current_high=25100.0,
            previous_low=24800.0,
            current_low=24900.0,
        )
    )

    assert structure_type == StructureType.HIGHER_HIGH
    assert direction == StructureDirection.BULLISH

    # -------------------------------------------------------------
    # Test 3 — bearish structure
    # -------------------------------------------------------------

    structure_type, direction = (
        D5StructureEngine.classify_swing_sequence(
            previous_high=25000.0,
            current_high=24900.0,
            previous_low=24800.0,
            current_low=24700.0,
        )
    )

    assert structure_type == StructureType.LOWER_LOW
    assert direction == StructureDirection.BEARISH

    # -------------------------------------------------------------
    # Test 4 — valid D5 evaluation
    # -------------------------------------------------------------

    observation = D5Observation(
        name="price",
        value=25050.0,
        observed_at=datetime(
            2026,
            9,
            4,
            9,
            59,
            30,
            tzinfo=timezone.utc,
        ),
        market_id="INDEX|NIFTY|NSE",
        instrument_id=(
            "INDEX|NIFTY|SPOT|INDEX|NSE"
        ),
        source_id="TEST_SOURCE",
    )

    structure = (
        D5StructureEngine.build_structure(
            structure_type=StructureType.HIGHER_HIGH,
            direction=StructureDirection.BULLISH,
            name="swing_structure",
            value={
                "previous_high": 25000.0,
                "current_high": 25100.0,
                "previous_low": 24800.0,
                "current_low": 24900.0,
            },
            observed_at=observation.observed_at,
            market_id="INDEX|NIFTY|NSE",
            instrument_id=(
                "INDEX|NIFTY|SPOT|INDEX|NSE"
            ),
            evidence_kind=EvidenceKind.DERIVED,
            source_ids=("TEST_SOURCE",),
        )
    )

    result = evaluate_d5_structure(
        identity=identity,
        observations=[observation],
        structures=[structure],
        evaluation_time=evaluation_time,
        required_inputs=["price"],
        max_age_seconds=300,
    )

    assert result.status == D5Status.READY
    assert len(result.structures) == 1

    # -------------------------------------------------------------
    # Test 5 — future-data leakage
    # -------------------------------------------------------------

    future_observation = D5Observation(
        name="future_price",
        value=26000.0,
        observed_at=datetime(
            2026,
            9,
            4,
            10,
            1,
            0,
            tzinfo=timezone.utc,
        ),
        market_id="INDEX|NIFTY|NSE",
        instrument_id=(
            "INDEX|NIFTY|SPOT|INDEX|NSE"
        ),
        source_id="TEST_SOURCE",
    )

    future_result = evaluate_d5_structure(
        identity=identity,
        observations=[future_observation],
        structures=[],
        evaluation_time=evaluation_time,
    )

    assert future_result.status == D5Status.BLOCKED

    # -------------------------------------------------------------
    # Test 6 — identity mismatch
    # -------------------------------------------------------------

    wrong_identity_structure = (
        D5StructureEngine.build_structure(
            structure_type=StructureType.BREAKOUT,
            direction=StructureDirection.BULLISH,
            name="wrong_market_structure",
            value=True,
            observed_at=evaluation_time,
            market_id="CRYPTO|BTC|BINANCE",
            instrument_id="CRYPTO|BTC|SPOT|BTCUSDT|BINANCE",
        )
    )

    mismatch_result = evaluate_d5_structure(
        identity=identity,
        observations=[],
        structures=[wrong_identity_structure],
        evaluation_time=evaluation_time,
    )

    assert mismatch_result.status == D5Status.LIMITED
    assert any(
        "IDENTITY_MISMATCH" in item
        for item in mismatch_result.conflicts
    )

    # -------------------------------------------------------------
    # Test 7 — incomplete identity
    # -------------------------------------------------------------

    incomplete_identity = D5Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="SPOT",
        contract="INDEX",
        venue="",
    )

    blocked_result = evaluate_d5_structure(
        identity=incomplete_identity,
        observations=[],
        structures=[],
        evaluation_time=evaluation_time,
    )

    assert blocked_result.status == D5Status.BLOCKED

    print("D5 SELF-TEST: PASS")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    _self_test()