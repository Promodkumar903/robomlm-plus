```python
"""
ROBOMLM_PLUS — Buyer Workspace
Market Selector

Architecture:
    Buyer UI
        ↓
    Market Selection
        ↓
    Buyer Workspace Controller
        ↓
    Application / API Layer

IMPORTANT:
- This module performs selection only.
- It does NOT calculate intelligence.
- It does NOT calculate decision/risk.
- It does NOT perform market compatibility decisions.
- It does NOT access broker/exchange engines directly.
- It does NOT privilege any specific market.
- Empty provider data is represented as an empty state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional


SELECTOR_VERSION = "1.0.0"


@dataclass(frozen=True)
class SelectorOption:
    """Generic UI selector option."""

    value: str
    label: str
    description: str = ""
    enabled: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "label": self.label,
            "description": self.description,
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class SelectionResult:
    """Normalized selector result."""

    selected_value: Optional[str]
    valid: bool
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_value": self.selected_value,
            "valid": self.valid,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


class MarketOptionProvider:
    """
    Pluggable market option provider.

    The provider may later be connected to:
        - canonical market registry
        - application service
        - API layer
        - entitlement-aware market catalogue

    This class intentionally contains no market intelligence logic.
    """

    def __init__(
        self,
        loader: Optional[Callable[[], Iterable[Any]]] = None,
    ) -> None:
        self.loader = loader

    def get_options(self) -> List[SelectorOption]:
        if self.loader is None:
            return []

        try:
            raw_options = self.loader()
        except Exception:
            return []

        return normalize_market_options(raw_options)


def normalize_market_options(
    options: Optional[Iterable[Any]],
) -> List[SelectorOption]:
    """Normalize provider output into SelectorOption objects."""

    if not options:
        return []

    normalized: List[SelectorOption] = []

    for item in options:
        if isinstance(item, SelectorOption):
            normalized.append(item)
            continue

        if isinstance(item, Mapping):
            value = str(
                item.get("value")
                or item.get("id")
                or item.get("code")
                or item.get("name")
                or ""
            ).strip()

            if not value:
                continue

            label = str(
                item.get("label")
                or item.get("name")
                or item.get("display_name")
                or value
            ).strip()

            normalized.append(
                SelectorOption(
                    value=value,
                    label=label,
                    description=str(
                        item.get("description") or ""
                    ).strip(),
                    enabled=bool(item.get("enabled", True)),
                    metadata=dict(item),
                )
            )
            continue

        value = str(item).strip()

        if value:
            normalized.append(
                SelectorOption(
                    value=value,
                    label=value,
                )
            )

    return normalized


class MarketSelector:
    """State-free market selector model."""

    def __init__(
        self,
        options: Optional[Iterable[Any]] = None,
        provider: Optional[MarketOptionProvider] = None,
    ) -> None:
        self._options = normalize_market_options(options)

        if provider is not None:
            self.provider = provider
        else:
            self.provider = MarketOptionProvider()

    def get_options(self) -> List[SelectorOption]:
        if self._options:
            return list(self._options)

        return self.provider.get_options()

    def validate(self, value: Optional[str]) -> SelectionResult:
        value = (value or "").strip()

        if not value:
            return SelectionResult(
                selected_value=None,
                valid=False,
                reason="No market selected.",
            )

        options = self.get_options()

        if not options:
            return SelectionResult(
                selected_value=value,
                valid=True,
                reason="Selection accepted; canonical provider validation is pending.",
                metadata={"provider_validation_pending": True},
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
                reason="Selected market is not available in the current market registry.",
            )

        return SelectionResult(
            selected_value=value,
            valid=True,
        )


def render_market_selector(
    st: Any,
    controller: Any,
    options: Optional[Iterable[Any]] = None,
    provider: Optional[MarketOptionProvider] = None,
    key: str = "buyer_market_selector",
) -> SelectionResult:
    """
    Render market selector and synchronize selection with Buyer controller.
    """

    selector = MarketSelector(
        options=options,
        provider=provider,
    )

    available = [
        option
        for option in selector.get_options()
        if option.enabled
    ]

    st.markdown("### Market")

    if not available:
        st.info(
            "No market catalogue is currently supplied. "
            "Connect the canonical market registry/API provider."
        )

        return SelectionResult(
            selected_value=None,
            valid=False,
            reason="Market catalogue unavailable.",
        )

    labels = [option.label for option in available]

    current = getattr(
        getattr(controller, "state", None),
        "selected_market",
        None,
    )

    default_index = 0

    if current:
        for index, option in enumerate(available):
            if option.value == current:
                default_index = index
                break

    selected_label = st.selectbox(
        "Select market",
        labels,
        index=default_index,
        key=key,
    )

    selected_option = next(
        option
        for option in available
        if option.label == selected_label
    )

    result = selector.validate(selected_option.value)

    if result.valid:
        controller.select_market(selected_option.value)

        if selected_option.description:
            st.caption(selected_option.description)
    else:
        st.warning(result.reason)

    return result


__all__ = [
    "SELECTOR_VERSION",
    "SelectorOption",
    "SelectionResult",
    "MarketOptionProvider",
    "normalize_market_options",
    "MarketSelector",
    "render_market_selector",
]
```
