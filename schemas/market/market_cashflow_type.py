"""
ROBOMLM PLUS
V6 Market Cashflow Type Schema

Purpose:
    Structural vocabulary for classifying account cashflow events.

Design rules:
    - Immutable definitions.
    - Currency agnostic.
    - Supports INR, USD, USDT and other currencies/assets.
    - Classification only; no financial decision logic.
    - No execution authorization.
    - No risk decisions.
    - No V7+ dependency.
"""


from __future__ import annotations

from dataclasses import asdict, dataclass
from types import MappingProxyType
from typing import Any, ClassVar, Mapping


MARKET_CASHFLOW_TYPE_SCHEMA_VERSION = "1.0.0"
MARKET_CASHFLOW_TYPE_SCHEMA = "V6_MARKET_CASHFLOW_TYPE"


@dataclass(frozen=True)
class CashflowTypeDefinition:
    """
    Immutable definition of a cashflow classification.
    """

    code: str
    name: str
    category: str
    direction: str
    balance_effect: str
    description: str
    reversible: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MarketCashflowType:
    """
    Controlled vocabulary for MarketCashflow.cashflow_type.

    The vocabulary is intentionally structural. It does not decide
    whether a transaction should occur or whether it is permitted.
    """

    DEPOSIT: ClassVar[str] = "DEPOSIT"
    WITHDRAWAL: ClassVar[str] = "WITHDRAWAL"

    TRANSFER_IN: ClassVar[str] = "TRANSFER_IN"
    TRANSFER_OUT: ClassVar[str] = "TRANSFER_OUT"

    FEE: ClassVar[str] = "FEE"
    FUNDING: ClassVar[str] = "FUNDING"

    REALIZED_PNL: ClassVar[str] = "REALIZED_PNL"
    UNREALIZED_PNL: ClassVar[str] = "UNREALIZED_PNL"

    INTEREST: ClassVar[str] = "INTEREST"
    DIVIDEND: ClassVar[str] = "DIVIDEND"

    REBATE: ClassVar[str] = "REBATE"
    COMMISSION: ClassVar[str] = "COMMISSION"

    TAX: ClassVar[str] = "TAX"
    ADJUSTMENT: ClassVar[str] = "ADJUSTMENT"

    CONVERSION_IN: ClassVar[str] = "CONVERSION_IN"
    CONVERSION_OUT: ClassVar[str] = "CONVERSION_OUT"

    OTHER_INFLOW: ClassVar[str] = "OTHER_INFLOW"
    OTHER_OUTFLOW: ClassVar[str] = "OTHER_OUTFLOW"

    UNKNOWN: ClassVar[str] = "UNKNOWN"

    _DEFINITIONS: ClassVar[
        Mapping[str, CashflowTypeDefinition]
    ] = MappingProxyType(
        {
            DEPOSIT: CashflowTypeDefinition(
                code=DEPOSIT,
                name="Deposit",
                category="FUNDING",
                direction="IN",
                balance_effect="INCREASE",
                description="External funds added to the account.",
                reversible=True,
            ),
            WITHDRAWAL: CashflowTypeDefinition(
                code=WITHDRAWAL,
                name="Withdrawal",
                category="FUNDING",
                direction="OUT",
                balance_effect="DECREASE",
                description="Funds removed from the account.",
                reversible=True,
            ),
            TRANSFER_IN: CashflowTypeDefinition(
                code=TRANSFER_IN,
                name="Transfer In",
                category="TRANSFER",
                direction="IN",
                balance_effect="INCREASE",
                description="Funds transferred into the account.",
                reversible=True,
            ),
            TRANSFER_OUT: CashflowTypeDefinition(
                code=TRANSFER_OUT,
                name="Transfer Out",
                category="TRANSFER",
                direction="OUT",
                balance_effect="DECREASE",
                description="Funds transferred out of the account.",
                reversible=True,
            ),
            FEE: CashflowTypeDefinition(
                code=FEE,
                name="Fee",
                category="COST",
                direction="OUT",
                balance_effect="DECREASE",
                description="Account-related fee or service charge.",
                reversible=False,
            ),
            FUNDING: CashflowTypeDefinition(
                code=FUNDING,
                name="Funding",
                category="FUNDING_COST",
                direction="SIGNED",
                balance_effect="VARIABLE",
                description="Funding payment or funding receipt.",
                reversible=False,
            ),
            REALIZED_PNL: CashflowTypeDefinition(
                code=REALIZED_PNL,
                name="Realized PnL",
                category="PNL",
                direction="SIGNED",
                balance_effect="VARIABLE",
                description="Realized profit or loss contribution.",
                reversible=False,
            ),
            UNREALIZED_PNL: CashflowTypeDefinition(
                code=UNREALIZED_PNL,
                name="Unrealized PnL",
                category="PNL",
                direction="SIGNED",
                balance_effect="VARIABLE",
                description="Unrealized profit or loss representation.",
                reversible=False,
            ),
            INTEREST: CashflowTypeDefinition(
                code=INTEREST,
                name="Interest",
                category="INCOME",
                direction="SIGNED",
                balance_effect="VARIABLE",
                description="Interest income or interest charge.",
                reversible=False,
            ),
            DIVIDEND: CashflowTypeDefinition(
                code=DIVIDEND,
                name="Dividend",
                category="INCOME",
                direction="IN",
                balance_effect="INCREASE",
                description="Dividend credited to the account.",
                reversible=False,
            ),
            REBATE: CashflowTypeDefinition(
                code=REBATE,
                name="Rebate",
                category="INCOME",
                direction="IN",
                balance_effect="INCREASE",
                description="Rebate or credited trading benefit.",
                reversible=False,
            ),
            COMMISSION: CashflowTypeDefinition(
                code=COMMISSION,
                name="Commission",
                category="COST",
                direction="OUT",
                balance_effect="DECREASE",
                description="Trading or transaction commission.",
                reversible=False,
            ),
            TAX: CashflowTypeDefinition(
                code=TAX,
                name="Tax",
                category="COST",
                direction="OUT",
                balance_effect="DECREASE",
                description="Tax-related account movement.",
                reversible=False,
            ),
            ADJUSTMENT: CashflowTypeDefinition(
                code=ADJUSTMENT,
                name="Adjustment",
                category="ADJUSTMENT",
                direction="SIGNED",
                balance_effect="VARIABLE",
                description="External or system accounting adjustment.",
                reversible=True,
            ),
            CONVERSION_IN: CashflowTypeDefinition(
                code=CONVERSION_IN,
                name="Conversion In",
                category="CONVERSION",
                direction="IN",
                balance_effect="INCREASE",
                description=(
                    "Currency or asset conversion received into "
                    "the target currency."
                ),
                reversible=True,
            ),
            CONVERSION_OUT: CashflowTypeDefinition(
                code=CONVERSION_OUT,
                name="Conversion Out",
                category="CONVERSION",
                direction="OUT",
                balance_effect="DECREASE",
                description=(
                    "Currency or asset conversion sent from "
                    "the source currency."
                ),
                reversible=True,
            ),
            OTHER_INFLOW: CashflowTypeDefinition(
                code=OTHER_INFLOW,
                name="Other Inflow",
                category="OTHER",
                direction="IN",
                balance_effect="INCREASE",
                description=(
                    "Other account inflow not covered by "
                    "a specific type."
                ),
                reversible=False,
            ),
            OTHER_OUTFLOW: CashflowTypeDefinition(
                code=OTHER_OUTFLOW,
                name="Other Outflow",
                category="OTHER",
                direction="OUT",
                balance_effect="DECREASE",
                description=(
                    "Other account outflow not covered by "
                    "a specific type."
                ),
                reversible=False,
            ),
            UNKNOWN: CashflowTypeDefinition(
                code=UNKNOWN,
                name="Unknown",
                category="UNKNOWN",
                direction="UNKNOWN",
                balance_effect="UNKNOWN",
                description="Cashflow classification is not yet known.",
                reversible=False,
            ),
        }
    )

    # ------------------------------------------------------------------
    # Vocabulary access
    # ------------------------------------------------------------------

    @classmethod
    def all_types(cls) -> tuple[str, ...]:
        return tuple(cls._DEFINITIONS.keys())

    @classmethod
    def definitions(cls) -> tuple[CashflowTypeDefinition, ...]:
        return tuple(cls._DEFINITIONS.values())

    @classmethod
    def get_definition(
        cls,
        cashflow_type: str,
    ) -> CashflowTypeDefinition | None:
        if not cashflow_type:
            return None

        return cls._DEFINITIONS.get(
            str(cashflow_type).strip().upper()
        )

    @classmethod
    def normalize(cls, cashflow_type: str | None) -> str:
        """
        Normalize a cashflow type to the controlled vocabulary.

        Unknown values are mapped to UNKNOWN rather than silently
        inventing a new classification.
        """

        if not cashflow_type:
            return cls.UNKNOWN

        normalized = str(cashflow_type).strip().upper()

        return (
            normalized
            if normalized in cls._DEFINITIONS
            else cls.UNKNOWN
        )

    @classmethod
    def is_valid(cls, cashflow_type: str | None) -> bool:
        if not cashflow_type:
            return False

        return str(cashflow_type).strip().upper() in cls._DEFINITIONS

    # ------------------------------------------------------------------
    # Direction helpers
    # ------------------------------------------------------------------

    @classmethod
    def direction(
        cls,
        cashflow_type: str | None,
    ) -> str:
        definition = cls.get_definition(
            cls.normalize(cashflow_type)
        )

        if definition is None:
            return "UNKNOWN"

        return definition.direction

    @classmethod
    def is_inflow(cls, cashflow_type: str | None) -> bool:
        return cls.direction(cashflow_type) == "IN"

    @classmethod
    def is_outflow(cls, cashflow_type: str | None) -> bool:
        return cls.direction(cashflow_type) == "OUT"

    @classmethod
    def is_signed(cls, cashflow_type: str | None) -> bool:
        return cls.direction(cashflow_type) == "SIGNED"

    # ------------------------------------------------------------------
    # Category helpers
    # ------------------------------------------------------------------

    @classmethod
    def category(
        cls,
        cashflow_type: str | None,
    ) -> str:
        definition = cls.get_definition(
            cls.normalize(cashflow_type)
        )

        if definition is None:
            return "UNKNOWN"

        return definition.category

    @classmethod
    def is_funding(cls, cashflow_type: str | None) -> bool:
        return cls.category(cashflow_type) == "FUNDING"

    @classmethod
    def is_transfer(cls, cashflow_type: str | None) -> bool:
        return cls.category(cashflow_type) == "TRANSFER"

    @classmethod
    def is_cost(cls, cashflow_type: str | None) -> bool:
        return cls.category(cashflow_type) == "COST"

    @classmethod
    def is_pnl(cls, cashflow_type: str | None) -> bool:
        return cls.category(cashflow_type) == "PNL"

    @classmethod
    def is_conversion(cls, cashflow_type: str | None) -> bool:
        return cls.category(cashflow_type) == "CONVERSION"

    # ------------------------------------------------------------------
    # Balance effect
    # ------------------------------------------------------------------

    @classmethod
    def balance_effect(
        cls,
        cashflow_type: str | None,
    ) -> str:
        definition = cls.get_definition(
            cls.normalize(cashflow_type)
        )

        if definition is None:
            return "UNKNOWN"

        return definition.balance_effect

    # ------------------------------------------------------------------
    # Structural validation
    # ------------------------------------------------------------------

    @classmethod
    def issue_flags(
        cls,
        cashflow_type: str | None,
    ) -> list[str]:
        issues: list[str] = []

        if not cashflow_type:
            issues.append("MISSING_CASHFLOW_TYPE")
            return issues

        normalized = str(cashflow_type).strip().upper()

        if normalized not in cls._DEFINITIONS:
            issues.append("UNKNOWN_CASHFLOW_TYPE")

        return issues

    @classmethod
    def is_structurally_valid(
        cls,
        cashflow_type: str | None,
    ) -> bool:
        return len(cls.issue_flags(cashflow_type)) == 0

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @classmethod
    def to_dict(
        cls,
        cashflow_type: str | None,
    ) -> dict[str, Any]:
        normalized = cls.normalize(cashflow_type)
        definition = cls.get_definition(normalized)

        if definition is None:
            return {
                "code": normalized,
                "schema": MARKET_CASHFLOW_TYPE_SCHEMA,
                "version": MARKET_CASHFLOW_TYPE_SCHEMA_VERSION,
            }

        result = definition.to_dict()
        result["schema"] = MARKET_CASHFLOW_TYPE_SCHEMA
        result["version"] = MARKET_CASHFLOW_TYPE_SCHEMA_VERSION

        return result


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

def market_cashflow_type_health() -> dict[str, Any]:
    return {
        "schema": MARKET_CASHFLOW_TYPE_SCHEMA,
        "version": MARKET_CASHFLOW_TYPE_SCHEMA_VERSION,
        "status": "ready",
        "type_count": len(MarketCashflowType.all_types()),
        "currency_agnostic": True,
        "supports_inr": True,
        "supports_usd": True,
        "supports_usdt": True,
        "direction_classification": True,
        "category_classification": True,
        "normalization_supported": True,
        "decision_logic": False,
        "execution_authorization": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_CASHFLOW_TYPE_SCHEMA_VERSION",
    "MARKET_CASHFLOW_TYPE_SCHEMA",
    "CashflowTypeDefinition",
    "MarketCashflowType",
    "market_cashflow_type_health",
]
