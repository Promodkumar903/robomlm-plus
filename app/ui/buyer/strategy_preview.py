```python
"""
ROBOMLM_PLUS — Buyer Workspace
Strategy Preview

Purpose
-------
Show the registered strategy definition selected by the Buyer.

The preview is descriptive only.

It does NOT:
- execute the strategy
- generate a trading signal
- calculate entry
- calculate target
- calculate stop loss
- calculate position size
- calculate risk
- make a D13 decision
- authorize execution
- bypass CAS

Architecture
------------
Strategy Registry / Application Layer
                ↓
         Strategy Preview
                ↓
             Buyer
                ↓
       Apply for Analysis
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


PREVIEW_VERSION = "1.0.0"


@dataclass(frozen=True)
class StrategyPreview:
    """
    Normalized descriptive strategy representation.

    Values are supplied by the canonical strategy source.
    """

    strategy_id: str
    name: str
    description: str = ""
    category: str = ""
    objective: str = ""
    applicable_markets: tuple[str, ...] = ()
    applicable_instruments: tuple[str, ...] = ()
    applicable_contracts: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_mapping(
        cls,
        data: Mapping[str, Any],
    ) -> "StrategyPreview":

        strategy_id = str(
            data.get("strategy_id")
            or data.get("id")
            or data.get("value")
            or ""
        ).strip()

        name = str(
            data.get("name")
            or data.get("label")
            or strategy_id
        ).strip()

        return cls(
            strategy_id=strategy_id,
            name=name,
            description=str(
                data.get("description") or ""
            ).strip(),
            category=str(
                data.get("category") or ""
            ).strip(),
            objective=str(
                data.get("objective") or ""
            ).strip(),
            applicable_markets=tuple(
                _normalize_sequence(
                    data.get("applicable_markets")
                )
            ),
            applicable_instruments=tuple(
                _normalize_sequence(
                    data.get("applicable_instruments")
                )
            ),
            applicable_contracts=tuple(
                _normalize_sequence(
                    data.get("applicable_contracts")
                )
            ),
            tags=tuple(
                _normalize_sequence(
                    data.get("tags")
                )
            ),
            metadata=dict(data),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "objective": self.objective,
            "applicable_markets": list(
                self.applicable_markets
            ),
            "applicable_instruments": list(
                self.applicable_instruments
            ),
            "applicable_contracts": list(
                self.applicable_contracts
            ),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


def _normalize_sequence(
    value: Any,
) -> list[str]:

    if value is None:
        return []

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        return [value]

    try:
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]
    except TypeError:
        value = str(value).strip()

        return [value] if value else []


def normalize_strategy_preview(
    source: Any,
) -> Optional[StrategyPreview]:
    """
    Convert a canonical strategy payload into StrategyPreview.

    Returns None when no usable strategy definition exists.
    """

    if source is None:
        return None

    if isinstance(source, StrategyPreview):
        return source

    if isinstance(source, Mapping):
        preview = StrategyPreview.from_mapping(
            source
        )

        if not preview.strategy_id and not preview.name:
            return None

        return preview

    # Avoid interpreting arbitrary engine objects as strategy
    # definitions. Only explicit mappings / StrategyPreview are
    # accepted.
    return None


def render_strategy_preview(
    st: Any,
    preview: Optional[StrategyPreview],
) -> None:
    """
    Render descriptive strategy preview.

    This function has no authority over the strategy itself.
    """

    st.markdown("### Strategy Preview")

    if preview is None:
        st.info(
            "Strategy preview is unavailable until a "
            "canonical strategy definition is supplied."
        )
        return

    if preview.name:
        st.write(f"**Strategy:** {preview.name}")

    if preview.strategy_id:
        st.caption(
            f"Strategy ID: {preview.strategy_id}"
        )

    if preview.category:
        st.write(
            f"**Category:** {preview.category}"
        )

    if preview.objective:
        st.write(
            f"**Objective:** {preview.objective}"
        )

    if preview.description:
        st.write(
            preview.description
        )

    if preview.applicable_markets:
        st.write(
            "**Markets:** "
            + ", ".join(
                preview.applicable_markets
            )
        )

    if preview.applicable_instruments:
        st.write(
            "**Instruments:** "
            + ", ".join(
                preview.applicable_instruments
            )
        )

    if preview.applicable_contracts:
        st.write(
            "**Contracts:** "
            + ", ".join(
                preview.applicable_contracts
            )
        )

    if preview.tags:
        st.write(
            "**Tags:** "
            + ", ".join(preview.tags)
        )

    st.caption(
        "Preview only — strategy analysis and decision "
        "remain downstream of Buyer."
    )


def build_preview_from_option(
    option: Any,
) -> Optional[StrategyPreview]:
    """
    Build a preview from a SelectorOption-like object.

    This keeps preview logic independent from the strategy engine.
    """

    if option is None:
        return None

    if hasattr(option, "metadata"):
        metadata = getattr(
            option,
            "metadata",
            {},
        )

        if isinstance(metadata, Mapping):
            payload = dict(metadata)

            payload.setdefault(
                "strategy_id",
                getattr(
                    option,
                    "value",
                    "",
                ),
            )

            payload.setdefault(
                "name",
                getattr(
                    option,
                    "label",
                    "",
                ),
            )

            payload.setdefault(
                "description",
                getattr(
                    option,
                    "description",
                    "",
                ),
            )

            return normalize_strategy_preview(
                payload
            )

    if isinstance(option, Mapping):
        return normalize_strategy_preview(
            option
        )

    return None


__all__ = [
    "PREVIEW_VERSION",
    "StrategyPreview",
    "normalize_strategy_preview",
    "render_strategy_preview",
    "build_preview_from_option",
]
```
