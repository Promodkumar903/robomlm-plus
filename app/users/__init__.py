"""
ROBOMLM_PLUS Users Package
===========================

Exports the public User Service and Profile Service APIs.

Architecture:
    User Service
        ↓
    Profile Service
        ↓
    Application / API / UI

This package does not own:
    - Authentication
    - Credentials
    - Billing
    - Subscription / Entitlement
    - Market Intelligence
    - D13 Decision Authority
    - Risk Authority
    - CAS Authority
    - Execution / Orders / Positions
"""

from .user_service import *
from .profile_service import *

from .user_service import __all__ as _user_all
from .profile_service import __all__ as _profile_all


__all__ = [
    *_user_all,
    *_profile_all,
]


del _user_all
del _profile_all