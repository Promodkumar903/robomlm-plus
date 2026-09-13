"""
ROBOMLM_PLUS
Decision Layer — D7 Liquidity / Volatility

D7 = LIQUIDITY / VOLATILITY

Liquidity and volatility are maintained as separate dimensions.

Liquidity primitives:
    - bid/ask spread
    - spread in basis points
    - bid depth
    - ask depth
    - total visible depth
    - depth imbalance
    - executable quantity
    - market impact / slippage observations

Volatility primitives:
    - realized volatility
    - return volatility
    - range
    - ATR-style range measurement
    - absolute return
    - price dispersion

Engineering rules:
    1. Canonical identity is mandatory.
    2. Liquidity != volume.
    3. Volatility != direction.
    4. No arbitrary 0-100 combined score.
    5. Missing inputs are preserved.
    6. No silent zero/default substitution.
    7. Future observations are rejected.
    8. Stale observations can degrade the result.
    9. Conflicts are surfaced, never silently resolved.
   10. D7 does not make a BUY/SELL decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite, log
from typing import Any, Dict, List, Optional, Sequence, Tuple


# =====================================================================
# ENUMS
# =====================================================================

class D7Status(str, Enum):
    READY = "READY"
    LIMITED = "LIMITED"
    BLOCKED = "BLOCKED"


class D7Dimension(str, Enum):
    LIQUIDITY = "LIQUIDITY"
    VOLATILITY = "VOLATILITY"


class LiquidityType(str, Enum):
    BID_ASK_SPREAD = "BID_ASK_SPREAD"
    SPREAD_BPS = "SPREAD_BPS"
    BID_DEPTH = "BID_DEPTH"
    ASK_DEPTH = "ASK_DEPTH"
    TOTAL_DEPTH = "TOTAL_DEPTH"
    DEPTH_IMBALANCE = "DEPTH_IMBALANCE"
    EXECUTABLE_QUANTITY = "EXECUTABLE_QUANTITY"
    MARKET_IMPACT = "MARKET_IMPACT"
    SLIPPAGE = "SLIPPAGE"
    UNKNOWN = "UNKNOWN"


class VolatilityType(str, Enum):
    REALIZED_VOLATILITY = "REALIZED_VOLATILITY"
    RETURN_VOLATILITY = "RETURN_VOLATILITY"
    ABSOLUTE_RETURN = "ABSOLUTE_RETURN"
    PRICE_RANGE = "PRICE_RANGE"
    ATR_RANGE = "ATR_RANGE"
    DISPERSION = "DISPERSION"
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


def _finite_number(
    value: Any,
    name: str,
) -> float:
    if isinstance(value, bool):
        raise ValueError(
            f"{name} must be numeric, not bool"
        )

    try:
        result = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"{name} must be numeric"
        )

    if not isfinite(result):
        raise ValueError(
            f"{name} must be finite"
        )

    return result


# =====================================================================
# IDENTITY
# =====================================================================

@dataclass(frozen=True)
class D7Identity:
    """
    Canonical market/instrument identity.
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
                errors.append(
                    f"MISSING_IDENTITY:{name}"
                )

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
                errors.append(
                    "MISSING_IDENTITY:base_currency"
                )

            if not self.quote_currency:
                errors.append(
                    "MISSING_IDENTITY:quote_currency"
                )

        return errors


# =====================================================================
# OBSERVATION
# =====================================================================

@dataclass(frozen=True)
class D7Observation:
    """
    Atomic D7 observation.

    The observation explicitly identifies whether it belongs to
    liquidity or volatility.

    A volume observation alone is NOT automatically liquidity evidence.
    """

    name: str
    dimension: D7Dimension
    metric_type: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str
    source_id: str

    evidence_kind: EvidenceKind = EvidenceKind.OBSERVED

    valid: bool = True

    unit: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def age_seconds(
        self,
        evaluation_time: datetime,
    ) -> float:
        return _age_seconds(
            self.observed_at,
            evaluation_time,
        )


# =====================================================================
# LIQUIDITY EVIDENCE
# =====================================================================

@dataclass(frozen=True)
class D7Liquidity:
    """
    Structured liquidity evidence.

    No proprietary score is generated.
    """

    liquidity_type: LiquidityType

    name: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str

    evidence_kind: EvidenceKind = (
        EvidenceKind.DERIVED
    )

    source_ids: Tuple[str, ...] = ()

    unit: Optional[str] = None

    conflict_status: ConflictStatus = (
        ConflictStatus.NONE
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# =====================================================================
# VOLATILITY EVIDENCE
# =====================================================================

@dataclass(frozen=True)
class D7Volatility:
    """
    Structured volatility evidence.

    Volatility is magnitude/dispersion information.
    It is not automatically bullish or bearish.
    """

    volatility_type: VolatilityType

    name: str
    value: Any

    observed_at: datetime

    market_id: str
    instrument_id: str

    evidence_kind: EvidenceKind = (
        EvidenceKind.DERIVED
    )

    source_ids: Tuple[str, ...] = ()

    unit: Optional[str] = None

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
class D7Result:

    status: D7Status

    liquidity: List[D7Liquidity] = field(
        default_factory=list
    )

    volatility: List[D7Volatility] = field(
        default_factory=list
    )

    missing_inputs: List[str] = field(
        default_factory=list
    )

    stale_inputs: List[str] = field(
        default_factory=list
    )

    conflicts: List[str] = field(
        default_factory=list
    )

    identity_errors: List[str] = field(
        default_factory=list
    )

    market_id: Optional[str] = None
    instrument_id: Optional[str] = None

    contract_version: Optional[str] = None

    evaluation_time: datetime = field(
        default_factory=_utc_now
    )

    warnings: List[str] = field(
        default_factory=list
    )

    def as_dict(self) -> Dict[str, Any]:

        return {
            "status": self.status.value,

            "liquidity": [
                {
                    "liquidity_type": (
                        item.liquidity_type.value
                    ),
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
                    "unit": item.unit,
                    "conflict_status": (
                        item.conflict_status.value
                    ),
                    "metadata": dict(
                        item.metadata
                    ),
                }
                for item in self.liquidity
            ],

            "volatility": [
                {
                    "volatility_type": (
                        item.volatility_type.value
                    ),
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
                    "unit": item.unit,
                    "conflict_status": (
                        item.conflict_status.value
                    ),
                    "metadata": dict(
                        item.metadata
                    ),
                }
                for item in self.volatility
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
            "contract_version": (
                self.contract_version
            ),

            "evaluation_time": (
                self.evaluation_time.isoformat()
            ),

            "warnings": list(
                self.warnings
            ),
        }


# =====================================================================
# D7 ENGINE
# =====================================================================

class D7LiquidityVolatilityEngine:
    """
    D7 Liquidity / Volatility engine.

    Liquidity and volatility are independently represented.
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
        identity: D7Identity,
        observations: Sequence[D7Observation],
        liquidity: Sequence[D7Liquidity],
        volatility: Sequence[D7Volatility],
        evaluation_time: Optional[
            datetime
        ] = None,
        required_liquidity: Optional[
            Sequence[LiquidityType]
        ] = None,
        required_volatility: Optional[
            Sequence[VolatilityType]
        ] = None,
    ) -> D7Result:

        evaluation_time = _ensure_utc(
            evaluation_time or _utc_now()
        )

        identity_errors = identity.validate()

        result = D7Result(
            status=D7Status.READY,

            market_id=self._canonical_market_id(
                identity
            ),

            instrument_id=(
                self._canonical_instrument_id(
                    identity
                )
            ),

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

            result.status = D7Status.BLOCKED

            result.warnings.append(
                "D7_BLOCKED_IDENTITY_NOT_RESOLVED"
            )

            return result

        # -------------------------------------------------------------
        # REQUIRED TYPES
        # -------------------------------------------------------------

        available_liquidity = {
            item.metric_type
            for item in observations
            if (
                item.valid
                and item.dimension
                == D7Dimension.LIQUIDITY
            )
        }

        available_volatility = {
            item.metric_type
            for item in observations
            if (
                item.valid
                and item.dimension
                == D7Dimension.VOLATILITY
            )
        }

        if required_liquidity:

            for required in required_liquidity:

                if required.value not in (
                    available_liquidity
                ):

                    result.missing_inputs.append(
                        "LIQUIDITY_TYPE:"
                        + required.value
                    )

        if required_volatility:

            for required in required_volatility:

                if required.value not in (
                    available_volatility
                ):

                    result.missing_inputs.append(
                        "VOLATILITY_TYPE:"
                        + required.value
                    )

        # -------------------------------------------------------------
        # OBSERVATION VALIDATION
        # -------------------------------------------------------------

        valid_observations: List[
            D7Observation
        ] = []

        for observation in observations:

            observed_at = _ensure_utc(
                observation.observed_at
            )

            # Future-data protection
            if observed_at > evaluation_time:

                result.status = D7Status.BLOCKED

                result.warnings.append(
                    "FUTURE_DATA_REJECTED:"
                    + observation.name
                )

                continue

            if not observation.valid:

                result.missing_inputs.append(
                    "INVALID:"
                    + observation.name
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
        # LIQUIDITY VALIDATION
        # -------------------------------------------------------------

        valid_liquidity: List[
            D7Liquidity
        ] = []

        for item in liquidity:

            observed_at = _ensure_utc(
                item.observed_at
            )

            if observed_at > evaluation_time:

                result.status = D7Status.BLOCKED

                result.warnings.append(
                    "FUTURE_LIQUIDITY_REJECTED:"
                    + item.name
                )

                continue

            if (
                item.market_id
                != result.market_id
                or item.instrument_id
                != result.instrument_id
            ):

                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + item.name
                )

                continue

            valid_liquidity.append(item)

        result.liquidity.extend(
            valid_liquidity
        )

        # -------------------------------------------------------------
        # VOLATILITY VALIDATION
        # -------------------------------------------------------------

        valid_volatility: List[
            D7Volatility
        ] = []

        for item in volatility:

            observed_at = _ensure_utc(
                item.observed_at
            )

            if observed_at > evaluation_time:

                result.status = D7Status.BLOCKED

                result.warnings.append(
                    "FUTURE_VOLATILITY_REJECTED:"
                    + item.name
                )

                continue

            if (
                item.market_id
                != result.market_id
                or item.instrument_id
                != result.instrument_id
            ):

                result.conflicts.append(
                    "IDENTITY_MISMATCH:"
                    + item.name
                )

                continue

            valid_volatility.append(item)

        result.volatility.extend(
            valid_volatility
        )

        # -------------------------------------------------------------
        # CONFLICT DETECTION
        # -------------------------------------------------------------

        detected_conflicts = (
            self._detect_conflicts(
                valid_liquidity,
                valid_volatility,
            )
        )

        result.conflicts.extend(
            detected_conflicts
        )

        if detected_conflicts:

            result.status = D7Status.LIMITED

            result.warnings.append(
                "D7_CONFLICT_PRESENT"
            )

        # -------------------------------------------------------------
        # MISSING
        # -------------------------------------------------------------

        if result.missing_inputs:

            if result.status != D7Status.BLOCKED:
                result.status = D7Status.LIMITED

        # -------------------------------------------------------------
        # STALE
        # -------------------------------------------------------------

        if result.stale_inputs:

            if result.status != D7Status.BLOCKED:
                result.status = D7Status.LIMITED

        # -------------------------------------------------------------
        # NO LIQUIDITY
        # -------------------------------------------------------------

        if not valid_liquidity:

            if result.status != D7Status.BLOCKED:
                result.status = D7Status.LIMITED

            result.warnings.append(
                "NO_VALID_LIQUIDITY_EVIDENCE"
            )

        # -------------------------------------------------------------
        # NO VOLATILITY
        # -------------------------------------------------------------

        if not valid_volatility:

            if result.status != D7Status.BLOCKED:
                result.status = D7Status.LIMITED

            result.warnings.append(
                "NO_VALID_VOLATILITY_EVIDENCE"
            )

        return result

    # -----------------------------------------------------------------
    # LIQUIDITY BUILDERS
    # -----------------------------------------------------------------

    @staticmethod
    def build_liquidity(
        *,
        liquidity_type: LiquidityType,
        name: str,
        value: Any,
        observed_at: datetime,
        market_id: str,
        instrument_id: str,
        evidence_kind: EvidenceKind = (
            EvidenceKind.DERIVED
        ),
        source_ids: Sequence[str] = (),
        unit: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> D7Liquidity:

        return D7Liquidity(
            liquidity_type=liquidity_type,
            name=name,
            value=value,
            observed_at=_ensure_utc(
                observed_at
            ),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=evidence_kind,
            source_ids=tuple(source_ids),
            unit=unit,
            metadata=dict(metadata or {}),
        )

    # -----------------------------------------------------------------
    # VOLATILITY BUILDER
    # -----------------------------------------------------------------

    @staticmethod
    def build_volatility(
        *,
        volatility_type: VolatilityType,
        name: str,
        value: Any,
        observed_at: datetime,
        market_id: str,
        instrument_id: str,
        evidence_kind: EvidenceKind = (
            EvidenceKind.DERIVED
        ),
        source_ids: Sequence[str] = (),
        unit: Optional[str] = None,
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> D7Volatility:

        return D7Volatility(
            volatility_type=volatility_type,
            name=name,
            value=value,
            observed_at=_ensure_utc(
                observed_at
            ),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=evidence_kind,
            source_ids=tuple(source_ids),
            unit=unit,
            metadata=dict(metadata or {}),
        )

    # -----------------------------------------------------------------
    # SPREAD
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_spread(
        bid: float,
        ask: float,
    ) -> float:

        bid = _finite_number(
            bid,
            "bid",
        )

        ask = _finite_number(
            ask,
            "ask",
        )

        if bid < 0 or ask < 0:
            raise ValueError(
                "bid and ask must be >= 0"
            )

        if ask < bid:
            raise ValueError(
                "ask cannot be below bid"
            )

        return ask - bid

    # -----------------------------------------------------------------
    # SPREAD BPS
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_spread_bps(
        bid: float,
        ask: float,
    ) -> float:

        bid = _finite_number(
            bid,
            "bid",
        )

        ask = _finite_number(
            ask,
            "ask",
        )

        if bid <= 0:
            raise ValueError(
                "bid must be > 0"
            )

        spread = (
            D7LiquidityVolatilityEngine
            .calculate_spread(
                bid,
                ask,
            )
        )

        mid = (
            bid + ask
        ) / 2.0

        if mid <= 0:
            raise ValueError(
                "mid price must be > 0"
            )

        return (
            spread
            / mid
            * 10_000.0
        )

    # -----------------------------------------------------------------
    # DEPTH IMBALANCE
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_depth_imbalance(
        bid_depth: float,
        ask_depth: float,
    ) -> float:

        bid_depth = _finite_number(
            bid_depth,
            "bid_depth",
        )

        ask_depth = _finite_number(
            ask_depth,
            "ask_depth",
        )

        if bid_depth < 0:
            raise ValueError(
                "bid_depth must be >= 0"
            )

        if ask_depth < 0:
            raise ValueError(
                "ask_depth must be >= 0"
            )

        denominator = (
            bid_depth
            + ask_depth
        )

        if denominator == 0:
            raise ValueError(
                "Cannot calculate depth imbalance "
                "when total depth = 0"
            )

        return (
            bid_depth
            - ask_depth
        ) / denominator

    # -----------------------------------------------------------------
    # LOG RETURN
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_log_return(
        previous_price: float,
        current_price: float,
    ) -> float:

        previous_price = _finite_number(
            previous_price,
            "previous_price",
        )

        current_price = _finite_number(
            current_price,
            "current_price",
        )

        if previous_price <= 0:
            raise ValueError(
                "previous_price must be > 0"
            )

        if current_price <= 0:
            raise ValueError(
                "current_price must be > 0"
            )

        return log(
            current_price
            / previous_price
        )

    # -----------------------------------------------------------------
    # REALIZED VOLATILITY
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_realized_volatility(
        prices: Sequence[float],
        *,
        annualization_factor: Optional[
            float
        ] = None,
    ) -> float:

        """
        Realized volatility from log returns.

        If annualization_factor is supplied:

            sigma_annual =
                std(log_returns)
                * sqrt(annualization_factor)

        Without it, returns the period volatility.

        The annualization factor is deliberately not hard-coded because
        it depends on market, timeframe and observation convention.
        """

        if len(prices) < 2:
            raise ValueError(
                "At least two prices are required"
            )

        numeric_prices = [
            _finite_number(
                price,
                "price",
            )
            for price in prices
        ]

        for price in numeric_prices:
            if price <= 0:
                raise ValueError(
                    "All prices must be > 0"
                )

        returns = [
            D7LiquidityVolatilityEngine
            .calculate_log_return(
                numeric_prices[i - 1],
                numeric_prices[i],
            )
            for i in range(
                1,
                len(numeric_prices),
            )
        ]

        mean_return = (
            sum(returns)
            / len(returns)
        )

        variance = (
            sum(
                (r - mean_return) ** 2
                for r in returns
            )
            / len(returns)
        )

        volatility = variance ** 0.5

        if annualization_factor is not None:

            if annualization_factor <= 0:
                raise ValueError(
                    "annualization_factor "
                    "must be > 0"
                )

            volatility *= (
                annualization_factor ** 0.5
            )

        return volatility

    # -----------------------------------------------------------------
    # PRICE RANGE
    # -----------------------------------------------------------------

    @staticmethod
    def calculate_price_range(
        high: float,
        low: float,
    ) -> float:

        high = _finite_number(
            high,
            "high",
        )

        low = _finite_number(
            low,
            "low",
        )

        if high < 0 or low < 0:
            raise ValueError(
                "high and low must be >= 0"
            )

        if high < low:
            raise ValueError(
                "high cannot be below low"
            )

        return high - low

    # -----------------------------------------------------------------
    # CONFLICT DETECTION
    # -----------------------------------------------------------------

    @staticmethod
    def _detect_conflicts(
        liquidity: Sequence[D7Liquidity],
        volatility: Sequence[D7Volatility],
    ) -> List[str]:

        conflicts: List[str] = []

        # Same metric from multiple sources with materially different
        # values is retained as a conflict rather than silently choosing
        # one source.

        liquidity_groups: Dict[
            str,
            List[D7Liquidity],
        ] = {}

        for item in liquidity:

            liquidity_groups.setdefault(
                item.name,
                [],
            ).append(item)

        for name, items in liquidity_groups.items():

            values = []

            for item in items:

                try:
                    values.append(
                        float(item.value)
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

            if len(values) >= 2:

                first = values[0]

                if any(
                    value != first
                    for value in values[1:]
                ):

                    conflicts.append(
                        "LIQUIDITY_VALUE_CONFLICT:"
                        + name
                    )

        volatility_groups: Dict[
            str,
            List[D7Volatility],
        ] = {}

        for item in volatility:

            volatility_groups.setdefault(
                item.name,
                [],
            ).append(item)

        for name, items in volatility_groups.items():

            values = []

            for item in items:

                try:
                    values.append(
                        float(item.value)
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

            if len(values) >= 2:

                first = values[0]

                if any(
                    value != first
                    for value in values[1:]
                ):

                    conflicts.append(
                        "VOLATILITY_VALUE_CONFLICT:"
                        + name
                    )

        return conflicts

    # -----------------------------------------------------------------
    # ID HELPERS
    # -----------------------------------------------------------------

    @staticmethod
    def _canonical_market_id(
        identity: D7Identity,
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
        identity: D7Identity,
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

def evaluate_d7_liquidity_volatility(
    *,
    identity: D7Identity,
    observations: Sequence[D7Observation],
    liquidity: Sequence[D7Liquidity],
    volatility: Sequence[D7Volatility],
    evaluation_time: Optional[
        datetime
    ] = None,
    required_liquidity: Optional[
        Sequence[LiquidityType]
    ] = None,
    required_volatility: Optional[
        Sequence[VolatilityType]
    ] = None,
    max_age_seconds: Optional[float] = None,
) -> D7Result:

    engine = D7LiquidityVolatilityEngine(
        max_age_seconds=max_age_seconds
    )

    return engine.evaluate(
        identity=identity,
        observations=observations,
        liquidity=liquidity,
        volatility=volatility,
        evaluation_time=evaluation_time,
        required_liquidity=required_liquidity,
        required_volatility=required_volatility,
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

    identity = D7Identity(
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
    # Test 2 — spread
    # -------------------------------------------------------------

    spread = (
        D7LiquidityVolatilityEngine
        .calculate_spread(
            25000.0,
            25001.0,
        )
    )

    assert abs(
        spread - 1.0
    ) < 1e-12

    # -------------------------------------------------------------
    # Test 3 — spread BPS
    # -------------------------------------------------------------

    spread_bps = (
        D7LiquidityVolatilityEngine
        .calculate_spread_bps(
            25000.0,
            25001.0,
        )
    )

    assert spread_bps > 0.0

    # -------------------------------------------------------------
    # Test 4 — depth imbalance
    # -------------------------------------------------------------

    imbalance = (
        D7LiquidityVolatilityEngine
        .calculate_depth_imbalance(
            750.0,
            250.0,
        )
    )

    assert abs(
        imbalance - 0.5
    ) < 1e-12

    # -------------------------------------------------------------
    # Test 5 — log return
    # -------------------------------------------------------------

    log_return = (
        D7LiquidityVolatilityEngine
        .calculate_log_return(
            100.0,
            110.0,
        )
    )

    assert log_return > 0.0

    # -------------------------------------------------------------
    # Test 6 — realized volatility
    # -------------------------------------------------------------

    volatility_value = (
        D7LiquidityVolatilityEngine
        .calculate_realized_volatility(
            [
                100.0,
                101.0,
                99.0,
                102.0,
            ]
        )
    )

    assert volatility_value > 0.0

    # -------------------------------------------------------------
    # Test 7 — valid D7 evaluation
    # -------------------------------------------------------------

    observation_spread = D7Observation(
        name="spread_bps",
        dimension=D7Dimension.LIQUIDITY,
        metric_type=(
            LiquidityType.SPREAD_BPS.value
        ),
        value=0.4,
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
        unit="bps",
    )

    observation_vol = D7Observation(
        name="realized_volatility",
        dimension=D7Dimension.VOLATILITY,
        metric_type=(
            VolatilityType.REALIZED_VOLATILITY.value
        ),
        value=0.012,
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
        unit="period",
    )

    liquidity_item = (
        D7LiquidityVolatilityEngine
        .build_liquidity(
            liquidity_type=(
                LiquidityType.SPREAD_BPS
            ),
            name="spread_bps",
            value=0.4,
            observed_at=(
                observation_spread.observed_at
            ),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=(
                EvidenceKind.OBSERVED
            ),
            source_ids=("TEST_SOURCE",),
            unit="bps",
        )
    )

    volatility_item = (
        D7LiquidityVolatilityEngine
        .build_volatility(
            volatility_type=(
                VolatilityType.REALIZED_VOLATILITY
            ),
            name="realized_volatility",
            value=0.012,
            observed_at=(
                observation_vol.observed_at
            ),
            market_id=market_id,
            instrument_id=instrument_id,
            evidence_kind=(
                EvidenceKind.OBSERVED
            ),
            source_ids=("TEST_SOURCE",),
            unit="period",
        )
    )

    result = (
        evaluate_d7_liquidity_volatility(
            identity=identity,
            observations=[
                observation_spread,
                observation_vol,
            ],
            liquidity=[
                liquidity_item
            ],
            volatility=[
                volatility_item
            ],
            evaluation_time=evaluation_time,
            required_liquidity=[
                LiquidityType.SPREAD_BPS
            ],
            required_volatility=[
                VolatilityType.REALIZED_VOLATILITY
            ],
            max_age_seconds=300,
        )
    )

    assert result.status == D7Status.READY
    assert len(result.liquidity) == 1
    assert len(result.volatility) == 1

    # -------------------------------------------------------------
    # Test 8 — future data
    # -------------------------------------------------------------

    future_observation = D7Observation(
        name="future_spread",
        dimension=D7Dimension.LIQUIDITY,
        metric_type=(
            LiquidityType.SPREAD_BPS.value
        ),
        value=0.2,
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
    )

    future_result = (
        evaluate_d7_liquidity_volatility(
            identity=identity,
            observations=[
                future_observation
            ],
            liquidity=[],
            volatility=[],
            evaluation_time=evaluation_time,
        )
    )

    assert (
        future_result.status
        == D7Status.BLOCKED
    )

    # -------------------------------------------------------------
    # Test 9 — identity mismatch
    # -------------------------------------------------------------

    wrong_liquidity = (
        D7LiquidityVolatilityEngine
        .build_liquidity(
            liquidity_type=(
                LiquidityType.BID_DEPTH
            ),
            name="wrong_market_depth",
            value=100.0,
            observed_at=evaluation_time,
            market_id="CRYPTO|BTC|BINANCE",
            instrument_id=(
                "CRYPTO|BTC|SPOT|BTCUSDT|BINANCE"
            ),
        )
    )

    mismatch_result = (
        evaluate_d7_liquidity_volatility(
            identity=identity,
            observations=[],
            liquidity=[
                wrong_liquidity
            ],
            volatility=[],
            evaluation_time=evaluation_time,
        )
    )

    assert (
        mismatch_result.status
        == D7Status.LIMITED
    )

    assert any(
        "IDENTITY_MISMATCH" in item
        for item in mismatch_result.conflicts
    )

    # -------------------------------------------------------------
    # Test 10 — zero depth must not become zero imbalance
    # -------------------------------------------------------------

    try:
        D7LiquidityVolatilityEngine.calculate_depth_imbalance(
            0.0,
            0.0,
        )

        raise AssertionError(
            "Zero-depth imbalance must fail"
        )

    except ValueError:
        pass

    # -------------------------------------------------------------
    # Test 11 — invalid spread
    # -------------------------------------------------------------

    try:
        D7LiquidityVolatilityEngine.calculate_spread(
            101.0,
            100.0,
        )

        raise AssertionError(
            "ask < bid must fail"
        )

    except ValueError:
        pass

    # -------------------------------------------------------------
    # Test 12 — incomplete identity
    # -------------------------------------------------------------

    incomplete_identity = D7Identity(
        category="INDEX",
        underlying="NIFTY",
        instrument="SPOT",
        contract="INDEX",
        venue="",
    )

    blocked_result = (
        evaluate_d7_liquidity_volatility(
            identity=incomplete_identity,
            observations=[],
            liquidity=[],
            volatility=[],
            evaluation_time=evaluation_time,
        )
    )

    assert (
        blocked_result.status
        == D7Status.BLOCKED
    )

    print("D7 SELF-TEST: PASS")


# =====================================================================
# ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    _self_test()