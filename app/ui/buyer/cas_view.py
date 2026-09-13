```python
"""
ROBOMLM_PLUS — Buyer Workspace
CAS View

CAS = Control / Authorization / Suitability boundary.

Buyer flow:
    Intelligence
        ↓
    D13 Decision
        ↓
    Risk
        ↓
    CAS
        ↓
    Result / PLUS / Authorized Execution

IMPORTANT
---------
This module is PRESENTATION ONLY.

It must NOT:
- calculate risk
- calculate suitability
- calculate exposure
- authorize execution
- override CAS
- convert BLOCK into ALLOW
- convert REVIEW_REQUIRED into ALLOW
- bypass D13
- bypass Risk
- submit broker orders

CAS remains an upstream authorization authority/service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional


VIEW_VERSION = "1.0.0"


class CASStatus:
    """Canonical CAS result states."""

    ALLOW = "ALLOW"
    ALLOW_WITH_RESTRICTION = "ALLOW_WITH_RESTRICTION"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    BLOCK = "BLOCK"

    PROCESSING = "PROCESSING"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    ERROR = "ERROR"


@dataclass
class CASViewModel:
    """Normalized CAS presentation model."""

    available: bool = False
    status: str = CASStatus.NOT_AVAILABLE

    reason: str = ""
    restrictions: Any = None
    checks: Any = None
    risk: Any = None
    suitability: Any = None
    exposure: Any = None
    permissions: Any = None
    compliance: Any = None

    authorized_action: Any = None

    audit_id: Optional[str] = None
    timestamp: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    @classmethod
    def from_payload(
        cls,
        payload: Any,
    ) -> "CASViewModel":

        if payload is None:
            return cls()

        if isinstance(payload, cls):
            return payload

        if not isinstance(payload, Mapping):
            return cls(
                available=True,
                status=CASStatus.ERROR,
                reason=(
                    "Unsupported CAS payload format."
                ),
            )

        status = str(
            payload.get(
                "status",
                payload.get(
                    "decision",
                    CASStatus.NOT_AVAILABLE,
                ),
            )
        ).upper().strip()

        return cls(
            available=bool(
                payload.get(
                    "available",
                    True,
                )
            ),
            status=status,
            reason=str(
                payload.get(
                    "reason",
                    payload.get(
                        "message",
                        "",
                    ),
                )
                or ""
            ),
            restrictions=payload.get(
                "restrictions"
            ),
            checks=payload.get(
                "checks"
            ),
            risk=payload.get(
                "risk"
            ),
            suitability=payload.get(
                "suitability"
            ),
            exposure=payload.get(
                "exposure"
            ),
            permissions=payload.get(
                "permissions"
            ),
            compliance=payload.get(
                "compliance"
            ),
            authorized_action=payload.get(
                "authorized_action"
            ),
            audit_id=(
                str(payload["audit_id"])
                if payload.get("audit_id") is not None
                else None
            ),
            timestamp=(
                str(payload["timestamp"])
                if payload.get("timestamp") is not None
                else None
            ),
            metadata=dict(payload),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "reason": self.reason,
            "restrictions": self.restrictions,
            "checks": self.checks,
            "risk": self.risk,
            "suitability": self.suitability,
            "exposure": self.exposure,
            "permissions": self.permissions,
            "compliance": self.compliance,
            "authorized_action": self.authorized_action,
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
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


def render_cas_view(
    st: Any,
    payload: Any,
) -> CASViewModel:
    """
    Display CAS result.

    No CAS decision is created or modified here.
    """

    model = CASViewModel.from_payload(
        payload
    )

    st.markdown("## CAS")

    if not model.available:
        st.info(
            "CAS result is not available yet."
        )
        return model

    status = model.status.upper()

    if status == CASStatus.ALLOW:
        st.success(
            "CAS: ALLOW"
        )

    elif status == CASStatus.ALLOW_WITH_RESTRICTION:
        st.warning(
            "CAS: ALLOW WITH RESTRICTION"
        )

    elif status == CASStatus.REVIEW_REQUIRED:
        st.warning(
            "CAS: REVIEW REQUIRED"
        )

    elif status == CASStatus.BLOCK:
        st.error(
            "CAS: BLOCK"
        )

    elif status == CASStatus.PROCESSING:
        st.info(
            "CAS evaluation is in progress."
        )

    elif status == CASStatus.ERROR:
        st.error(
            "CAS evaluation returned an error."
        )

    else:
        st.info(
            f"CAS status: {status}"
        )

    if model.reason:
        st.write(
            f"**Reason:** {model.reason}"
        )

    _render_value(
        st,
        "Restrictions",
        model.restrictions,
    )

    _render_value(
        st,
        "CAS Checks",
        model.checks,
    )

    _render_value(
        st,
        "Risk Assessment",
        model.risk,
    )

    _render_value(
        st,
        "Suitability",
        model.suitability,
    )

    _render_value(
        st,
        "Exposure",
        model.exposure,
    )

    _render_value(
        st,
        "Permissions",
        model.permissions,
    )

    _render_value(
        st,
        "Compliance",
        model.compliance,
    )

    if model.authorized_action is not None:
        _render_value(
            st,
            "Authorized Action",
            model.authorized_action,
        )

    if model.audit_id:
        st.caption(
            f"CAS Audit ID: {model.audit_id}"
        )

    if model.timestamp:
        st.caption(
            f"CAS Timestamp: {model.timestamp}"
        )

    if status == CASStatus.BLOCK:
        st.error(
            "Execution is blocked by CAS. "
            "Buyer cannot override this result."
        )

    elif status == CASStatus.REVIEW_REQUIRED:
        st.warning(
            "Manual review is required. "
            "Buyer cannot convert this result into authorization."
        )

    elif status == CASStatus.ALLOW_WITH_RESTRICTION:
        st.warning(
            "Authorization contains restrictions. "
            "Restrictions must remain intact downstream."
        )

    elif status == CASStatus.ALLOW:
        st.success(
            "CAS authorization is available. "
            "Any execution remains subject to the authorized downstream path."
        )

    st.caption(
        "CAS is an authorization boundary. "
        "This view only displays the upstream CAS result."
    )

    return model


def is_cas_authorized(
    payload: Any,
) -> bool:
    """
    Read-only helper.

    This does NOT authorize anything.
    It only reports whether the upstream CAS status
    is ALLOW or ALLOW_WITH_RESTRICTION.
    """

    model = CASViewModel.from_payload(
        payload
    )

    return model.status in {
        CASStatus.ALLOW,
        CASStatus.ALLOW_WITH_RESTRICTION,
    }


__all__ = [
    "VIEW_VERSION",
    "CASStatus",
    "CASViewModel",
    "render_cas_view",
    "is_cas_authorized",
]
```
