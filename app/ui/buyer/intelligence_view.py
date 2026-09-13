```python
"""
ROBOMLM_PLUS — Buyer Workspace
Intelligence View

Flow:
    Buyer Request
        ↓
    Intelligence
        ↓
    D13 Decision
        ↓
    Risk
        ↓
    CAS

This module is PRESENTATION ONLY.

It must NOT:
- calculate intelligence
- generate signals
- calculate scores
- calculate entry/exit
- calculate risk
- make decisions
- override D13
- authorize execution
- bypass CAS
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


VIEW_VERSION = "1.0.0"


@dataclass
class IntelligenceViewModel:
    """
    Normalized intelligence payload for Buyer presentation.

    The values are produced upstream.
    """

    available: bool = False
    status: str = "NOT_AVAILABLE"

    summary: str = ""

    market_state: Any = None
    structure: Any = None
    flow: Any = None
    liquidity: Any = None
    volatility: Any = None
    timing: Any = None
    derivatives: Any = None
    participation: Any = None
    relationships: Any = None

    confidence: Any = None
    opportunity: Any = None

    evidence: Any = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_payload(
        cls,
        payload: Any,
    ) -> "IntelligenceViewModel":

        if payload is None:
            return cls()

        if isinstance(payload, cls):
            return payload

        if not isinstance(payload, Mapping):
            return cls(
                available=True,
                status="AVAILABLE",
                summary=str(payload),
            )

        return cls(
            available=bool(
                payload.get(
                    "available",
                    True,
                )
            ),
            status=str(
                payload.get(
                    "status",
                    "AVAILABLE",
                )
            ),
            summary=str(
                payload.get(
                    "summary",
                    payload.get(
                        "message",
                        "",
                    ),
                )
                or ""
            ),
            market_state=payload.get(
                "market_state"
            ),
            structure=payload.get(
                "structure"
            ),
            flow=payload.get(
                "flow"
            ),
            liquidity=payload.get(
                "liquidity"
            ),
            volatility=payload.get(
                "volatility"
            ),
            timing=payload.get(
                "timing"
            ),
            derivatives=payload.get(
                "derivatives"
            ),
            participation=payload.get(
                "participation"
            ),
            relationships=payload.get(
                "relationships"
            ),
            confidence=payload.get(
                "confidence"
            ),
            opportunity=payload.get(
                "opportunity"
            ),
            evidence=payload.get(
                "evidence"
            ),
            metadata=dict(payload),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "summary": self.summary,
            "market_state": self.market_state,
            "structure": self.structure,
            "flow": self.flow,
            "liquidity": self.liquidity,
            "volatility": self.volatility,
            "timing": self.timing,
            "derivatives": self.derivatives,
            "participation": self.participation,
            "relationships": self.relationships,
            "confidence": self.confidence,
            "opportunity": self.opportunity,
            "evidence": self.evidence,
            "metadata": dict(self.metadata),
        }


def _render_value(
    st: Any,
    label: str,
    value: Any,
) -> None:

    if value is None:
        return

    if isinstance(value, Mapping):
        with st.expander(label, expanded=False):
            st.json(dict(value))
        return

    if isinstance(value, (list, tuple)):
        with st.expander(label, expanded=False):
            st.write(list(value))
        return

    st.write(
        f"**{label}:** {value}"
    )


def render_intelligence_view(
    st: Any,
    payload: Any,
) -> IntelligenceViewModel:
    """
    Render upstream intelligence.

    No calculations are performed.
    """

    model = IntelligenceViewModel.from_payload(
        payload
    )

    st.markdown("## Intelligence")

    if not model.available:
        st.info(
            "Intelligence is not available yet. "
            "Apply for Analysis to request downstream analysis."
        )
        return model

    status = model.status.upper()

    if status == "ERROR":
        st.error(
            model.summary
            or "Intelligence processing returned an error."
        )

    elif status in {
        "PROCESSING",
        "PENDING",
    }:
        st.info(
            model.summary
            or "Intelligence processing is in progress."
        )

    else:
        st.success(
            model.summary
            or "Intelligence is available."
        )

    if model.evidence is not None:
        _render_value(
            st,
            "Evidence",
            model.evidence,
        )

    if model.market_state is not None:
        _render_value(
            st,
            "Market State",
            model.market_state,
        )

    if model.structure is not None:
        _render_value(
            st,
            "Structure",
            model.structure,
        )

    if model.flow is not None:
        _render_value(
            st,
            "Flow",
            model.flow,
        )

    if model.liquidity is not None:
        _render_value(
            st,
            "Liquidity",
            model.liquidity,
        )

    if model.volatility is not None:
        _render_value(
            st,
            "Volatility",
            model.volatility,
        )

    if model.timing is not None:
        _render_value(
            st,
            "Timing",
            model.timing,
        )

    if model.derivatives is not None:
        _render_value(
            st,
            "Derivatives",
            model.derivatives,
        )

    if model.participation is not None:
        _render_value(
            st,
            "Participation",
            model.participation,
        )

    if model.relationships is not None:
        _render_value(
            st,
            "Relationships",
            model.relationships,
        )

    if model.confidence is not None:
        _render_value(
            st,
            "Confidence",
            model.confidence,
        )

    if model.opportunity is not None:
        _render_value(
            st,
            "Opportunity",
            model.opportunity,
        )

    st.caption(
        "Presentation only — intelligence is produced upstream."
    )

    return model


__all__ = [
    "VIEW_VERSION",
    "IntelligenceViewModel",
    "render_intelligence_view",
]
```
