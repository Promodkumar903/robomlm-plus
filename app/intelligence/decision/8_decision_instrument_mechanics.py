"""
ROBOMLM_PLUS
Decision Layer — D8 Instrument Mechanics

D8 = INSTRUMENT MECHANICS

Purpose
-------
Represent and validate mechanics that belong to the tradable instrument
or its contract.

D8 covers:
    - instrument type
    - contract specification
    - tick size
    - lot / contract quantity
    - multiplier
    - price precision
    - settlement mechanics
    - option strike / option type
    - futures contract mechanics
    - expiry as an INSTRUMENT/CONTRACT PROPERTY

D9 separately handles:
    TIME / EVENT

Therefore:
    D8 -> what the instrument/contract IS and how it mechanically works
    D9 -> when events/time conditions occur

Engineering rules
-----------------
1. Canonical identity is mandatory.
2. Instrument mechanics must belong to the identified instrument.
3. Contract mechanics are not treated as market direction.
4. Expiry metadata is represented here only as a contract property.
5. Event timing belongs to D9.
6. Margin is financing/risk information, NOT instrument identity.
7. Missing mechanics are preserved.
8. No silent defaults.
9. Future-dated observations are rejected.
10. Identity mismatch is rejected/surfaced.
11. Observed and derived information remain distinct.
12. No arbitrary 0-100 score.
13. D8 does not make a BUY/SELL decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple


# =====================================================================
# ENUMS
# =====================================================================

class D8Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class InstrumentType(str, Enum):
    SPOT = "SPOT"
    INDEX = "INDEX"
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    PERPETUAL = "PERPETUAL"
    CFD = "CFD"
    FORWARD = "FORWARD"
    ETF = "ETF"
    FUND = "FUND"
    UNKNOWN = "UNKNOWN"


class OptionType(str, Enum):
    CALL = "CALL"
    PUT = "PUT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class SettlementType(str, Enum):
    CASH = "CASH"
    PHYSICAL = "PHYSICAL"
    DELIVERY = "DELIVERY"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


class ExerciseType(str, Enum):
    EUROPEAN = "EUROPEAN"
    AMERICAN = "AMERICAN"
    BERMUDAN = "BERMUDAN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
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


# =====================================================================
# IDENTITY
# =====================================================================

@dataclass(frozen=True)
class D8Identity:
    """
    Canonical instrument identity.

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

            if (
                value is None
                or str(value).strip() == ""
            ):
                errors.append(
                    f"MISSING_IDENTITY:{name}"
                )

        category = str(
            self.category
        ).upper()

        instrument = str(
            self.instrument
        ).upper()

        pair_like = (
            "FX" in category
            or "FOREX" in category
            or "FX" in instrument
            or "FOREX" in instrument
            or "PAIR" in instrument
        )

        if pair_like:

            if not self.base_currency:
                errors.append(
                    "MISSING_IDENTITY:base_currency"
                )

            if not self.quote_currency:
                errors.append(
                    "MISSING_IDENTITY:quote_currency"
                )

        return errors


# =====================================================================
# CONTRACT MECHANICS
# =====================================================================

@dataclass(frozen=True)
class D8Mechanics:

    instrument_type: InstrumentType

    # -------------------------------------------------------------
    # Price mechanics
    # -------------------------------------------------------------

    tick_size: Optional[float] = None

    price_precision: Optional[int] = None

    # -------------------------------------------------------------
    # Quantity mechanics
    # -------------------------------------------------------------

    lot_size: Optional[float] = None

    contract_quantity: Optional[float] = None

    multiplier: Optional[float] = None

    # -------------------------------------------------------------
    # Derivative mechanics
    # -------------------------------------------------------------

    expiry: Optional[datetime] = None

    strike_price: Optional[float] = None

    option_type: OptionType = (
        OptionType.NOT_APPLICABLE
    )

    exercise_type: ExerciseType = (
        ExerciseType.NOT_APPLICABLE
    )

    # -------------------------------------------------------------
    # Settlement
    # -------------------------------------------------------------

    settlement_type: SettlementType = (
        SettlementType.UNKNOWN
    )

    settlement_asset: Optional[str] = None

    # -------------------------------------------------------------
    # Contract identity
    # -------------------------------------------------------------

    contract_id: Optional[str] = None

    exchange_symbol: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def validate(self) -> List[str]:

        errors: List[str] = []

        # ---------------------------------------------------------
        # Numeric mechanics
        # ---------------------------------------------------------

        if (
            self.tick_size is not None
            and self.tick_size <= 0
        ):
            errors.append(
                "INVALID_TICK_SIZE"
            )

        if (
            self.price_precision is not None
            and self.price_precision < 0
        ):
            errors.append(
                "INVALID_PRICE_PRECISION"
            )

        if (
            self.lot_size is not None
            and self.lot_size <= 0
        ):
            errors.append(
                "INVALID_LOT_SIZE"
            )

        if (
            self.contract_quantity is not None
            and self.contract_quantity <= 0
        ):
            errors.append(
                "INVALID_CONTRACT_QUANTITY"
            )

        if (
            self.multiplier is not None
            and self.multiplier <= 0
        ):
            errors.append(
                "INVALID_MULTIPLIER"
            )

        if (
            self.strike_price is not None
            and self.strike_price <= 0
        ):
            errors.append(
                "INVALID_STRIKE_PRICE"
            )

        # ---------------------------------------------------------
        # Option mechanics
        # ---------------------------------------------------------

        if self.instrument_type == InstrumentType.OPTION:

            if (
                self.option_type
                == OptionType.NOT_APPLICABLE
            ):
                errors.append(
                    "OPTION_TYPE_REQUIRED"
                )

            if self.strike_price is None:
                errors.append(
                    "OPTION_STRIKE_REQUIRED"
                )

            if (
                self.exercise_type
                == ExerciseType.NOT_APPLICABLE
            ):
                errors.append(
                    "OPTION_EXERCISE_TYPE_REQUIRED"
                )

        else:

            if self.option_type not in (
                OptionType.NOT_APPLICABLE,
                OptionType.UNKNOWN,
            ):
                errors.append(
                    "OPTION_TYPE_ON_NON_OPTION"
                )

        # ---------------------------------------------------------
        # Expiry mechanics
        # ---------------------------------------------------------

        derivative_types = {
            InstrumentType.FUTURE,
            InstrumentType.OPTION,
            InstrumentType.FORWARD,
        }

        if (
            self.instrument_type in derivative_types
            and self.expiry is None
        ):
            errors.append(
                "DERIVATIVE_EXPIRY_REQUIRED"
            )

        # ---------------------------------------------------------
        # Settlement
        # ---------------------------------------------------------

        if (
            self.settlement_type
            == SettlementType.UNKNOWN
        ):
            errors.append(
                "SETTLEMENT_TYPE_UNKNOWN"
            )

        return errors


# =====================================================================
# OBSERVATION
# =====================================================================

@dataclass(frozen=True)
class D8Observation:

    name: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str

    source_id: str

    evidence_kind: EvidenceKind = (
        EvidenceKind.OBSERVED
    )

    valid: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================================
# MECHANIC EVIDENCE
# =====================================================================

@dataclass(frozen=True)
class D8MechanicEvidence:

    name: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str

    evidence_kind: EvidenceKind = (
        EvidenceKind.OBSERVED
    )

    source_ids: Tuple[str, ...] = ()

    conflict_status: ConflictStatus = (
        ConflictStatus.NONE
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================================
# RESULT
# =====================================================================

@dataclass
class D8Result:

    status: D8Status

    mechanics: Optional[D8Mechanics] = None

    evidence: List[D8MechanicEvidence] = (
        field(default_factory=list)
    )

    missing_inputs: List[str] = (
        field(default_factory=list)
    )

    conflicts: List[str] = (
        field(default_factory=list)
    )

    identity_errors: List[str] = (
        field(default_factory=list)
    )

    future_data_errors: List[str] = (
        field(default_factory=list)
    )

    market_id: Optional[str] = None

    instrument_id: Optional[str] = None

    contract_version: Optional[str] = None

    evaluation_time: datetime = field(
        default_factory=_utc_now
    )

    warnings: List[str] = (
        field(default_factory=list)
    )

    def as_dict(self) -> Dict[str, Any]:

        mechanics_dict = None

        if self.mechanics is not None:

            mechanics_dict = {
                "instrument_type": (
                    self.mechanics
                    .instrument_type
                    .value
                ),

                "tick_size": (
                    self.mechanics.tick_size
                ),

                "price_precision": (
                    self.mechanics
                    .price_precision
                ),

                "lot_size": (
                    self.mechanics.lot_size
                ),

                "contract_quantity": (
                    self.mechanics
                    .contract_quantity
                ),

                "multiplier": (
                    self.mechanics.multiplier
                ),

                "expiry": (
                    self.mechanics
                    .expiry.isoformat()
                    if self.mechanics.expiry
                    else None
                ),

                "strike_price": (
                    self.mechanics
                    .strike_price
                ),

                "option_type": (
                    self.mechanics
                    .option_type
                    .value
                ),

                "exercise_type": (
                    self.mechanics
                    .exercise_type
                    .value
                ),

                "settlement_type": (
                    self.mechanics
                    .settlement_type
                    .value
                ),

                "settlement_asset": (
                    self.mechanics
                    .settlement_asset
                ),

                "contract_id": (
                    self.mechanics
                    .contract_id
                ),

                "exchange_symbol": (
                    self.mechanics
                    .exchange_symbol
                ),

                "metadata": dict(
                    self.mechanics.metadata
                ),
            }

        return {
            "status": self.status.value,
            "mechanics": mechanics_dict,

            "evidence": [
                {
                    "name": item.name,
                    "value": item.value,
                    "observed_at": (
                        item.observed_at.isoformat()
                    ),
                    "market_id": item.market_id,
                    "instrument_id": item.instrument_id,
                    "evidence_kind": (
                        item.evidence_kind.value
                    ),
                    "source_ids": list(
                        item.source_ids
                    ),
                    "conflict_status": (
                        item.conflict_status.value
                    ),
                    "metadata": dict(
                        item.metadata
                    ),
                }
                for item in self.evidence
            ],

            "missing_inputs": list(
                self.missing_inputs
            ),

            "conflicts": list(
                self.conflicts
            ),

            "identity_errors": list(
                self.identity_errors
            ),

            "future_data_errors": list(
                self.future_data_errors
            ),

            "market_id": self.market_id,

            "instrument_id": (
                self.instrument_id
            ),

            "contract_version": (
                self.contract_version
            ),

            "evaluation_time": (
                self.evaluation_time
                .isoformat()
            ),

            "warnings": list(
                self.warnings
            ),
        }


# =====================================================================
# D8 ENGINE
# =====================================================================

class D8InstrumentMechanicsEngine:

    def evaluate(
        self,
        *,
        identity: D8Identity,
        mechanics: D8Mechanics,
        evidence: Sequence[
            D8MechanicEvidence
        ] = (),
        observations: Sequence[
            D8Observation
        ] = (),
        evaluation_time: Optional[
            datetime
        ] = None,
        required_mechanics: Optional[
            Sequence[str]
        ] = None,
    ) -> D8Result:

        evaluation_time = _ensure_utc(
            evaluation_time or _utc_now()
        )

        identity_errors = identity.validate()

        market_id = (
            self._canonical_market_id(
                identity
            )
        )

        instrument_id = (
            self._canonical_instrument_id(
                identity
            )
        )

        result = D8Result(
            status=D8Status.READY,

            mechanics=mechanics,

            market_id=market_id,

            instrument_id=instrument_id,

            contract_version=(
                identity.contract_version
            ),

            evaluation_time=evaluation_time,

            identity_errors=identity_errors,
        )

        # -------------------------------------------------------------
        # IDENTITY GUARD
        # -------------------------------------------------------------

        if identity_errors:

            result.status = D8Status.BLOCKED

            result.warnings.append(
                "D8_BLOCKED_IDENTITY_NOT_RESOLVED"
            )

            return result

        # -------------------------------------------------------------
        # MECHANICS VALIDATION
        # -------------------------------------------------------------

        mechanics_errors = mechanics.validate()

        if mechanics_errors:

            result.missing_inputs.extend(
                [
                    error
                    for error in mechanics_errors
                    if (
                        "REQUIRED" in error
                        or "UNKNOWN" in error
                    )
                ]
            )

            result.conflicts.extend(
                [
                    error
                    for error in mechanics_errors
                    if (
                        "INVALID" in error
                        or "ON_NON_OPTION" in error
                    )
                ]
            )

            if any(
                error.startswith(
                    "INVALID"
                )
                for error in mechanics_errors
            ):

                result.status = D8Status.BLOCKED

            elif result.status != D8Status.BLOCKED:

                result.status = D8Status.LIMITED

        # -------------------------------------------------------------
        # REQUIRED MECHANICS
        # -------------------------------------------------------------

        if required_mechanics:

            for required in required_mechanics:

                value = getattr(
                    mechanics,
                    required,
                    None,
                )

                if value is None:

                    result.missing_inputs.append(
                        required
                    )

        # -------------------------------------------------------------
        # EXPIRY FUTURE CHECK
        #
        # Expiry itself is NOT treated as D9 event logic here.
        # Only validity against the evaluation timestamp is checked.
        # -------------------------------------------------------------

        if mechanics.expiry is not None:

            expiry = _ensure_utc(
                mechanics.expiry
            )

            if expiry < evaluation_time:

                result.warnings.append(
                    "CONTRACT_EXPIRY_PAST"
                )

        # -------------------------------------------------------------
        # OBSERVATION VALIDATION
        # -------------------------------------------------------------

        for observation in observations:

            observed_at = _ensure_utc(
                observation.observed_at
            )

            if observed_at > evaluation_time:

                result.future_data_errors.append(
                    observation.name
                )

                result.status = D8Status.BLOCKED

                continue

            if not observation.valid:

                result.missing_inputs.append(
                    "INVALID:"
                    + observation.name
                )

                continue

            if (
                observation.market_id
                != market_id
                or observation.instrument_id
                != instrument_id
            ):

                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + observation.name
                )

                continue

        # -------------------------------------------------------------
        # EVIDENCE VALIDATION
        # -------------------------------------------------------------

        valid_evidence: List[
            D8MechanicEvidence
        ] = []

        for item in evidence:

            observed_at = _ensure_utc(
                item.observed_at
            )

            if observed_at > evaluation_time:

                result.future_data_errors.append(
                    item.name
                )

                result.status = D8Status.BLOCKED

                continue

            if (
                item.market_id != market_id
                or item.instrument_id
                != instrument_id
            ):

                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + item.name
                )

                continue

            valid_evidence.append(item)

        result.evidence.extend(
            valid_evidence
        )

        # -------------------------------------------------------------
        # DUPLICATE MECHANIC CONFLICT
        # -------------------------------------------------------------

        grouped: Dict[
            str,
            List[D8MechanicEvidence]
        ] = {}

        for item in valid_evidence:

            grouped.setdefault(
                item.name,
                []
            ).append(item)

        for name, items in grouped.items():

            if len(items) < 2:
                continue

            values = [
                item.value
                for item in items
            ]

            first = values[0]

            if any(
                value != first
                for value in values[1:]
            ):

                result.conflicts.append(
                    "MECHANIC_VALUE_CONFLICT:"
                    + name
                )

        # -------------------------------------------------------------
        # FINAL STATUS
        # -------------------------------------------------------------

        if result.future_data_errors:

            result.status = D8Status.BLOCKED

        elif result.conflicts:

            if result.status != D8Status.BLOCKED:
                result.status = D8Status.LIMITED

        elif result.missing_inputs:

            if result.status != D8Status.BLOCKED:
                result.status = D8Status.LIMITED

        return result

    # -----------------------------------------------------------------
    # OPTION PAYOFF PRIMITIVE
    # -----------------------------------------------------------------

    @staticmethod
    def intrinsic_option_value(
        *,
        option_type: OptionType,
        underlying_price: float,
        strike_price: float,
    ) -> float:

        if underlying_price <= 0:
            raise ValueError(
                "underlying_price must be > 0"
            )

        if strike_price <= 0:
            raise ValueError(
                "strike_price must be > 0"
            )

        if option_type == OptionType.CALL:

            return max(
                0.0,
                underlying_price
                - strike_price,
            )

        if option_type == OptionType.PUT:

            return max(
                0.0,
                strike_price
                - underlying_price,
            )

        raise ValueError(
            "option_type must be CALL or PUT"
        )

    # -----------------------------------------------------------------
    # CONTRACT NOTIONAL
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_contract_notional(
        *,
        price: float,
        contract_quantity: float = 1.0,
        multiplier: float = 1.0,
    ) -> float:

        if price < 0:
            raise ValueError(
                "price must be >= 0"
            )

        if contract_quantity <= 0:
            raise ValueError(
                "contract_quantity must be > 0"
            )

        if multiplier <= 0:
            raise ValueError(
                "multiplier must be > 0"
            )

        return (
            price
            * contract_quantity
            * multiplier
        )

    # -----------------------------------------------------------------
    # TICK VALUE
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_tick_value(
        *,
        tick_size: float,
        contract_quantity: float = 1.0,
        multiplier: float = 1.0,
    ) -> float:

        if tick_size <= 0:
            raise ValueError(
                "tick_size must be > 0"
            )

        if contract_quantity <= 0:
            raise ValueError(
                "contract_quantity must be > 0"
            )

        if multiplier <= 0:
            raise ValueError(
                "multiplier must be > 0"
            )

        return (
            tick_size
            * contract_quantity
            * multiplier
        )

    # -----------------------------------------------------------------
    # ID HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _canonical_market_id(
        identity: D8Identity,
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
        identity: D8Identity,
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

def evaluate_d8_instrument_mechanics(
    *,
    identity: D8Identity,
    mechanics: D8Mechanics,
    evidence: Sequence[
        D8MechanicEvidence
    ] = (),
    observations: Sequence[
        D8Observation
    ] = (),
    evaluation_time: Optional[
        datetime
    ] = None,
    required_mechanics: Optional[
        Sequence[str]
    ] = None,
) -> D8Result:

    engine = D8InstrumentMechanicsEngine()

    return engine.evaluate(
        identity=identity,
        mechanics=mechanics,
        evidence=evidence,
        observations=observations,
        evaluation_time=evaluation_time,
        required_mechanics=required_mechanics,
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

    # -------------------------------------------------------------
    # NIFTY FUTURE
    # -------------------------------------------------------------

    future_identity = D8Identity(
        category="INDEX_DERIVATIVE",
        underlying="NIFTY",
        instrument="FUTURE",
        contract="NIFTY_FUT",
        venue="NSE",
        market_profile_version="V6",
        instrument_profile_version="V6",
        contract_version="V6",
    )

    future_mechanics = D8Mechanics(
        instrument_type=InstrumentType.FUTURE,
        tick_size=0.05,
        price_precision=2,
        lot_size=65.0,
        contract_quantity=65.0,
        multiplier=1.0,
        expiry=datetime(
            2026,
            9,
            24,
            15,
            30,
            tzinfo=timezone.utc,
        ),
        settlement_type=SettlementType.CASH,
        contract_id="NIFTY-FUT-2026-09",
        exchange_symbol="NIFTY",
    )

    # -------------------------------------------------------------
    # Test 1 — identity
    # -------------------------------------------------------------

    assert (
        future_identity.validate()
        == []
    )

    # -------------------------------------------------------------
    # Test 2 — mechanics
    # -------------------------------------------------------------

    assert (
        future_mechanics.validate()
        == []
    )

    # -------------------------------------------------------------
    # Test 3 — tick value
    # -------------------------------------------------------------

    tick_value = (
        D8InstrumentMechanicsEngine
        .calculate_tick_value(
            tick_size=0.05,
            contract_quantity=65.0,
            multiplier=1.0,
        )
    )

    assert abs(
        tick_value - 3.25
    ) < 1e-12

    # -------------------------------------------------------------
    # Test 4 — contract notional
    # -------------------------------------------------------------

    notional = (
        D8InstrumentMechanicsEngine
        .calculate_contract_notional(
            price=25000.0,
            contract_quantity=65.0,
            multiplier=1.0,
        )
    )

    assert (
        notional
        == 1_625_000.0
    )

    # -------------------------------------------------------------
    # Test 5 — valid evaluation
    # -------------------------------------------------------------

    result = (
        evaluate_d8_instrument_mechanics(
            identity=future_identity,
            mechanics=future_mechanics,
            evaluation_time=evaluation_time,
            required_mechanics=[
                "tick_size",
                "lot_size",
                "expiry",
                "settlement_type",
            ],
        )
    )

    assert (
        result.status
        == D8Status.READY
    )

    # -------------------------------------------------------------
    # OPTION
    # -------------------------------------------------------------

    option_identity = D8Identity(
        category="INDEX_DERIVATIVE",
        underlying="NIFTY",
        instrument="OPTION",
        contract="NIFTY_CE",
        venue="NSE",
        market_profile_version="V6",
        instrument_profile_version="V6",
        contract_version="V6",
    )

    option_mechanics = D8Mechanics(
        instrument_type=InstrumentType.OPTION,
        tick_size=0.05,
        price_precision=2,
        lot_size=65.0,
        contract_quantity=65.0,
        multiplier=1.0,
        expiry=datetime(
            2026,
            9,
            10,
            15,
            30,
            tzinfo=timezone.utc,
        ),
        strike_price=25000.0,
        option_type=OptionType.CALL,
        exercise_type=ExerciseType.EUROPEAN,
        settlement_type=SettlementType.CASH,
        contract_id="NIFTY-25000-CE-2026-09-10",
    )

    # -------------------------------------------------------------
    # Test 6 — option mechanics
    # -------------------------------------------------------------

    assert (
        option_mechanics.validate()
        == []
    )

    # -------------------------------------------------------------
    # Test 7 — call intrinsic value
    # -------------------------------------------------------------

    intrinsic = (
        D8InstrumentMechanicsEngine
        .intrinsic_option_value(
            option_type=OptionType.CALL,
            underlying_price=25100.0,
            strike_price=25000.0,
        )
    )

    assert (
        intrinsic
        == 100.0
    )

    # -------------------------------------------------------------
    # Test 8 — put intrinsic value
    # -------------------------------------------------------------

    intrinsic_put = (
        D8InstrumentMechanicsEngine
        .intrinsic_option_value(
            option_type=OptionType.PUT,
            underlying_price=24900.0,
            strike_price=25000.0,
        )
    )

    assert (
        intrinsic_put
        == 100.0
    )

    # -------------------------------------------------------------
    # Test 9 — future-data guard
    # -------------------------------------------------------------

    future_evidence = D8MechanicEvidence(
        name="future_tick_size",
        value=0.10,
        observed_at=datetime(
            2026,
            9,
            4,
            10,
            1,
            0,
            tzinfo=timezone.utc,
        ),
        market_id=(
            "INDEX_DERIVATIVE|NIFTY|NSE"
        ),
        instrument_id=(
            "INDEX_DERIVATIVE|"
            "NIFTY|FUTURE|"
            "NIFTY_FUT|NSE"
        ),
        source_ids=("TEST",),
    )

    future_result = (
        evaluate_d8_instrument_mechanics(
            identity=future_identity,
            mechanics=future_mechanics,
            evidence=[future_evidence],
            evaluation_time=evaluation_time,
        )
    )

    assert (
        future_result.status
        == D8Status.BLOCKED
    )

    # -------------------------------------------------------------
    # Test 10 — identity mismatch
    # -------------------------------------------------------------

    wrong_evidence = D8MechanicEvidence(
        name="wrong_market_mechanic",
        value=1.0,
        observed_at=evaluation_time,
        market_id="CRYPTO|BTC|BINANCE",
        instrument_id=(
            "CRYPTO|BTC|SPOT|BTCUSDT|BINANCE"
        ),
    )

    mismatch_result = (
        evaluate_d8_instrument_mechanics(
            identity=future_identity,
            mechanics=future_mechanics,
            evidence=[wrong_evidence],
            evaluation_time=evaluation_time,
        )
    )

    assert (
        mismatch_result.status
        == D8Status.LIMITED
    )

    assert any(
        "IDENTITY_MISMATCH" in item
        for item in mismatch_result.conflicts
    )

    # -------------------------------------------------------------
    # Test 11 — invalid derivative without expiry
    # -------------------------------------------------------------

    invalid_future = D8Mechanics(
        instrument_type=InstrumentType.FUTURE,
        tick_size=0.05,
        settlement_type=SettlementType.CASH,
    )

    assert any(
        "DERIVATIVE_EXPIRY_REQUIRED" == error
        for error in invalid_future.validate()
    )

    # -------------------------------------------------------------
    # Test 12 — option without strike
    # -------------------------------------------------------------

    invalid_option = D8Mechanics(
        instrument_type=InstrumentType.OPTION,
        tick_size=0.05,
        expiry=datetime(
            2026,
            9,
            10,
            tzinfo=timezone.utc,
        ),
        option_type=OptionType.CALL,
        exercise_type=ExerciseType.EUROPEAN,
        settlement_type=SettlementType.CASH,
    )

    assert any(
        "OPTION_STRIKE_REQUIRED" == error
        for error in invalid_option.validate()
    )

    # -------------------------------------------------------------
    # Test 13 — margin is not an instrument mechanic
    # -------------------------------------------------------------

    assert (
        "margin"
        not in D8Mechanics.__dataclass_fields__
    )

    # -------------------------------------------------------------
    # Test 14 — incomplete identity
    # -------------------------------------------------------------

    incomplete_identity = D8Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="FUTURE",
        contract="",
        venue="NSE",
    )

    blocked_result = (
        evaluate_d8_instrument_mechanics(
            identity=incomplete_identity,
            mechanics=future_mechanics,
            evaluation_time=evaluation_time,
        )
    )

    assert (
        blocked_result.status
        == D8Status.BLOCKED
    )

    print("D8 SELF-TEST: PASS")


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _self_test()