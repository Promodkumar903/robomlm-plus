```python
"""
ROBOMLM_PLUS — Buyer Workspace
Instrument Selector

Purpose:
    Select an instrument belonging to the selected market.

Architecture:
    Market
        ↓
    Instrument Selection
        ↓
    Buyer Controller

IMPORTANT:
- Selection only.
- No signal generation.
- No intelligence calculation.
- No D13 decision.
- No risk calculation.
- No CAS authorization.
- No broker/execution access.
- Actual market/instrument compatibility belongs downstream.
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


class InstrumentOptionProvider:
    """
    Pluggable instrument provider.

    Expected future source:
        canonical instrument registry/API/application service.
    """

    def __init__(
        self,
        loader: Optional[Callable[[Optional[str]], Iterable[Any]]] = None,
    ) -> None:
        self.loader = loader

    def get_options(
        self,
        market: Optional[str],
    ) -> List[SelectorOption]:

        if self.loader is None:
            return []

        try:
            raw_options = self.loader(market)
        except Exception:
            return []

        return normalize_market_options(raw_options)


@dataclass
class InstrumentSelector:
    """Instrument selector model."""

    options: Optional[Iterable[Any]] = None
    provider: Optional[InstrumentOptionProvider] = None

    def __post_init__(self) -> None:
        self._static_options = normalize_market_options(
            self.options
        )

        if self.provider is None:
            self.provider = InstrumentOptionProvider()

    def get_options(
        self,
        market: Optional[str],
    ) -> List[SelectorOption]:

        if self._static_options:
            return list(self._static_options)

        if self.provider is None:
            return []

        return self.provider.get_options(market)

    def validate(
        self,
        value: Optional[str],
        market: Optional[str],
    ) -> SelectionResult:

        value = (value or "").strip()

        if not market:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="Select a market before selecting an instrument.",
            )

        if not value:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="No instrument selected.",
            )

        options = self.get_options(market)

        if not options:
            return SelectionResult(
                selected_value=value,
                valid=True,
                reason=(
                    "Selection accepted; canonical instrument "
                    "validation is pending."
                ),
                metadata={
                    "provider_validation_pending": True,
                    "market": market,
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
                    "Selected instrument is not available "
                    "for the current market catalogue."
                ),
                metadata={"market": market},
            )

        return SelectionResult(
            selected_value=value,
            valid=True,
            metadata={"market": market},
        )


def render_instrument_selector(
    st: Any,
    controller: Any,
    options: Optional[Iterable[Any]] = None,
    provider: Optional[InstrumentOptionProvider] = None,
    key: str = "buyer_instrument_selector",
) -> SelectionResult:
    """Render instrument selector for the currently selected market."""

    market = getattr(
        getattr(controller, "state", None),
        "selected_market",
        None,
    )

    st.markdown("### Instrument")

    if not market:
        st.info("Select a market first.")

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Market selection required.",
        )

    selector = InstrumentSelector(
        options=options,
        provider=provider,
    )

    available = [
        option
        for option in selector.get_options(market)
        if option.enabled
    ]

    if not available:
        st.info(
            "No instrument catalogue is currently supplied "
            "for this market."
        )

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Instrument catalogue unavailable.",
            metadata={"market": market},
        )

    labels = [option.label for option in available]

    current = getattr(
        getattr(controller, "state", None),
        "selected_instrument",
        None,
    )

    default_index = 0

    if current:
        for index, option in enumerate(available):
            if option.value == current:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select instrument",
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
    )

    if result.valid:
        controller.select_instrument(
            selected_option.value
        )

        if selected_option.description:
            st.caption(selected_option.description)
    else:
        st.warning(result.reason)

    return result


__all__ = [
    "SELECTOR_VERSION",
    "InstrumentOptionProvider",
    "InstrumentSelector",
    "render_instrument_selector",
]
```
