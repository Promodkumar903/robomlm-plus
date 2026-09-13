"""
ROBOMLM_PLUS
Decision Layer — D6 Flow

D6 = FLOW

Purpose
-------
Represent and validate market-flow evidence entering the Decision layer.

Flow is not the same thing as volume.

Examples of flow evidence:
    - buy/sell transaction flow
    - aggressive buyer/seller activity
    - signed volume
    - delta
    - order-flow imbalance
    - bid/ask pressure
    - derivative flow
    - cross-instrument flow
    - observed or derived directional flow

Engineering rules
-----------------
1. Canonical identity is mandatory.
2. Flow is distinct from raw volume/activity.
3. Observed and derived evidence remain explicit.
4. No silent zero/default for missing flow.
5. Future data is rejected.
6. Stale data can degrade the result.
7. Conflicting flow evidence is preserved.
8. No arbitrary proprietary 0-100 score.
9. D6 does not make a BUY/SELL decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# =====================================================================
# ENUMS
# =====================================================================

class D6Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class FlowType(str, Enum):
    TRANSACTION_FLOW = "TRANSACTION_FLOW"
    AGGRESSOR_FLOW = "AGGRESSOR_FLOW"
    SIGNED_VOLUME = "SIGNED_VOLUME"
    DELTA = "DELTA"
    ORDER_FLOW_IMBALANCE = "ORDER_FLOW_IMBALANCE"
    BID_ASK_PRESSURE = "BID_ASK_PRESSURE"
    DERIVATIVE_FLOW = "DERIVATIVE_FLOW"
    CROSS_INSTRUMENT_FLOW = "CROSS_INSTRUMENT_FLOW"
    CROSS_MARKET_FLOW = "CROSS_MARKET_FLOW"
    UNKNOWN = "UNKNOWN"


class FlowDirection(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"


class EvidenceKind(str, Enum):
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"


class ConflictStatus(str, Enum):
    NONE = "NONE"
    PRESENT = "PRESENT"


# =====================================================================
# HELPERS
# =====================================================================

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _age_seconds(
    observed_at: datetime,
    evaluation_time: datetime,
) -> float:
    return max(
        0.0,
        (
            _ensure_utc(evaluation_time)
            - _ensure_utc(observed_at)
        ).total_seconds(),
    )


# =====================================================================
# IDENTITY
# =====================================================================

@dataclass(frozen=True)
class D6Identity:
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


# =====================================================================
# FLOW OBSERVATION
# =====================================================================

@dataclass(frozen=True)
class D6Observation:
    """
    Atomic flow observation.

    Examples:
        signed_volume = +1250
        delta = -840
        imbalance = +0.42

    `value` is intentionally not forced into a single numeric schema
    because BlackBox/live adapters may provide different flow primitives.

    Raw volume/activity must NOT be silently interpreted as directional
    flow. The flow_type identifies what the observation actually means.
    """

    name: str
    flow_type: FlowType
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str
    source_id: str

    direction: FlowDirection = FlowDirection.UNKNOWN

    evidence_kind: EvidenceKind = EvidenceKind.OBSERVED

    valid: bool = True

    unit: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def age_seconds(
        self,
        evaluation_time: datetime,
    ) -> float:
        return _age_seconds(
            self.observed_at,
            evaluation_time,
        )


# =====================================================================
# FLOW EVIDENCE
# =====================================================================

@dataclass(frozen=True)
class D6Flow:
    """
    Structured D6 flow evidence.
    """

    flow_type: FlowType
    direction: FlowDirection

    name: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str

    evidence_kind: EvidenceKind = EvidenceKind.DERIVED

    source_ids: Tuple[str, ...] = ()

    # Optional normalized directional quantity.
    #
    # This is NOT a proprietary score.
    #
    # If supplied, it should represent the actual measurement supplied
    # by the relevant flow model/adapter.
    normalized_value: Optional[float] = None

    conflict_status: ConflictStatus = ConflictStatus.NONE

    metadata: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# RESULT
# =====================================================================

@dataclass
class D6Result:

    status: D6Status

    flows: List[D6Flow] = field(default_factory=list)

    missing_inputs: List[str] = field(default_factory=list)
    stale_inputs: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    identity_errors: List[str] = field(default_factory=list)

    market_id: Optional[str] = None
    instrument_id: Optional[str] = None

    contract_version: Optional[str] = None

    evaluation_time: datetime = field(
        default_factory=_utc_now
    )

    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:

        return {
            "status": self.status.value,

            "flows": [
                {
                    "flow_type": flow.flow_type.value,
                    "direction": flow.direction.value,
                    "name": flow.name,
                    "value": flow.value,
                    "normalized_value": flow.normalized_value,
                    "observed_at": (
                        flow.observed_at.isoformat()
                    ),
                    "market_id": flow.market_id,
                    "instrument_id": flow.instrument_id,
                    "evidence_kind": (
                        flow.evidence_kind.value
                    ),
                    "source_ids": list(
                        flow.source_ids
                    ),
                    "conflict_status": (
                        flow.conflict_status.value
                    ),
                    "metadata": dict(flow.metadata),
                }
                for flow in self.flows
            ],

            "missing_inputs": list(
                self.missing_inputs
            ),

            "stale_inputs": list(
                self.stale_inputs
            ),

            "conflicts": list(
                self.conflicts
            ),

            "identity_errors": list(
                self.identity_errors
            ),

            "market_id": self.market_id,
            "instrument_id": self.instrument_id,
            "contract_version": self.contract_version,

            "evaluation_time": (
                self.evaluation_time.isoformat()
            ),

            "warnings": list(
                self.warnings
            ),
        }


# =====================================================================
# D6 ENGINE
# =====================================================================

class D6FlowEngine:
    """
    D6 Flow validation and representation engine.

    D6 does not convert flow into a BUY/SELL decision.
    """

    def __init__(
        self,
        *,
        max_age_seconds: Optional[float] = None,
    ) -> None:

        if (
            max_age_seconds is not None
            and max_age_seconds < 0
        ):
            raise ValueError(
                "max_age_seconds must be >= 0"
            )

        self.max_age_seconds = max_age_seconds

    # -----------------------------------------------------------------
    # MAIN EVALUATION
    # -----------------------------------------------------------------

    def evaluate(
        self,
        *,
        identity: D6Identity,
        observations: Sequence[D6Observation],
        flows: Sequence[D6Flow],
        evaluation_time: Optional[datetime] = None,
        required_flow_types: Optional[
            Sequence[FlowType]
        ] = None,
    ) -> D6Result:

        evaluation_time = _ensure_utc(
            evaluation_time or _utc_now()
        )

        identity_errors = identity.validate()

        result = D6Result(
            status=D6Status.READY,

            market_id=self._canonical_market_id(
                identity
            ),

            instrument_id=self._canonical_instrument_id(
                identity
            ),

            contract_version=identity.contract_version,

            evaluation_time=evaluation_time,

            identity_errors=identity_errors,
        )

        # -------------------------------------------------------------
        # IDENTITY GUARD
        # -------------------------------------------------------------

        if identity_errors:

            result.status = D6Status.BLOCKED

            result.warnings.append(
                "D6_BLOCKED_IDENTITY_NOT_RESOLVED"
            )

            return result

        # -------------------------------------------------------------
        # REQUIRED FLOW TYPES
        # -------------------------------------------------------------

        available_flow_types = {
            observation.flow_type
            for observation in observations
            if observation.valid
        }

        if required_flow_types:

            for required_type in required_flow_types:

                if required_type not in available_flow_types:

                    result.missing_inputs.append(
                        f"FLOW_TYPE:"
                        f"{required_type.value}"
                    )

        # -------------------------------------------------------------
        # OBSERVATION VALIDATION
        # -------------------------------------------------------------

        valid_observations: List[
            D6Observation
        ] = []

        for observation in observations:

            observed_at = _ensure_utc(
                observation.observed_at
            )

            # Future-data protection
            if observed_at > evaluation_time:

                result.status = D6Status.BLOCKED

                result.warnings.append(
                    "FUTURE_DATA_REJECTED:"
                    + observation.name
                )

                continue

            if not observation.valid:

                result.missing_inputs.append(
                    f"INVALID:"
                    f"{observation.name}"
                )

                continue

            age = observation.age_seconds(
                evaluation_time
            )

            if (
                self.max_age_seconds is not None
                and age > self.max_age_seconds
            ):

                result.stale_inputs.append(
                    observation.name
                )

            valid_observations.append(
                observation
            )

        # -------------------------------------------------------------
        # FLOW VALIDATION
        # -------------------------------------------------------------

        valid_flows: List[D6Flow] = []

        for flow in flows:

            observed_at = _ensure_utc(
                flow.observed_at
            )

            # Future flow protection
            if observed_at > evaluation_time:

                result.status = D6Status.BLOCKED

                result.warnings.append(
                    "FUTURE_FLOW_REJECTED:"
                    + flow.name
                )

                continue

            # Identity contamination protection
            if (
                flow.market_id
                != result.market_id
                or flow.instrument_id
                != result.instrument_id
            ):

                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + flow.name
                )

                continue

            valid_flows.append(flow)

        result.flows.extend(
            valid_flows
        )

        # -------------------------------------------------------------
        # FLOW CONFLICT DETECTION
        # -------------------------------------------------------------

        detected_conflicts = (
            self._detect_flow_conflicts(
                valid_flows
            )
        )

        result.conflicts.extend(
            detected_conflicts
        )

        if detected_conflicts:

            result.status = D6Status.LIMITED

            result.warnings.append(
                "FLOW_DIRECTION_CONFLICT_PRESENT"
            )

        # -------------------------------------------------------------
        # MISSING INPUTS
        # -------------------------------------------------------------

        if result.missing_inputs:

            if result.status != D6Status.BLOCKED:
                result.status = D6Status.LIMITED

        # -------------------------------------------------------------
        # STALE INPUTS
        # -------------------------------------------------------------

        if result.stale_inputs:

            if result.status != D6Status.BLOCKED:
                result.status = D6Status.LIMITED

        # -------------------------------------------------------------
        # NO VALID FLOW
        # -------------------------------------------------------------

        if not valid_flows:

            if result.status != D6Status.BLOCKED:
                result.status = D6Status.LIMITED

            result.warnings.append(
                "NO_VALID_FLOW_EVIDENCE"
            )

        return result

    # -----------------------------------------------------------------
    # FLOW BUILDER
    # -----------------------------------------------------------------

    @staticmethod
    def build_flow(
        *,
        flow_type: FlowType,
        direction: FlowDirection,
        name: str,
        value: Any,
        observed_at: datetime,
        market_id: str,
        instrument_id: str,
        evidence_kind: EvidenceKind = (
            EvidenceKind.DERIVED
        ),
        source_ids: Sequence[str] = (),
        normalized_value: Optional[
            float
        ] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> D6Flow:

        return D6Flow(
            flow_type=flow_type,
            direction=direction,
            name=name,
            value=value,
            observed_at=_ensure_utc(
                observed_at
            ),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=evidence_kind,
            source_ids=tuple(source_ids),
            normalized_value=normalized_value,
            metadata=dict(metadata or {}),
        )

    # -----------------------------------------------------------------
    # SIGNED FLOW PRIMITIVE
    # -----------------------------------------------------------------

    @staticmethod
    def classify_signed_flow(
        value: float,
        *,
        epsilon: float = 0.0,
    ) -> FlowDirection:

        """
        Deterministic primitive.

            value > +epsilon -> BUY
            value < -epsilon -> SELL
            otherwise         -> NEUTRAL

        This is a measurement classification, not a trading score.
        """

        if value > epsilon:
            return FlowDirection.BUY

        if value < -epsilon:
            return FlowDirection.SELL

        return FlowDirection.NEUTRAL

    # -----------------------------------------------------------------
    # FLOW IMBALANCE
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_imbalance(
        buy_quantity: float,
        sell_quantity: float,
    ) -> float:

        """
        Standard directional imbalance:

            I = (B - S) / (B + S)

        Domain:
            -1 <= I <= +1

        No denominator means no information:
            B + S = 0 -> ValueError

        Zero is NOT silently substituted.
        """

        if buy_quantity < 0:
            raise ValueError(
                "buy_quantity must be >= 0"
            )

        if sell_quantity < 0:
            raise ValueError(
                "sell_quantity must be >= 0"
            )

        denominator = (
            buy_quantity
            + sell_quantity
        )

        if denominator == 0:
            raise ValueError(
                "Cannot calculate flow imbalance "
                "when buy + sell quantity = 0"
            )

        return (
            buy_quantity
            - sell_quantity
        ) / denominator

    # -----------------------------------------------------------------
    # CONFLICT DETECTION
    # -----------------------------------------------------------------

    @staticmethod
    def _detect_flow_conflicts(
        flows: Sequence[D6Flow],
    ) -> List[str]:

        conflicts: List[str] = []

        grouped: Dict[
            Tuple[str, FlowType],
            List[D6Flow],
        ] = {}

        for flow in flows:

            key = (
                flow.name,
                flow.flow_type,
            )

            grouped.setdefault(
                key,
                [],
            ).append(flow)

        for (name, flow_type), items in grouped.items():

            directions = {
                item.direction
                for item in items
                if item.direction
                in {
                    FlowDirection.BUY,
                    FlowDirection.SELL,
                }
            }

            if (
                FlowDirection.BUY in directions
                and FlowDirection.SELL in directions
            ):

                conflicts.append(
                    "FLOW_CONFLICT:"
                    f"{name}:"
                    f"{flow_type.value}"
                )

        return conflicts

    # -----------------------------------------------------------------
    # ID HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _canonical_market_id(
        identity: D6Identity,
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
        identity: D6Identity,
    ) -> str:

        parts = [
            identity.category,
            identity.underlying,
            identity.instrument,
            identity.contract,
            identity.venue,
        ]

        if identity.base_currency:
            parts.append(
                identity.base_currency
            )

        if identity.quote_currency:
            parts.append(
                identity.quote_currency
            )

        return "|".join(parts)


# =====================================================================
# CONVENIENCE FUNCTION
# =====================================================================

def evaluate_d6_flow(
    *,
    identity: D6Identity,
    observations: Sequence[D6Observation],
    flows: Sequence[D6Flow],
    evaluation_time: Optional[datetime] = None,
    required_flow_types: Optional[
        Sequence[FlowType]
    ] = None,
    max_age_seconds: Optional[float] = None,
) -> D6Result:

    engine = D6FlowEngine(
        max_age_seconds=max_age_seconds
    )

    return engine.evaluate(
        identity=identity,
        observations=observations,
        flows=flows,
        evaluation_time=evaluation_time,
        required_flow_types=required_flow_types,
    )


# =====================================================================
# SELF TEST
# =====================================================================

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

    identity = D6Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="SPOT",
        contract="INDEX",
        venue="NSE",
        market_profile_version="V6",
        instrument_profile_version="V6",
        contract_version="V6",
    )

    market_id = "INDEX|NIFTY|NSE"

    instrument_id = (
        "INDEX|NIFTY|SPOT|INDEX|NSE"
    )

    # -------------------------------------------------------------
    # Test 1 — identity
    # -------------------------------------------------------------

    assert identity.validate() == []

    # -------------------------------------------------------------
    # Test 2 — signed flow classification
    # -------------------------------------------------------------

    assert (
        D6FlowEngine.classify_signed_flow(
            100.0
        )
        == FlowDirection.BUY
    )

    assert (
        D6FlowEngine.classify_signed_flow(
            -100.0
        )
        == FlowDirection.SELL
    )

    assert (
        D6FlowEngine.classify_signed_flow(
            0.0
        )
        == FlowDirection.NEUTRAL
    )

    # -------------------------------------------------------------
    # Test 3 — imbalance
    # -------------------------------------------------------------

    imbalance = (
        D6FlowEngine.calculate_imbalance(
            75.0,
            25.0,
        )
    )

    assert abs(
        imbalance - 0.5
    ) < 1e-12

    # -------------------------------------------------------------
    # Test 4 — valid flow
    # -------------------------------------------------------------

    observation = D6Observation(
        name="signed_delta",
        flow_type=FlowType.DELTA,
        value=500.0,
        observed_at=datetime(
            2026,
            9,
            4,
            9,
            59,
            30,
            tzinfo=timezone.utc,
        ),
        market_id=market_id,
        instrument_id=instrument_id,
        source_id="TEST_SOURCE",
        direction=FlowDirection.BUY,
    )

    flow = D6FlowEngine.build_flow(
        flow_type=FlowType.DELTA,
        direction=FlowDirection.BUY,
        name="signed_delta",
        value=500.0,
        observed_at=observation.observed_at,
        market_id=market_id,
        instrument_id=instrument_id,
        evidence_kind=EvidenceKind.OBSERVED,
        source_ids=("TEST_SOURCE",),
        normalized_value=0.5,
    )

    result = evaluate_d6_flow(
        identity=identity,
        observations=[observation],
        flows=[flow],
        evaluation_time=evaluation_time,
        required_flow_types=[
            FlowType.DELTA
        ],
        max_age_seconds=300,
    )

    assert result.status == D6Status.READY
    assert len(result.flows) == 1

    # -------------------------------------------------------------
    # Test 5 — future data leakage
    # -------------------------------------------------------------

    future_observation = D6Observation(
        name="future_delta",
        flow_type=FlowType.DELTA,
        value=999.0,
        observed_at=datetime(
            2026,
            9,
            4,
            10,
            1,
            0,
            tzinfo=timezone.utc,
        ),
        market_id=market_id,
        instrument_id=instrument_id,
        source_id="TEST_SOURCE",
        direction=FlowDirection.BUY,
    )

    future_result = evaluate_d6_flow(
        identity=identity,
        observations=[future_observation],
        flows=[],
        evaluation_time=evaluation_time,
    )

    assert future_result.status == D6Status.BLOCKED

    # -------------------------------------------------------------
    # Test 6 — identity mismatch
    # -------------------------------------------------------------

    wrong_flow = D6FlowEngine.build_flow(
        flow_type=FlowType.DELTA,
        direction=FlowDirection.BUY,
        name="wrong_market_flow",
        value=100.0,
        observed_at=evaluation_time,
        market_id="CRYPTO|BTC|BINANCE",
        instrument_id=(
            "CRYPTO|BTC|SPOT|BTCUSDT|BINANCE"
        ),
    )

    mismatch_result = evaluate_d6_flow(
        identity=identity,
        observations=[],
        flows=[wrong_flow],
        evaluation_time=evaluation_time,
    )

    assert mismatch_result.status == D6Status.LIMITED

    assert any(
        "IDENTITY_MISMATCH" in item
        for item in mismatch_result.conflicts
    )

    # -------------------------------------------------------------
    # Test 7 — conflicting flow
    # -------------------------------------------------------------

    buy_flow = D6FlowEngine.build_flow(
        flow_type=FlowType.DELTA,
        direction=FlowDirection.BUY,
        name="same_delta",
        value=100.0,
        observed_at=evaluation_time,
        market_id=market_id,
        instrument_id=instrument_id,
    )

    sell_flow = D6FlowEngine.build_flow(
        flow_type=FlowType.DELTA,
        direction=FlowDirection.SELL,
        name="same_delta",
        value=-100.0,
        observed_at=evaluation_time,
        market_id=market_id,
        instrument_id=instrument_id,
    )

    conflict_result = evaluate_d6_flow(
        identity=identity,
        observations=[],
        flows=[
            buy_flow,
            sell_flow,
        ],
        evaluation_time=evaluation_time,
    )

    assert conflict_result.status == D6Status.LIMITED

    assert any(
        "FLOW_CONFLICT" in item
        for item in conflict_result.conflicts
    )

    # -------------------------------------------------------------
    # Test 8 — incomplete identity
    # -------------------------------------------------------------

    incomplete_identity = D6Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="SPOT",
        contract="INDEX",
        venue="",
    )

    blocked_result = evaluate_d6_flow(
        identity=incomplete_identity,
        observations=[],
        flows=[],
        evaluation_time=evaluation_time,
    )

    assert (
        blocked_result.status
        == D6Status.BLOCKED
    )

    print("D6 SELF-TEST: PASS")


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _self_test()