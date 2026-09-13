```python
"""
ROBOMLM_PLUS — Buyer Workspace
PLUS View

Purpose
-------
Display the handoff from Buyer/CAS into ROBOMLM PLUS.

Blueprint boundary:
    Buyer
      ↓
    Decision
      ↓
    Risk
      ↓
    CAS
      ↓
    PLUS
      ↓
    Authorized downstream workflow

IMPORTANT
---------
PLUS is NOT the Buyer.

This UI module:
- does not execute orders
- does not call brokers
- does not modify positions
- does not override D13
- does not override Risk
- does not override CAS
- does not manufacture authorization
- does not calculate intelligence

It only displays the downstream PLUS handoff state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


VIEW_VERSION = "1.0.0"


class PLUSStatus:
    """PLUS handoff states."""

    NOT_AVAILABLE = "NOT_AVAILABLE"
    READY = "READY"
    RESTRICTED = "RESTRICTED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCKED = "BLOCKED"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"


@dataclass
class PLUSViewModel:
    """Normalized PLUS presentation model."""

    available: bool = False
    status: str = PLUSStatus.NOT_AVAILABLE

    request_id: Optional[str] = None

    decision: Any = None
    risk: Any = None
    cas: Any = None

    authorized_action: Any = None
    restrictions: Any = None

    monitoring: Any = None
    protection: Any = None
    reconciliation: Any = None

    message: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_payload(
        cls,
        payload: Any,
    ) -> "PLUSViewModel":

        if payload is None:
            return cls()

        if isinstance(payload, cls):
            return payload

        if not isinstance(payload, Mapping):
            return cls(
                available=False,
                status=PLUSStatus.ERROR,
                message=(
                    "Unsupported PLUS payload format."
                ),
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
                    PLUSStatus.NOT_AVAILABLE,
                )
            ).upper().strip(),
            request_id=(
                str(payload["request_id"])
                if payload.get("request_id") is not None
                else None
            ),
            decision=payload.get(
                "decision"
            ),
            risk=payload.get(
                "risk"
            ),
            cas=payload.get(
                "cas"
            ),
            authorized_action=payload.get(
                "authorized_action"
            ),
            restrictions=payload.get(
                "restrictions"
            ),
            monitoring=payload.get(
                "monitoring"
            ),
            protection=payload.get(
                "protection"
            ),
            reconciliation=payload.get(
                "reconciliation"
            ),
            message=str(
                payload.get(
                    "message",
                    payload.get(
                        "reason",
                        "",
                    ),
                )
                or ""
            ),
            metadata=dict(payload),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "request_id": self.request_id,
            "decision": self.decision,
            "risk": self.risk,
            "cas": self.cas,
            "authorized_action": self.authorized_action,
            "restrictions": self.restrictions,
            "monitoring": self.monitoring,
            "protection": self.protection,
            "reconciliation": self.reconciliation,
            "message": self.message,
            "metadata": dict(self.metadata),
        }


def _render_value(
    st: Any,
    title: str,
    value: Any,
) -> None:

    if value is None:
        return

    if isinstance(value, Mapping):
        with st.expander(
            title,
            expanded=False,
        ):
            st.json(dict(value))
        return

    if isinstance(value, (list, tuple)):
        with st.expander(
            title,
            expanded=False,
        ):
            st.write(list(value))
        return

    st.write(
        f"**{title}:** {value}"
    )


def render_plus_view(
    st: Any,
    payload: Any,
) -> PLUSViewModel:
    """
    Display PLUS downstream state.
    """

    model = PLUSViewModel.from_payload(
        payload
    )

    st.markdown("## ROBOMLM PLUS")

    if not model.available:
        st.info(
            "PLUS handoff is not available."
        )
        return model

    status = model.status.upper()

    if status == PLUSStatus.READY:
        st.success(
            "PLUS: READY"
        )

    elif status == PLUSStatus.RESTRICTED:
        st.warning(
            "PLUS: RESTRICTED"
        )

    elif status == PLUSStatus.REVIEW_REQUIRED:
        st.warning(
            "PLUS: REVIEW REQUIRED"
        )

    elif status == PLUSStatus.BLOCKED:
        st.error(
            "PLUS: BLOCKED"
        )

    elif status == PLUSStatus.PROCESSING:
        st.info(
            "PLUS processing is in progress."
        )

    elif status == PLUSStatus.ERROR:
        st.error(
            "PLUS returned an error."
        )

    else:
        st.info(
            f"PLUS status: {status}"
        )

    if model.request_id:
        st.caption(
            f"Request ID: {model.request_id}"
        )

    if model.message:
        st.write(
            f"**Status Message:** {model.message}"
        )

    _render_value(
        st,
        "D13 Decision",
        model.decision,
    )

    _render_value(
        st,
        "Risk",
        model.risk,
    )

    _render_value(
        st,
        "CAS",
        model.cas,
    )

    _render_value(
        st,
        "Authorized Action",
        model.authorized_action,
    )

    _render_value(
        st,
        "Restrictions",
        model.restrictions,
    )

    _render_value(
        st,
        "Monitoring",
        model.monitoring,
    )

    _render_value(
        st,
        "Protection",
        model.protection,
    )

    _render_value(
        st,
        "Reconciliation",
        model.reconciliation,
    )

    if status == PLUSStatus.BLOCKED:
        st.error(
            "PLUS handoff is blocked. "
            "No downstream execution may be initiated from Buyer."
        )

    elif status == PLUSStatus.REVIEW_REQUIRED:
        st.warning(
            "PLUS requires review. "
            "Buyer cannot authorize execution."
        )

    elif status == PLUSStatus.RESTRICTED:
        st.warning(
            "PLUS is restricted. "
            "Upstream CAS restrictions must remain enforced."
        )

    elif status == PLUSStatus.READY:
        st.success(
            "PLUS handoff is ready according to the supplied upstream result."
        )

    st.caption(
        "PLUS is downstream of Buyer/CAS. "
        "This view does not control PLUS execution."
    )

    return model


def build_plus_payload(
    decision: Any = None,
    risk: Any = None,
    cas: Any = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a read-only handoff payload.

    This function does NOT authorize execution.

    The caller must obtain the authoritative CAS result
    from the actual CAS service before any downstream action.
    """

    return {
        "request_id": request_id,
        "decision": decision,
        "risk": risk,
        "cas": cas,
        "available": False,
        "status": PLUSStatus.NOT_AVAILABLE,
        "authorized_action": None,
        "message": (
            "Handoff payload prepared for downstream "
            "application/service processing."
        ),
    }


__all__ = [
    "VIEW_VERSION",
    "PLUSStatus",
    "PLUSViewModel",
    "render_plus_view",
    "build_plus_payload",
]
```
