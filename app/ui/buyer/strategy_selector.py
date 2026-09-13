```python
"""
ROBOMLM_PLUS — Buyer Workspace
Strategy Selector

Purpose
-------
Select the strategy requested by the Buyer.

Architecture
------------
Market
    ↓
Instrument
    ↓
Contract
    ↓
Strategy Selection
    ↓
Apply for Analysis
    ↓
Application / Intelligence Pipeline
    ↓
D13 Decision Authority

IMPORTANT
---------
This module is a selection layer only.

It MUST NOT:
- invent strategies
- calculate strategy signals
- calculate entry/exit levels
- calculate risk
- calculate intelligence
- make D13 decisions
- authorize execution
- bypass CAS
- submit broker orders
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional

try:
    from .market_selector import (
        SelectionResult,
        SelectorOption,
        normalize_market_options,
    )
except ImportError:
    from market_selector import (
        SelectionResult,
        SelectorOption,
        normalize_market_options,
    )


SELECTOR_VERSION = "1.0.0"


class StrategyOptionProvider:
    """
    Pluggable canonical strategy provider.

    Future source may be:
        - Strategy Registry
        - Application Service
        - API Layer
        - Entitlement-aware Strategy Catalogue

    The provider only supplies registered strategy definitions.
    """

    def __init__(
        self,
        loader: Optional[
            Callable[
                [Optional[str], Optional[str], Optional[str]],
                Iterable[Any],
            ]
        ] = None,
    ) -> None:
        self.loader = loader

    def get_options(
        self,
        market: Optional[str],
        instrument: Optional[str],
        contract: Optional[str],
    ) -> List[SelectorOption]:

        if self.loader is None:
            return []

        try:
            raw_options = self.loader(
                market,
                instrument,
                contract,
            )
        except Exception:
            return []

        return normalize_market_options(raw_options)


@dataclass
class StrategySelector:
    """
    Strategy selector model.

    No strategy mathematics is performed here.
    """

    options: Optional[Iterable[Any]] = None
    provider: Optional[StrategyOptionProvider] = None

    def __post_init__(self) -> None:
        self._static_options = normalize_market_options(
            self.options
        )

        if self.provider is None:
            self.provider = StrategyOptionProvider()

    def get_options(
        self,
        market: Optional[str],
        instrument: Optional[str],
        contract: Optional[str],
    ) -> List[SelectorOption]:

        if self._static_options:
            return list(self._static_options)

        if self.provider is None:
            return []

        return self.provider.get_options(
            market,
            instrument,
            contract,
        )

    def validate(
        self,
        value: Optional[str],
        market: Optional[str],
        instrument: Optional[str],
        contract: Optional[str],
    ) -> SelectionResult:

        value = (value or "").strip()

        if not market:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="Select a market before selecting a strategy.",
            )

        if not instrument:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="Select an instrument before selecting a strategy.",
            )

        if not contract:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="Select a contract before selecting a strategy.",
            )

        if not value:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="No strategy selected.",
            )

        options = self.get_options(
            market,
            instrument,
            contract,
        )

        # Provider not configured:
        # do not invent a strategy universe.
        if not options:
            return SelectionResult(
                selected_value=value,
                valid=True,
                reason=(
                    "Strategy selection accepted; canonical "
                    "strategy validation is pending."
                ),
                metadata={
                    "provider_validation_pending": True,
                    "market": market,
                    "instrument": instrument,
                    "contract": contract,
                },
            )

        valid_values = {
            option.value
            for option in options
            if option.enabled
        }

        if value not in valid_values:
            return SelectionResult(
                selected_value=value,
                valid=False,
                reason=(
                    "Selected strategy is not available for "
                    "the current market/instrument/contract."
                ),
                metadata={
                    "market": market,
                    "instrument": instrument,
                    "contract": contract,
                },
            )

        return SelectionResult(
            selected_value=value,
            valid=True,
            metadata={
                "market": market,
                "instrument": instrument,
                "contract": contract,
            },
        )


def render_strategy_selector(
    st: Any,
    controller: Any,
    options: Optional[Iterable[Any]] = None,
    provider: Optional[StrategyOptionProvider] = None,
    key: str = "buyer_strategy_selector",
) -> SelectionResult:
    """
    Render the strategy selector.

    Synchronizes only the selected strategy with Buyer controller.
    """

    state = getattr(controller, "state", None)

    market = getattr(
        state,
        "selected_market",
        None,
    )

    instrument = getattr(
        state,
        "selected_instrument",
        None,
    )

    contract = getattr(
        state,
        "selected_contract",
        None,
    )

    st.markdown("### Strategy")

    if not market:
        st.info("Select a market first.")

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Market selection required.",
        )

    if not instrument:
        st.info("Select an instrument first.")

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Instrument selection required.",
        )

    if not contract:
        st.info("Select a contract first.")

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Contract selection required.",
        )

    selector = StrategySelector(
        options=options,
        provider=provider,
    )

    available = [
        option
        for option in selector.get_options(
            market,
            instrument,
            contract,
        )
        if option.enabled
    ]

    if not available:
        st.info(
            "No strategy catalogue is currently supplied "
            "for the selected market/instrument/contract."
        )

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Strategy catalogue unavailable.",
            metadata={
                "market": market,
                "instrument": instrument,
                "contract": contract,
            },
        )

    labels = [
        option.label
        for option in available
    ]

    current = getattr(
        state,
        "selected_strategy",
        None,
    )

    default_index = 0

    if current:
        for index, option in enumerate(available):
            if option.value == current:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select strategy",
        labels,
        index=default_index,
        key=key,
    )

    selected_option = next(
        option
        for option in available
        if option.label == selected_label
    )

    result = selector.validate(
        selected_option.value,
        market,
        instrument,
        contract,
    )

    if result.valid:
        controller.select_strategy(
            selected_option.value
        )

        if selected_option.description:
            st.caption(
                selected_option.description
            )
    else:
        st.warning(result.reason)

    return result


__all__ = [
    "SELECTOR_VERSION",
    "StrategyOptionProvider",
    "StrategySelector",
    "render_strategy_selector",
]
```
