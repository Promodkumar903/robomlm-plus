"""
ROBOMLM_PLUS
D14 — DECISION VALIDATION ENGINE

Decision Layer:
D1  Market Identity
D2  Data Contract
D3  Trust
D4  Relationships
D5  Structure
D6  Flow
D7  Liquidity / Volatility
D8  Instrument Mechanics
D9  Time / Event
D10 Market State
D11 Transition
D12 Future / Scenario
D13 Decision
D14 VALIDATION
D15 Learning
D16 Intelligence

D14 validates an already-made D13 decision against what actually
happened after the decision timestamp.

D14 MUST NOT:
- modify the original D13 decision
- use outcome data before its timestamp
- create a new decision
- learn/update model parameters
- become D15
- become D16

D14 MUST:
- preserve the original decision
- preserve decision-time information
- separate decision-time evidence from outcome evidence
- validate direction
- validate scenario
- validate horizon/timing
- validate invalidation where supplied
- validate execution/P&L independently where supplied
- detect future-data leakage
- detect identity mismatch
- produce an auditable validation record

No arbitrary universal 0-100 proprietary score is invented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# =====================================================================
# ENUMS
# =====================================================================

class ValidationStatus(str, Enum):
    VALIDATED = "VALIDATED"
    PARTIAL = "PARTIAL"
    INVALIDATED = "INVALIDATED"
    UNDETERMINED = "UNDETERMINED"
    BLOCKED = "BLOCKED"


class ValidationResult(str, Enum):
    CORRECT = "CORRECT"
    INCORRECT = "INCORRECT"
    PARTIAL = "PARTIAL"
    UNDETERMINED = "UNDETERMINED"


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class DecisionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WAIT = "WAIT"
    NO_ACTION = "NO_ACTION"
    BLOCKED = "BLOCKED"


class ValidationReason(str, Enum):
    ALIGNED = "ALIGNED"

    DIRECTION_MATCH = "DIRECTION_MATCH"
    DIRECTION_MISMATCH = "DIRECTION_MISMATCH"

    SCENARIO_MATCH = "SCENARIO_MATCH"
    SCENARIO_MISMATCH = "SCENARIO_MISMATCH"

    HORIZON_MATCH = "HORIZON_MATCH"
    HORIZON_MISSED = "HORIZON_MISSED"

    INVALIDATION_TRIGGERED = "INVALIDATION_TRIGGERED"
    INVALIDATION_NOT_TRIGGERED = "INVALIDATION_NOT_TRIGGERED"

    PNL_PROFIT = "PNL_PROFIT"
    PNL_LOSS = "PNL_LOSS"

    MISSING_OUTCOME = "MISSING_OUTCOME"

    FUTURE_LEAKAGE = "FUTURE_LEAKAGE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    TIMESTAMP_ERROR = "TIMESTAMP_ERROR"


# =====================================================================
# HELPERS
# =====================================================================

def parse_dt(value: Any) -> Optional[datetime]:
    """
    Normalize supported timestamp values to timezone-aware UTC datetime.
    """

    if value is None:
        return None

    if isinstance(value, datetime):
        dt = value

    elif isinstance(value, str):
        text = value.strip()

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            return None

    else:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =====================================================================
# D13 DECISION SNAPSHOT
# =====================================================================

@dataclass
class DecisionSnapshot:
    """
    Immutable-style snapshot of what D13 decided at T0.

    D14 validates this snapshot.
    D14 does not modify it.
    """

    decision_id: str
    market_id: str
    as_of: datetime

    action: DecisionAction

    selected_scenario_id: Optional[str] = None
    selected_scenario_type: Optional[str] = None

    expected_direction: Direction = Direction.UNKNOWN

    horizon: Optional[str] = None

    # Optional externally defined invalidation condition.
    invalidation_price: Optional[float] = None

    # Decision-time evidence only.
    evidence_ids: List[str] = field(default_factory=list)

    engine_version: str = "UNKNOWN"
    policy_version: str = "UNKNOWN"

    metadata: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# ACTUAL OUTCOME
# =====================================================================

@dataclass
class OutcomeObservation:
    """
    Actual post-decision observation.

    Every accepted observation must occur strictly after D13 T0.
    """

    observation_id: str
    market_id: str

    timestamp: datetime

    price: Optional[float] = None

    direction: Direction = Direction.UNKNOWN

    scenario_type: Optional[str] = None

    pnl: Optional[float] = None

    # Explicit externally determined invalidation status.
    invalidation_triggered: Optional[bool] = None

    source: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# VALIDATION COMPONENT
# =====================================================================

@dataclass
class ValidationComponent:
    name: str
    result: ValidationResult
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# VALIDATION RECORD
# =====================================================================

@dataclass
class ValidationRecord:
    """
    Auditable D14 output.

    This record becomes an input candidate for D15.
    It does not itself perform learning.
    """

    validation_id: str

    decision_id: str
    market_id: str

    decision_timestamp: datetime
    validation_timestamp: datetime

    status: ValidationStatus

    direction_validation: ValidationComponent
    scenario_validation: ValidationComponent
    horizon_validation: ValidationComponent
    invalidation_validation: ValidationComponent
    pnl_validation: ValidationComponent

    overall_result: ValidationResult

    leakage_detected: bool = False
    identity_mismatch: bool = False

    notes: List[str] = field(default_factory=list)

    provenance: Dict[str, Any] = field(default_factory=dict)


# =====================================================================
# D14 ENGINE
# =====================================================================

class D14DecisionValidationEngine:

    VERSION = "D14-1.0"

    # -----------------------------------------------------------------
    # PUBLIC VALIDATION
    # -----------------------------------------------------------------

    def validate(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation],
        validation_id: str = "D14-VALIDATION"
    ) -> ValidationRecord:

        decision_time = parse_dt(decision.as_of)

        # -------------------------------------------------------------
        # DECISION TIMESTAMP GATE
        # -------------------------------------------------------------

        if decision_time is None:
            return self._blocked(
                validation_id,
                decision,
                ValidationReason.TIMESTAMP_ERROR.value
            )

        # -------------------------------------------------------------
        # MARKET IDENTITY GATE
        # -------------------------------------------------------------

        if not decision.market_id:
            return self._blocked(
                validation_id,
                decision,
                ValidationReason.IDENTITY_MISMATCH.value
            )

        # -------------------------------------------------------------
        # FUTURE / IDENTITY GUARD
        # -------------------------------------------------------------

        leakage: List[str] = []
        identity_errors: List[str] = []

        clean_outcomes: List[OutcomeObservation] = []

        for outcome in outcomes:

            outcome_time = parse_dt(outcome.timestamp)

            # Invalid timestamp cannot be used.
            if outcome_time is None:
                leakage.append(
                    f"invalid_timestamp:{outcome.observation_id}"
                )
                continue

            # D14 accepts only observations strictly after T0.
            if outcome_time <= decision_time:
                leakage.append(
                    f"pre_decision_outcome:{outcome.observation_id}"
                )
                continue

            # Market identity must remain identical.
            if outcome.market_id != decision.market_id:
                identity_errors.append(
                    f"market_identity_mismatch:{outcome.observation_id}"
                )
                continue

            clean_outcomes.append(outcome)

        # -------------------------------------------------------------
        # HARD LEAKAGE BLOCK
        # -------------------------------------------------------------

        if leakage:
            return self._blocked(
                validation_id,
                decision,
                ValidationReason.FUTURE_LEAKAGE.value,
                leakage=leakage
            )

        # -------------------------------------------------------------
        # HARD IDENTITY BLOCK
        # -------------------------------------------------------------

        if identity_errors:
            return self._blocked(
                validation_id,
                decision,
                ValidationReason.IDENTITY_MISMATCH.value,
                leakage=identity_errors
            )

        # -------------------------------------------------------------
        # NO VALID OUTCOME
        # -------------------------------------------------------------

        if not clean_outcomes:
            return self._undetermined(
                validation_id,
                decision
            )

        # -------------------------------------------------------------
        # CHRONOLOGICAL ORDER
        # -------------------------------------------------------------

        clean_outcomes.sort(
            key=lambda x: parse_dt(x.timestamp) or utc_now()
        )

        first = clean_outcomes[0]
        latest = clean_outcomes[-1]

        # -------------------------------------------------------------
        # COMPONENT VALIDATION
        # -------------------------------------------------------------

        direction_component = self._validate_direction(
            decision,
            clean_outcomes
        )

        scenario_component = self._validate_scenario(
            decision,
            clean_outcomes
        )

        horizon_component = self._validate_horizon(
            decision,
            clean_outcomes
        )

        invalidation_component = self._validate_invalidation(
            decision,
            clean_outcomes
        )

        pnl_component = self._validate_pnl(
            decision,
            clean_outcomes
        )

        components = [
            direction_component,
            scenario_component,
            horizon_component,
            invalidation_component,
            pnl_component,
        ]

        # -------------------------------------------------------------
        # AGGREGATION
        # -------------------------------------------------------------

        overall = self._aggregate(components)

        if overall == ValidationResult.CORRECT:
            status = ValidationStatus.VALIDATED

        elif overall == ValidationResult.INCORRECT:
            status = ValidationStatus.INVALIDATED

        elif overall == ValidationResult.PARTIAL:
            status = ValidationStatus.PARTIAL

        else:
            status = ValidationStatus.UNDETERMINED

        # -------------------------------------------------------------
        # PROVENANCE
        # -------------------------------------------------------------

        first_time = parse_dt(first.timestamp)
        latest_time = parse_dt(latest.timestamp)

        return ValidationRecord(
            validation_id=validation_id,

            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=decision_time,
            validation_timestamp=latest_time or utc_now(),

            status=status,

            direction_validation=direction_component,
            scenario_validation=scenario_component,
            horizon_validation=horizon_component,
            invalidation_validation=invalidation_component,
            pnl_validation=pnl_component,

            overall_result=overall,

            leakage_detected=False,
            identity_mismatch=False,

            notes=[],

            provenance={
                "engine": "D14_DECISION_VALIDATION",
                "engine_version": self.VERSION,

                "decision_engine_version":
                    decision.engine_version,

                "decision_policy_version":
                    decision.policy_version,

                "decision_time":
                    decision_time.isoformat(),

                "first_outcome_time":
                    first_time.isoformat()
                    if first_time else None,

                "latest_outcome_time":
                    latest_time.isoformat()
                    if latest_time else None,

                "outcome_count":
                    len(clean_outcomes),

                # Outcome information exists here because this is D14.
                "future_outcome_observed":
                    True,

                "validated_by_D14":
                    True,

                # D14 never performs learning.
                "learning_applied":
                    False,

                # Clean validated record may be consumed by D15.
                "D15_ready":
                    True,

                # D16 is not executed here.
                "D16_applied":
                    False,
            }
        )

    # -----------------------------------------------------------------
    # DIRECTION
    # -----------------------------------------------------------------

    def _validate_direction(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation]
    ) -> ValidationComponent:

        expected = decision.expected_direction

        if expected == Direction.UNKNOWN:
            return ValidationComponent(
                name="direction",
                result=ValidationResult.UNDETERMINED,
                reason="Expected direction unavailable"
            )

        observed = [
            x.direction
            for x in outcomes
            if x.direction != Direction.UNKNOWN
        ]

        if not observed:
            return ValidationComponent(
                name="direction",
                result=ValidationResult.UNDETERMINED,
                reason="Observed direction unavailable"
            )

        # Latest observed direction is used for final direction validation.
        actual = observed[-1]

        if actual == expected:
            return ValidationComponent(
                name="direction",
                result=ValidationResult.CORRECT,
                reason=ValidationReason.DIRECTION_MATCH.value,
                evidence={
                    "expected": expected.value,
                    "actual": actual.value,
                }
            )

        return ValidationComponent(
            name="direction",
            result=ValidationResult.INCORRECT,
            reason=ValidationReason.DIRECTION_MISMATCH.value,
            evidence={
                "expected": expected.value,
                "actual": actual.value,
            }
        )

    # -----------------------------------------------------------------
    # SCENARIO
    # -----------------------------------------------------------------

    def _validate_scenario(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation]
    ) -> ValidationComponent:

        if not decision.selected_scenario_type:
            return ValidationComponent(
                name="scenario",
                result=ValidationResult.UNDETERMINED,
                reason="Selected D12 scenario unavailable"
            )

        actual = [
            x.scenario_type
            for x in outcomes
            if x.scenario_type
        ]

        if not actual:
            return ValidationComponent(
                name="scenario",
                result=ValidationResult.UNDETERMINED,
                reason="Actual scenario classification unavailable"
            )

        if decision.selected_scenario_type in actual:
            return ValidationComponent(
                name="scenario",
                result=ValidationResult.CORRECT,
                reason=ValidationReason.SCENARIO_MATCH.value,
                evidence={
                    "expected": decision.selected_scenario_type,
                    "observed": actual,
                }
            )

        return ValidationComponent(
            name="scenario",
            result=ValidationResult.INCORRECT,
            reason=ValidationReason.SCENARIO_MISMATCH.value,
            evidence={
                "expected": decision.selected_scenario_type,
                "observed": actual,
            }
        )

    # -----------------------------------------------------------------
    # HORIZON
    # -----------------------------------------------------------------

    def _validate_horizon(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation]
    ) -> ValidationComponent:

        if not decision.horizon:
            return ValidationComponent(
                name="horizon",
                result=ValidationResult.UNDETERMINED,
                reason="Decision horizon unavailable"
            )

        observed_horizon = None

        for outcome in outcomes:
            value = outcome.metadata.get("horizon")

            if value is not None:
                observed_horizon = value

        if observed_horizon is None:
            return ValidationComponent(
                name="horizon",
                result=ValidationResult.UNDETERMINED,
                reason="Observed horizon unavailable"
            )

        if str(observed_horizon) == str(decision.horizon):
            return ValidationComponent(
                name="horizon",
                result=ValidationResult.CORRECT,
                reason=ValidationReason.HORIZON_MATCH.value,
                evidence={
                    "expected": decision.horizon,
                    "observed": observed_horizon,
                }
            )

        return ValidationComponent(
            name="horizon",
            result=ValidationResult.PARTIAL,
            reason=ValidationReason.HORIZON_MISSED.value,
            evidence={
                "expected": decision.horizon,
                "observed": observed_horizon,
            }
        )

    # -----------------------------------------------------------------
    # INVALIDATION
    # -----------------------------------------------------------------

    def _validate_invalidation(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation]
    ) -> ValidationComponent:

        # -------------------------------------------------------------
        # EXPLICIT INVALIDATION
        # -------------------------------------------------------------

        explicit = [
            x.invalidation_triggered
            for x in outcomes
            if x.invalidation_triggered is not None
        ]

        if explicit:

            triggered = any(explicit)

            if triggered:
                return ValidationComponent(
                    name="invalidation",
                    result=ValidationResult.INCORRECT,
                    reason=ValidationReason.INVALIDATION_TRIGGERED.value,
                    evidence={
                        "triggered": True
                    }
                )

            return ValidationComponent(
                name="invalidation",
                result=ValidationResult.CORRECT,
                reason=ValidationReason.INVALIDATION_NOT_TRIGGERED.value,
                evidence={
                    "triggered": False
                }
            )

        # -------------------------------------------------------------
        # NO UNIVERSAL INVALIDATION RULE
        # -------------------------------------------------------------

        if decision.invalidation_price is None:
            return ValidationComponent(
                name="invalidation",
                result=ValidationResult.UNDETERMINED,
                reason="No externally supplied invalidation condition"
            )

        prices = [
            x.price
            for x in outcomes
            if x.price is not None
        ]

        if not prices:
            return ValidationComponent(
                name="invalidation",
                result=ValidationResult.UNDETERMINED,
                reason="Outcome prices unavailable"
            )

        level = decision.invalidation_price

        # -------------------------------------------------------------
        # LONG / UP INVALIDATION
        # -------------------------------------------------------------

        if decision.expected_direction == Direction.UP:
            triggered = min(prices) <= level

        # -------------------------------------------------------------
        # SHORT / DOWN INVALIDATION
        # -------------------------------------------------------------

        elif decision.expected_direction == Direction.DOWN:
            triggered = max(prices) >= level

        else:
            # No universal invalidation interpretation for NEUTRAL/UNKNOWN.
            return ValidationComponent(
                name="invalidation",
                result=ValidationResult.UNDETERMINED,
                reason="Invalidation direction unavailable",
                evidence={
                    "level": level
                }
            )

        if triggered:
            return ValidationComponent(
                name="invalidation",
                result=ValidationResult.INCORRECT,
                reason=ValidationReason.INVALIDATION_TRIGGERED.value,
                evidence={
                    "level": level,
                    "observed_prices": prices,
                }
            )

        return ValidationComponent(
            name="invalidation",
            result=ValidationResult.CORRECT,
            reason=ValidationReason.INVALIDATION_NOT_TRIGGERED.value,
            evidence={
                "level": level,
                "observed_prices": prices,
            }
        )

    # -----------------------------------------------------------------
    # PNL
    # -----------------------------------------------------------------

    def _validate_pnl(
        self,
        decision: DecisionSnapshot,
        outcomes: List[OutcomeObservation]
    ) -> ValidationComponent:

        pnl_values = [
            x.pnl
            for x in outcomes
            if x.pnl is not None
        ]

        if not pnl_values:
            return ValidationComponent(
                name="pnl",
                result=ValidationResult.UNDETERMINED,
                reason=ValidationReason.MISSING_OUTCOME.value
            )

        pnl = pnl_values[-1]

        if pnl > 0:
            return ValidationComponent(
                name="pnl",
                result=ValidationResult.CORRECT,
                reason=ValidationReason.PNL_PROFIT.value,
                evidence={
                    "pnl": pnl
                }
            )

        if pnl < 0:
            return ValidationComponent(
                name="pnl",
                result=ValidationResult.INCORRECT,
                reason=ValidationReason.PNL_LOSS.value,
                evidence={
                    "pnl": pnl
                }
            )

        return ValidationComponent(
            name="pnl",
            result=ValidationResult.PARTIAL,
            reason="P&L equals zero",
            evidence={
                "pnl": pnl
            }
        )

    # -----------------------------------------------------------------
    # AGGREGATION
    # -----------------------------------------------------------------

    def _aggregate(
        self,
        components: List[ValidationComponent]
    ) -> ValidationResult:

        # -------------------------------------------------------------
        # HARD NEGATIVES
        # -------------------------------------------------------------
        #
        # Direction mismatch and explicit invalidation are genuine
        # validation failures.
        #

        for component in components:

            if component.result == ValidationResult.INCORRECT:

                if component.reason in {
                    ValidationReason.DIRECTION_MISMATCH.value,
                    ValidationReason.INVALIDATION_TRIGGERED.value,
                }:
                    return ValidationResult.INCORRECT

        # -------------------------------------------------------------
        # AVAILABLE EVIDENCE
        # -------------------------------------------------------------
        #
        # UNDETERMINED means that a dimension could not be evaluated.
        # It must NOT automatically invalidate the entire validation.
        #

        available = [
            component
            for component in components
            if component.result != ValidationResult.UNDETERMINED
        ]

        if not available:
            return ValidationResult.UNDETERMINED

        # -------------------------------------------------------------
        # RESULT COUNTS
        # -------------------------------------------------------------

        has_partial = any(
            component.result == ValidationResult.PARTIAL
            for component in available
        )

        has_incorrect = any(
            component.result == ValidationResult.INCORRECT
            for component in available
        )

        has_correct = any(
            component.result == ValidationResult.CORRECT
            for component in available
        )

        # -------------------------------------------------------------
        # MIXED RESULT
        # -------------------------------------------------------------

        if has_incorrect and has_correct:
            return ValidationResult.PARTIAL

        # -------------------------------------------------------------
        # ONLY INCORRECT
        # -------------------------------------------------------------

        if has_incorrect:
            return ValidationResult.INCORRECT

        # -------------------------------------------------------------
        # PARTIAL
        # -------------------------------------------------------------

        if has_partial:
            return ValidationResult.PARTIAL

        # -------------------------------------------------------------
        # ALL AVAILABLE CORRECT
        # -------------------------------------------------------------

        if all(
            component.result == ValidationResult.CORRECT
            for component in available
        ):
            return ValidationResult.CORRECT

        return ValidationResult.UNDETERMINED

    # -----------------------------------------------------------------
    # BLOCKED
    # -----------------------------------------------------------------

    def _blocked(
        self,
        validation_id: str,
        decision: DecisionSnapshot,
        reason: str,
        leakage: Optional[List[str]] = None
    ) -> ValidationRecord:

        component = ValidationComponent(
            name="validation_gate",
            result=ValidationResult.UNDETERMINED,
            reason=reason,
            evidence={
                "blocked": True,
                "items": leakage or [],
            }
        )

        return ValidationRecord(
            validation_id=validation_id,

            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=
                parse_dt(decision.as_of) or utc_now(),

            validation_timestamp=utc_now(),

            status=ValidationStatus.BLOCKED,

            direction_validation=component,
            scenario_validation=component,
            horizon_validation=component,
            invalidation_validation=component,
            pnl_validation=component,

            overall_result=ValidationResult.UNDETERMINED,

            leakage_detected=bool(leakage),

            identity_mismatch=(
                reason == ValidationReason.IDENTITY_MISMATCH.value
            ),

            notes=[reason],

            provenance={
                "engine": "D14_DECISION_VALIDATION",
                "engine_version": self.VERSION,

                "validated_by_D14": False,
                "D15_ready": False,

                "learning_applied": False,
                "D16_applied": False,
            }
        )

    # -----------------------------------------------------------------
    # UNDETERMINED
    # -----------------------------------------------------------------

    def _undetermined(
        self,
        validation_id: str,
        decision: DecisionSnapshot
    ) -> ValidationRecord:

        component = ValidationComponent(
            name="outcome",
            result=ValidationResult.UNDETERMINED,
            reason=ValidationReason.MISSING_OUTCOME.value
        )

        return ValidationRecord(
            validation_id=validation_id,

            decision_id=decision.decision_id,
            market_id=decision.market_id,

            decision_timestamp=
                parse_dt(decision.as_of) or utc_now(),

            validation_timestamp=utc_now(),

            status=ValidationStatus.UNDETERMINED,

            direction_validation=component,
            scenario_validation=component,
            horizon_validation=component,
            invalidation_validation=component,
            pnl_validation=component,

            overall_result=ValidationResult.UNDETERMINED,

            leakage_detected=False,
            identity_mismatch=False,

            provenance={
                "engine": "D14_DECISION_VALIDATION",
                "engine_version": self.VERSION,

                "validated_by_D14": False,
                "D15_ready": False,

                "learning_applied": False,
                "D16_applied": False,
            }
        )


# =====================================================================
# SELF TEST
# =====================================================================

def _self_test() -> None:

    engine = D14DecisionValidationEngine()

    t0 = datetime(
        2026,
        9,
        4,
        9,
        30,
        tzinfo=timezone.utc
    )

    # =================================================================
    # 1. CORRECT DECISION VALIDATION
    # =================================================================

    decision = DecisionSnapshot(
        decision_id="DEC-001",

        market_id="NSE:NIFTY:SPOT",

        as_of=t0,

        action=DecisionAction.BUY,

        selected_scenario_id="SCN-001",

        selected_scenario_type="CONTINUATION",

        expected_direction=Direction.UP,

        horizon="SHORT",

        evidence_ids=["E-001"],

        engine_version="D13-1.0",

        policy_version="POLICY-TEST",
    )

    outcomes = [
        OutcomeObservation(
            observation_id="O-001",

            market_id="NSE:NIFTY:SPOT",

            timestamp=t0.replace(minute=45),

            price=25000,

            direction=Direction.UP,

            scenario_type="CONTINUATION",

            pnl=100,

            metadata={
                "horizon": "SHORT"
            }
        )
    ]

    result = engine.validate(
        decision,
        outcomes,
        validation_id="VAL-001"
    )

    assert result.status == ValidationStatus.VALIDATED

    assert result.overall_result == ValidationResult.CORRECT

    assert (
        result.direction_validation.result
        == ValidationResult.CORRECT
    )

    assert (
        result.scenario_validation.result
        == ValidationResult.CORRECT
    )

    assert (
        result.horizon_validation.result
        == ValidationResult.CORRECT
    )

    assert (
        result.pnl_validation.result
        == ValidationResult.CORRECT
    )

    # Invalidation is intentionally unavailable in this case.
    assert (
        result.invalidation_validation.result
        == ValidationResult.UNDETERMINED
    )

    assert result.provenance["D15_ready"] is True

    # D14 must not mutate the D13 decision.
    assert decision.decision_id == "DEC-001"
    assert decision.market_id == "NSE:NIFTY:SPOT"

    # =================================================================
    # 2. DIRECTION MISMATCH
    # =================================================================

    wrong_direction = [
        OutcomeObservation(
            observation_id="O-002",

            market_id="NSE:NIFTY:SPOT",

            timestamp=t0.replace(minute=50),

            price=24800,

            direction=Direction.DOWN,

            scenario_type="REVERSAL",

            pnl=-100,

            metadata={
                "horizon": "SHORT"
            }
        )
    ]

    result_wrong = engine.validate(
        decision,
        wrong_direction,
        validation_id="VAL-002"
    )

    assert result_wrong.status == ValidationStatus.INVALIDATED

    assert (
        result_wrong.direction_validation.result
        == ValidationResult.INCORRECT
    )

    # =================================================================
    # 3. FUTURE / PRE-DECISION OUTCOME ATTACK
    # =================================================================

    leaked = [
        OutcomeObservation(
            observation_id="O-FUTURE-LEAK",

            market_id="NSE:NIFTY:SPOT",

            # Same timestamp as decision = invalid for D14.
            timestamp=t0,

            price=25100,

            direction=Direction.UP,

            scenario_type="CONTINUATION",

            pnl=500,
        )
    ]

    leak_result = engine.validate(
        decision,
        leaked,
        validation_id="VAL-003"
    )

    assert leak_result.status == ValidationStatus.BLOCKED

    assert leak_result.leakage_detected is True

    assert leak_result.provenance["D15_ready"] is False

    # =================================================================
    # 4. MARKET IDENTITY ISOLATION
    # =================================================================

    wrong_market = [
        OutcomeObservation(
            observation_id="O-WRONG-MARKET",

            market_id="BINANCE:BTC:SPOT",

            timestamp=t0.replace(minute=45),

            price=100000,

            direction=Direction.UP,

            scenario_type="CONTINUATION",

            pnl=100,
        )
    ]

    identity_result = engine.validate(
        decision,
        wrong_market,
        validation_id="VAL-004"
    )

    assert identity_result.status == ValidationStatus.BLOCKED

    assert identity_result.identity_mismatch is True

    assert identity_result.provenance["D15_ready"] is False

    # =================================================================
    # 5. MISSING OUTCOME
    # =================================================================

    missing_result = engine.validate(
        decision,
        [],
        validation_id="VAL-005"
    )

    assert missing_result.status == ValidationStatus.UNDETERMINED

    assert (
        missing_result.overall_result
        == ValidationResult.UNDETERMINED
    )

    assert missing_result.provenance["D15_ready"] is False

    # =================================================================
    # 6. INVALIDATION TRIGGER
    # =================================================================

    invalidation_decision = DecisionSnapshot(
        decision_id="DEC-002",

        market_id="NSE:NIFTY:SPOT",

        as_of=t0,

        action=DecisionAction.BUY,

        selected_scenario_id="SCN-002",

        selected_scenario_type="CONTINUATION",

        expected_direction=Direction.UP,

        horizon="SHORT",

        invalidation_price=24900,
    )

    invalidation_outcome = [
        OutcomeObservation(
            observation_id="O-INV",

            market_id="NSE:NIFTY:SPOT",

            timestamp=t0.replace(minute=55),

            price=24850,

            direction=Direction.DOWN,

            scenario_type="REVERSAL",

            pnl=-150,

            invalidation_triggered=True,

            metadata={
                "horizon": "SHORT"
            }
        )
    ]

    invalidation_result = engine.validate(
        invalidation_decision,
        invalidation_outcome,
        validation_id="VAL-006"
    )

    assert (
        invalidation_result.invalidation_validation.result
        == ValidationResult.INCORRECT
    )

    assert (
        invalidation_result.status
        == ValidationStatus.INVALIDATED
    )

    assert invalidation_result.provenance["D15_ready"] is True

    # =================================================================
    # 7. D14 MUST NOT LEARN
    # =================================================================

    assert result.provenance["learning_applied"] is False

    assert result.provenance["D16_applied"] is False

    # =================================================================
    # PASS
    # =================================================================

    print("D14 SELF-TEST: PASS")


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _self_test()