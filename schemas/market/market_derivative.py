"""
ROBOMLM PLUS
V6 Market Derivative Schema

Purpose:
    Structural representation of derivative-market information.

Rules:
    - Derivative representation only.
    - No trading decision.
    - No execution logic.
    - No order generation.
    - No prediction.
    - No V7+ dependency.
    - Underlying identity and derivative identity remain distinct.
    - Observed and derived information remain distinguishable.
    - Expiry is represented explicitly.
    - Does not mutate source data.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_DERIVATIVE_SCHEMA_VERSION = "1.0.0"
MARKET_DERIVATIVE_SCHEMA = "V6_MARKET_DERIVATIVE"


@dataclass(frozen=True)
class MarketDerivative:
    """
    Immutable structural representation of derivative information.

    This schema describes derivative instruments and their observed or
    derived market attributes. It does not determine trade direction,
    position sizing, or execution.
    """

    # ------------------------------------------------------------------
    # Derivative Identity
    # ------------------------------------------------------------------

    derivative_id: Optional[str] = None
    timestamp: Optional[str] = None
    sequence: Optional[int] = None

    # ------------------------------------------------------------------
    # Market / Underlying Identity
    # ------------------------------------------------------------------

    market: Optional[str] = None
    underlying: Optional[str] = None
    underlying_symbol: Optional[str] = None
    instrument: Optional[str] = None
    symbol: Optional[str] = None

    # ------------------------------------------------------------------
    # Venue / Contract Identity
    # ------------------------------------------------------------------

    exchange: Optional[str] = None
    venue: Optional[str] = None
    contract: Optional[str] = None
    contract_type: Optional[str] = None
    derivative_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Expiry Identity
    # ------------------------------------------------------------------

    expiry: Optional[str] = None
    expiry_timestamp: Optional[str] = None
    days_to_expiry: Optional[float] = None

    # ------------------------------------------------------------------
    # Option Identity
    # ------------------------------------------------------------------

    option_type: Optional[str] = None
    strike: Optional[float] = None

    # ------------------------------------------------------------------
    # Contract Economics
    # ------------------------------------------------------------------

    contract_size: Optional[float] = None
    lot_size: Optional[float] = None
    tick_size: Optional[float] = None
    multiplier: Optional[float] = None

    # ------------------------------------------------------------------
    # Price / Premium
    # ------------------------------------------------------------------

    price: Optional[float] = None
    previous_price: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    premium: Optional[float] = None
    intrinsic_value: Optional[float] = None
    time_value: Optional[float] = None

    # ------------------------------------------------------------------
    # Participation / Open Interest
    # ------------------------------------------------------------------

    volume: Optional[float] = None
    open_interest: Optional[float] = None
    previous_open_interest: Optional[float] = None
    open_interest_change: Optional[float] = None

    # ------------------------------------------------------------------
    # Greeks / Volatility
    # ------------------------------------------------------------------

    implied_volatility: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None

    # ------------------------------------------------------------------
    # Derived Relationships
    # ------------------------------------------------------------------

    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
    open_interest_change_percent: Optional[float] = None
    bid_ask_spread: Optional[float] = None
    mid_price: Optional[float] = None

    # ------------------------------------------------------------------
    # Structural Classification
    # ------------------------------------------------------------------

    moneyness: Optional[str] = None
    liquidity_state: Optional[str] = None
    participation_state: Optional[str] = None
    expiry_state: Optional[str] = None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    observation_id: Optional[str] = None
    context_id: Optional[str] = None
    regime_id: Optional[str] = None
    structure_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    source: Optional[str] = None
    source_type: Optional[str] = None

    # ------------------------------------------------------------------
    # Observed / Derived Separation
    # ------------------------------------------------------------------

    observed_fields: tuple[str, ...] = field(default_factory=tuple)
    derived_fields: tuple[str, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate structural derivative information."""

        if self.sequence is not None:
            if isinstance(self.sequence, bool):
                raise TypeError(
                    "MarketDerivative.sequence must be an integer or None."
                )

            if not isinstance(self.sequence, int):
                raise TypeError(
                    "MarketDerivative.sequence must be an integer or None."
                )

            if self.sequence < 0:
                raise ValueError(
                    "MarketDerivative.sequence cannot be negative."
                )

        numeric_fields = {
            "days_to_expiry": self.days_to_expiry,
            "strike": self.strike,
            "contract_size": self.contract_size,
            "lot_size": self.lot_size,
            "tick_size": self.tick_size,
            "multiplier": self.multiplier,
            "price": self.price,
            "previous_price": self.previous_price,
            "bid": self.bid,
            "ask": self.ask,
            "premium": self.premium,
            "intrinsic_value": self.intrinsic_value,
            "time_value": self.time_value,
            "volume": self.volume,
            "open_interest": self.open_interest,
            "previous_open_interest": self.previous_open_interest,
            "open_interest_change": self.open_interest_change,
            "implied_volatility": self.implied_volatility,
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
            "price_change": self.price_change,
            "price_change_percent": self.price_change_percent,
            "open_interest_change_percent": (
                self.open_interest_change_percent
            ),
            "bid_ask_spread": self.bid_ask_spread,
            "mid_price": self.mid_price,
        }

        for field_name, value in numeric_fields.items():
            if value is None:
                continue

            if isinstance(value, bool):
                raise TypeError(
                    f"MarketDerivative.{field_name} "
                    "must be numeric or None."
                )

            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"MarketDerivative.{field_name} "
                    "must be numeric or None."
                )

        non_negative_fields = (
            "days_to_expiry",
            "strike",
            "contract_size",
            "lot_size",
            "tick_size",
            "multiplier",
            "price",
            "previous_price",
            "bid",
            "ask",
            "premium",
            "intrinsic_value",
            "time_value",
            "volume",
            "open_interest",
            "previous_open_interest",
            "implied_volatility",
            "bid_ask_spread",
            "mid_price",
        )

        for field_name in non_negative_fields:
            value = getattr(self, field_name)

            if value is not None and value < 0:
                raise ValueError(
                    f"MarketDerivative.{field_name} cannot be negative."
                )

        if self.option_type is not None:
            normalized_option_type = self.option_type.upper()

            if normalized_option_type not in {
                "CALL",
                "PUT",
                "CE",
                "PE",
            }:
                raise ValueError(
                    "MarketDerivative.option_type must be "
                    "CALL, PUT, CE, or PE when provided."
                )

        if self.metadata is None:
            raise TypeError(
                "MarketDerivative.metadata must be a mapping."
            )

        if not isinstance(self.metadata, Mapping):
            raise TypeError(
                "MarketDerivative.metadata must be a mapping."
            )

        if isinstance(self.observed_fields, str):
            raise TypeError(
                "MarketDerivative.observed_fields "
                "must be a sequence of names."
            )

        if isinstance(self.derived_fields, str):
            raise TypeError(
                "MarketDerivative.derived_fields "
                "must be a sequence of names."
            )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def has_identity(self) -> bool:
        """Return True when derivative identity is available."""

        return bool(
            self.derivative_id
            or self.instrument
            or self.symbol
        )

    def has_market_identity(self) -> bool:
        """Return True when market or underlying identity exists."""

        return bool(
            self.market
            or self.underlying
            or self.underlying_symbol
        )

    def has_contract_identity(self) -> bool:
        """Return True when contract identity is available."""

        return bool(
            self.contract
            or self.contract_type
            or self.derivative_type
        )

    # ------------------------------------------------------------------
    # Expiry
    # ------------------------------------------------------------------

    def has_expiry(self) -> bool:
        """Return True when expiry information is available."""

        return bool(
            self.expiry
            or self.expiry_timestamp
        )

    def has_days_to_expiry(self) -> bool:
        """Return True when days-to-expiry is available."""

        return self.days_to_expiry is not None

    # ------------------------------------------------------------------
    # Option Structure
    # ------------------------------------------------------------------

    def is_option(self) -> bool:
        """Return True when an option type is specified."""

        return self.option_type is not None

    def is_future(self) -> bool:
        """Return True when the derivative type indicates a future."""

        values = {
            str(self.derivative_type or "").upper(),
            str(self.contract_type or "").upper(),
        }

        return bool(
            values.intersection(
                {"FUTURE", "FUTURES", "FUT"}
            )
        )

    # ------------------------------------------------------------------
    # Price Calculations
    # ------------------------------------------------------------------

    def calculate_mid_price(self) -> Optional[float]:
        """Calculate bid/ask midpoint."""

        if self.bid is None or self.ask is None:
            return None

        return (self.bid + self.ask) / 2.0

    def calculate_bid_ask_spread(self) -> Optional[float]:
        """Calculate bid/ask spread."""

        if self.bid is None or self.ask is None:
            return None

        return self.ask - self.bid

    def calculate_price_change(self) -> Optional[float]:
        """Calculate absolute price change."""

        if self.price is None or self.previous_price is None:
            return None

        return self.price - self.previous_price

    def calculate_price_change_percent(self) -> Optional[float]:
        """Calculate percentage price change."""

        if self.price is None or self.previous_price is None:
            return None

        if self.previous_price == 0:
            return None

        return (
            (self.price - self.previous_price)
            / self.previous_price
        ) * 100.0

    # ------------------------------------------------------------------
    # Open Interest
    # ------------------------------------------------------------------

    def calculate_open_interest_change(self) -> Optional[float]:
        """Calculate absolute open-interest change."""

        if (
            self.open_interest is None
            or self.previous_open_interest is None
        ):
            return None

        return (
            self.open_interest
            - self.previous_open_interest
        )

    def calculate_open_interest_change_percent(
        self,
    ) -> Optional[float]:
        """Calculate percentage open-interest change."""

        if (
            self.open_interest is None
            or self.previous_open_interest is None
        ):
            return None

        if self.previous_open_interest == 0:
            return None

        return (
            (
                self.open_interest
                - self.previous_open_interest
            )
            / self.previous_open_interest
        ) * 100.0

    # ------------------------------------------------------------------
    # Structural Availability
    # ------------------------------------------------------------------

    def has_price(self) -> bool:
        """Return True when derivative price exists."""

        return self.price is not None

    def has_order_book(self) -> bool:
        """Return True when bid and ask are available."""

        return (
            self.bid is not None
            and self.ask is not None
        )

    def has_volume(self) -> bool:
        """Return True when volume exists."""

        return self.volume is not None

    def has_open_interest(self) -> bool:
        """Return True when open interest exists."""

        return self.open_interest is not None

    def has_greeks(self) -> bool:
        """Return True when at least one Greek exists."""

        return any(
            value is not None
            for value in (
                self.delta,
                self.gamma,
                self.theta,
                self.vega,
            )
        )

    def has_volatility(self) -> bool:
        """Return True when implied volatility exists."""

        return self.implied_volatility is not None

    # ------------------------------------------------------------------
    # Source References
    # ------------------------------------------------------------------

    def has_source_reference(self) -> bool:
        """Return True when an upstream reference exists."""

        return bool(
            self.observation_id
            or self.context_id
            or self.regime_id
            or self.structure_id
        )

    # ------------------------------------------------------------------
    # Provenance
    # ------------------------------------------------------------------

    def observed_field_names(self) -> tuple[str, ...]:
        """Return explicitly observed fields."""

        return tuple(self.observed_fields)

    def derived_field_names(self) -> tuple[str, ...]:
        """Return explicitly derived fields."""

        return tuple(self.derived_fields)

    # ------------------------------------------------------------------
    # Structural Validation
    # ------------------------------------------------------------------

    def issue_flags(self) -> tuple[str, ...]:
        """
        Return structural derivative issues.

        Validation only. No trading decision is produced.
        """

        issues: list[str] = []

        if not self.has_identity():
            issues.append("MISSING_DERIVATIVE_IDENTITY")

        if not self.has_market_identity():
            issues.append("MISSING_MARKET_IDENTITY")

        if not self.timestamp:
            issues.append("MISSING_TIMESTAMP")

        if not self.source:
            issues.append("MISSING_SOURCE")

        if not self.has_contract_identity():
            issues.append("MISSING_CONTRACT_IDENTITY")

        if not self.has_expiry():
            issues.append("MISSING_EXPIRY")

        if (
            self.bid is not None
            and self.ask is not None
            and self.ask < self.bid
        ):
            issues.append("INVALID_BID_ASK_RELATION")

        if (
            self.price is not None
            and self.previous_price is not None
            and self.previous_price == 0
        ):
            issues.append("ZERO_PREVIOUS_PRICE")

        if (
            self.open_interest is not None
            and self.previous_open_interest is not None
            and self.previous_open_interest < 0
        ):
            issues.append("INVALID_PREVIOUS_OPEN_INTEREST")

        if not self.has_source_reference():
            issues.append("MISSING_SOURCE_REFERENCE")

        if (
            self.derived_fields
            and not self.has_source_reference()
        ):
            issues.append(
                "DERIVED_DERIVATIVE_DATA_WITHOUT_SOURCE_REFERENCE"
            )

        return tuple(issues)

    def is_structurally_valid(self) -> bool:
        """Return True when no structural issues exist."""

        return not self.issue_flags()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize derivative information into a mapping."""

        data = asdict(self)

        data["observed_fields"] = list(self.observed_fields)
        data["derived_fields"] = list(self.derived_fields)
        data["metadata"] = dict(self.metadata)

        return data

    @staticmethod
    def schema_info() -> dict[str, str]:
        """Return schema identity and version."""

        return {
            "schema": MARKET_DERIVATIVE_SCHEMA,
            "version": MARKET_DERIVATIVE_SCHEMA_VERSION,
        }


def market_derivative_health() -> dict[str, Any]:
    """Return structural health information for the derivative schema."""

    return {
        "schema": MARKET_DERIVATIVE_SCHEMA,
        "version": MARKET_DERIVATIVE_SCHEMA_VERSION,
        "status": "ready",
        "immutable": True,
        "derivative_identity_supported": True,
        "market_identity_supported": True,
        "underlying_identity_supported": True,
        "contract_identity_supported": True,
        "expiry_supported": True,
        "option_identity_supported": True,
        "strike_supported": True,
        "price_supported": True,
        "order_book_supported": True,
        "volume_supported": True,
        "open_interest_supported": True,
        "greeks_supported": True,
        "implied_volatility_supported": True,
        "premium_supported": True,
        "intrinsic_time_value_supported": True,
        "price_change_supported": True,
        "open_interest_change_supported": True,
        "observed_derived_separation": True,
        "provenance_supported": True,
        "source_reference_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "order_generation": False,
        "prediction_logic": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DERIVATIVE_SCHEMA_VERSION",
    "MARKET_DERIVATIVE_SCHEMA",
    "MarketDerivative",
    "market_derivative_health",
]