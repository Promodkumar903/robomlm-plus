```python
"""
ROBOMLM_PLUS — Buyer Workspace
Decision View

D13 is the final Decision Authority.

This module displays the decision produced by D13.

It must NOT:
- create a decision
- modify a decision
- recalculate scores
- select a trade
- override D13
- authorize execution
- bypass Risk
- bypass CAS
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


VIEW_VERSION = "1.0.0"
DECISION_AUTHORITY = "D13"


@dataclass
class DecisionViewModel:
    """Normalized D13 decision presentation model."""

    available: bool = False
    status: str = "NOT_AVAILABLE"

    decision: Any = None
    action: Any = None
    direction: Any = None

    scenario: Any = None
    rationale: Any = None
    evidence: Any = None
    confidence: Any = None

    decision_authority: str = DECISION_AUTHORITY

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_payload(
        cls,
        payload: Any,
    ) -> "DecisionViewModel":

        if payload is None:
            return cls()

        if isinstance(payload, cls):
            return payload

        if not isinstance(payload, Mapping):
            return cls(
                available=True,
                status="AVAILABLE",
                decision=payload,
            )

        authority = str(
            payload.get(
                "decision_authority",
                payload.get(
                    "authority",
                    DECISION_AUTHORITY,
                ),
            )
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
            decision=payload.get(
                "decision",
                payload.get(
                    "verdict"
                ),
            ),
            action=payload.get(
                "action"
            ),
            direction=payload.get(
                "direction"
            ),
            scenario=payload.get(
                "scenario"
            ),
            rationale=payload.get(
                "rationale"
            ),
            evidence=payload.get(
                "evidence"
            ),
            confidence=payload.get(
                "confidence"
            ),
            decision_authority=authority,
            metadata=dict(payload),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "decision": self.decision,
            "action": self.action,
            "direction": self.direction,
            "scenario": self.scenario,
            "rationale": self.rationale,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "decision_authority": self.decision_authority,
            "metadata": dict(self.metadata),
        }


def render_decision_view(
    st: Any,
    payload: Any,
) -> DecisionViewModel:
    """
    Display the D13-produced decision.

    The UI cannot modify the decision.
    """

    model = DecisionViewModel.from_payload(
        payload
    )

    st.markdown("## Decision")

    st.caption(
        f"Decision Authority: {model.decision_authority}"
    )

    if not model.available:
        st.info(
            "Decision is not available yet."
        )
        return model

    if model.decision_authority != DECISION_AUTHORITY:
        st.warning(
            "Decision payload does not identify D13 as "
            "the expected decision authority."
        )

    status = model.status.upper()

    if status == "ERROR":
        st.error(
            "Decision processing returned an error."
        )

    elif status in {
        "PROCESSING",
        "PENDING",
    }:
        st.info(
            "Decision processing is in progress."
        )

    else:
        st.success(
            "D13 decision is available."
        )

    if model.decision is not None:
        st.metric(
            "Decision",
            str(model.decision),
        )

    if model.action is not None:
        st.write(
            f"**Action:** {model.action}"
        )

    if model.direction is not None:
        st.write(
            f"**Direction:** {model.direction}"
        )

    if model.scenario is not None:
        if isinstance(
            model.scenario,
            Mapping,
        ):
            with st.expander(
                "Scenario",
                expanded=False,
            ):
                st.json(
                    dict(model.scenario)
                )
        else:
            st.write(
                f"**Scenario:** {model.scenario}"
            )

    if model.rationale is not None:
        if isinstance(
            model.rationale,
            Mapping,
        ):
            with st.expander(
                "Decision Rationale",
                expanded=False,
            ):
                st.json(
                    dict(model.rationale)
                )
        else:
            st.write(
                f"**Rationale:** {model.rationale}"
            )

    if model.evidence is not None:
        with st.expander(
            "Decision Evidence",
            expanded=False,
        ):
            if isinstance(
                model.evidence,
                Mapping,
            ):
                st.json(
                    dict(model.evidence)
                )
            else:
                st.write(model.evidence)

    if model.confidence is not None:
        st.write(
            f"**Decision Confidence:** "
            f"{model.confidence}"
        )

    st.warning(
        "Buyer displays D13 output only. "
        "Decision cannot be overridden from this view."
    )

    return model


__all__ = [
    "VIEW_VERSION",
    "DECISION_AUTHORITY",
    "DecisionViewModel",
    "render_decision_view",
]
```
