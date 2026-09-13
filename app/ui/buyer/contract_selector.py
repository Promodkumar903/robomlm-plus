```python
"""
ROBOMLM_PLUS — Buyer Workspace
Contract Selector

Purpose:
    Select the exact tradable contract/configuration for the
    selected market + instrument.

Architecture:
    Market
        ↓
    Instrument
        ↓
    Contract
        ↓
    Strategy

IMPORTANT:
- Contract selection is not contract intelligence.
- No pricing calculation.
- No Greeks calculation.
- No OI calculation.
- No liquidity calculation.
- No D13 decision.
- No risk authorization.
- No CAS override.
- No broker execution.
- Exact contract universe must come from the canonical registry/API.
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


class ContractOptionProvider:
    """
    Pluggable contract provider.

    Future implementation can connect to:
        - contract registry
        - instrument service
        - market-data/API layer
        - canonical application service

    This class does not derive or invent contracts.
    """

    def __init__(
        self,
        loader: Optional[
            Callable[
                [Optional[str], Optional[str]],
                Iterable[Any],
            ]
        ] = None,
    ) -> None:
        self.loader = loader

    def get_options(
        self,
        market: Optional[str],
        instrument: Optional[str],
    ) -> List[SelectorOption]:

        if self.loader is None:
            return []

        try:
            raw_options = self.loader(
                market,
                instrument,
            )
        except Exception:
            return []

        return normalize_market_options(raw_options)


@dataclass
class ContractSelector:
    """Contract selector model."""

    options: Optional[Iterable[Any]] = None
    provider: Optional[ContractOptionProvider] = None

    def __post_init__(self) -> None:
        self._static_options = normalize_market_options(
            self.options
        )

        if self.provider is None:
            self.provider = ContractOptionProvider()

    def get_options(
        self,
        market: Optional[str],
        instrument: Optional[str],
    ) -> List[SelectorOption]:

        if self._static_options:
            return list(self._static_options)

        if self.provider is None:
            return []

        return self.provider.get_options(
            market,
            instrument,
        )

    def validate(
        self,
        value: Optional[str],
        market: Optional[str],
        instrument: Optional[str],
    ) -> SelectionResult:

        value = (value or "").strip()

        if not market:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="Select a market before selecting a contract.",
            )

        if not instrument:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason=(
                    "Select an instrument before selecting a contract."
                ),
            )

        if not value:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="No contract selected.",
            )

        options = self.get_options(
            market,
            instrument,
        )

        if not options:
            return SelectionResult(
                selected_value=value,
                valid=True,
                reason=(
                    "Selection accepted; canonical contract "
                    "validation is pending."
                ),
                metadata={
                    "provider_validation_pending": True,
                    "market": market,
                    "instrument": instrument,
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
                    "Selected contract is not available "
                    "for the selected market/instrument."
                ),
                metadata={
                    "market": market,
                    "instrument": instrument,
                },
            )

        return SelectionResult(
            selected_value=value,
            valid=True,
            metadata={
                "market": market,
                "instrument": instrument,
            },
        )


def render_contract_selector(
    st: Any,
    controller: Any,
    options: Optional[Iterable[Any]] = None,
    provider: Optional[ContractOptionProvider] = None,
    key: str = "buyer_contract_selector",
) -> SelectionResult:
    """Render contract selector for selected market/instrument."""

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

    st.markdown("### Contract")

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

    selector = ContractSelector(
        options=options,
        provider=provider,
    )

    available = [
        option
        for option in selector.get_options(
            market,
            instrument,
        )
        if option.enabled
    ]

    if not available:
        st.info(
            "No contract catalogue is currently supplied "
            "for the selected market/instrument."
        )

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Contract catalogue unavailable.",
            metadata={
                "market": market,
                "instrument": instrument,
            },
        )

    labels = [option.label for option in available]

    current = getattr(
        state,
        "selected_contract",
        None,
    )

    default_index = 0

    if current:
        for index, option in enumerate(available):
            if option.value == current:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select contract",
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
    )

    if result.valid:
        controller.select_contract(
            selected_option.value
        )

        if selected_option.description:
            st.caption(selected_option.description)
    else:
        st.warning(result.reason)

    return result


__all__ = [
    "SELECTOR_VERSION",
    "ContractOptionProvider",
    "ContractSelector",
    "render_contract_selector",
]
```
