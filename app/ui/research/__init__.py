```python
"""
ROBOMLM_PLUS Research UI Package
=================================

Controlled Research / Validation / Governance UI layer.

Architectural boundary
----------------------
UI may:
    - display research state
    - create research metadata
    - display experiment / validation / stress-test evidence
    - display admin review state
    - display candidate/version information
    - expose audit history
    - request controlled lifecycle actions

UI must NOT:
    - modify production intelligence formulas directly
    - directly control intelligence engines
    - directly place broker/exchange orders
    - bypass D13 decision authority
    - deploy production intelligence by itself
    - invent research formulas or validation thresholds

Canonical lifecycle:

RESEARCH
    ↓
EXPERIMENT
    ↓
VALIDATION
    ↓
STRESS_TEST
    ↓
ADMIN_REVIEW
    ↓
CANDIDATE
    ↓
VERSION
    ↓
APPROVED
    ↓
CONTROLLED DEPLOYMENT

Deployment / rollback remain outside the UI's direct mutation boundary.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Package metadata
# ---------------------------------------------------------------------------

PACKAGE_NAME = "robomlm_plus.app.ui.research"
PACKAGE_VERSION = "1.0.0"

# These values are architectural boundaries, not trading logic.
DECISION_AUTHORITY = "D13"
PRODUCTION_MUTATION_ALLOWED = False
DIRECT_ENGINE_CONTROL_ALLOWED = False
DIRECT_BROKER_CONTROL_ALLOWED = False


# ---------------------------------------------------------------------------
# Optional public imports
# ---------------------------------------------------------------------------
# Keep imports defensive so the package itself can load even while individual
# research modules are being developed/refactored.

try:
    from .research_page import (
        ResearchPageController,
        ResearchRecord,
        ResearchStatus,
        render_research_page,
    )
except ImportError:
    ResearchPageController = None
    ResearchRecord = None
    ResearchStatus = None
    render_research_page = None


# ---------------------------------------------------------------------------
# Public package contract
# ---------------------------------------------------------------------------

__all__ = [
    "PACKAGE_NAME",
    "PACKAGE_VERSION",
    "DECISION_AUTHORITY",
    "PRODUCTION_MUTATION_ALLOWED",
    "DIRECT_ENGINE_CONTROL_ALLOWED",
    "DIRECT_BROKER_CONTROL_ALLOWED",
    "ResearchPageController",
    "ResearchRecord",
    "ResearchStatus",
    "render_research_page",
]
```

**Important:** is `__init__.py` mein koi formula, trading signal, broker execution, ya production intelligence mutation nahi hai. Ye sirf **Research UI package boundary** establish karta hai.

Agar existing `research_page.py` mein names abhi available nahi hain, defensive `try/except` ki wajah se package import unnecessarily crash nahi karega.
