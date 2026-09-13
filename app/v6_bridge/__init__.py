"""
ROBOMLM PLUS - V6 Bridge Package

Compatibility and integration boundary for the completed V6 engine.

The V6 bridge is intentionally isolated from the V7+ intelligence layers.
It provides controlled access to legacy/current V6 components without
allowing legacy implementation details to leak across the application.
"""

V6_BRIDGE_PACKAGE = "app.v6_bridge"

__all__ = [
    "V6_BRIDGE_PACKAGE",
]