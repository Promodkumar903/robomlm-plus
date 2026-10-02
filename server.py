"""
ROBOMLM_PLUS
============================================================
FINAL FRONTEND <-> BACKEND WIRING SERVER
============================================================

Purpose
-------
Connect the existing ROBOMLM backend to the existing web frontend.

Existing backend remains owner of:
    Market Data
    Data Quality
    Evidence
    Intelligence
    D1-D16 Decision Cortex
    Metrics / EQE
    Opportunity / Scanner
    Buyer
    Risk
    CAS
    Memory
    Research
    ROBOMLM PLUS
    AUTOROBOMLM
    Execution / Reconciliation
    Account / Authorization

This file is the application/web gateway only.

IMPORTANT
---------
No research engine is copied here.
No D6 formula is recreated here.
No D13 formula is recreated here.
No BUY/SELL decision is invented here.
No CAS gate is bypassed here.

The server collects and exposes outputs from the existing backend.
"""

from __future__ import annotations
import os
import importlib
import inspect
import json
import logging
import pkgutil
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import uuid
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.auth.password_service import PasswordService
from app.auth.token_service import TokenService
from app.database.models.user_model import create_user_record
from app.database.repositories.user_repository import UserRepository
from app.auth.password_service import PasswordHash, PasswordService
# ============================================================================
# EXISTING TERMINAL SERVICE BRIDGE
# ============================================================================
#
# The Terminal domain already exists under app/terminal.
# This bridge deliberately does NOT recreate Terminal intelligence.
# It only discovers the existing service entry point and adapts its result
# for the HTTP layer.
#
# IMPORTANT:
#   - No D13 replacement
#   - No new decision engine
#   - No BUY/SELL generation here
#   - No Risk/CAS bypass
# ============================================================================

from typing import Any


def _load_existing_terminal_service():
    """
    Load the existing Terminal service without importing Terminal internals
    at module-import time.

    The project already contains:
        app/terminal/terminal_service.py

    We keep this lazy because a missing/optional Terminal dependency must not
    prevent the remaining frontend pages from loading.
    """
    try:
        from app.terminal import terminal_service
        return terminal_service
    except Exception as exc:
        return {
            "_load_error": str(exc),
        }


def _call_existing_terminal_service(
    symbol: str,
    timeframe: str = "1m",
    market: str | None = None,
    instrument: str | None = None,
    contract: str | None = None,
) -> dict[str, Any]:
    """
    Call the existing Terminal service using the first compatible public
    service function found.

    This is an adapter only. It does not calculate a new trading decision.
    """
    service = _load_existing_terminal_service()

    if isinstance(service, dict) and "_load_error" in service:
        return {
            "ok": False,
            "status": "SERVICE_UNAVAILABLE",
            "symbol": symbol,
            "timeframe": timeframe,
            "error": service["_load_error"],
        }

    # ------------------------------------------------------------------
    # Prefer explicit public service entry points.
    #
    # We do NOT silently fabricate a result if none exists.
    # ------------------------------------------------------------------
    candidate_names = (
        "get_terminal",
        "get_terminal_state",
        "build_terminal",
        "build_terminal_state",
        "analyze_terminal",
        "terminal_analysis",
        "get_state",
    )

    for name in candidate_names:
        fn = getattr(service, name, None)

        if not callable(fn):
            continue

        # Try the common keyword contract first.
        call_variants = (
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "market": market,
                "instrument": instrument,
                "contract": contract,
            },
            {
                "symbol": symbol,
                "timeframe": timeframe,
            },
            {
                "symbol": symbol,
            },
        )

        for kwargs in call_variants:
            # Remove optional None values so existing service signatures
            # that do not accept them are less likely to reject the call.
            clean_kwargs = {
                key: value
                for key, value in kwargs.items()
                if value is not None
            }

            try:
                result = fn(**clean_kwargs)

                if result is None:
                    continue

                if isinstance(result, dict):
                    return {
                        "ok": True,
                        "status": "READY",
                        "source": "app.terminal.terminal_service",
                        **result,
                    }

                # Preserve non-dict service results instead of inventing
                # a fake Terminal structure.
                return {
                    "ok": True,
                    "status": "READY",
                    "source": "app.terminal.terminal_service",
                    "result": result,
                }

            except TypeError:
                # Signature mismatch; try the next compatible call form.
                continue

            except Exception as exc:
                return {
                    "ok": False,
                    "status": "SERVICE_ERROR",
                    "source": "app.terminal.terminal_service",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": str(exc),
                }

    return {
        "ok": False,
        "status": "NO_PUBLIC_SERVICE_ENTRYPOINT",
        "source": "app.terminal.terminal_service",
        "symbol": symbol,
        "timeframe": timeframe,
        "error": (
            "Existing Terminal service was found, but no supported public "
            "entry point was identified."
        ),
    }


# ============================================================
# ROOT
# ============================================================

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
STATIC = WEB / "static"


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

LOGGER = logging.getLogger("ROBOMLM.FRONTEND_GATEWAY")


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="ROBOMLM_PLUS - Market Intelligence Operating System",
    version="FINAL-FRONTEND-BACKEND-WIRING-1.0",
    description=(
        "Frontend gateway for the existing ROBOMLM_PLUS backend. "
        "The existing intelligence engines remain authoritative."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


if STATIC.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC)),
        name="static",
    )
# ============================================================
# AUTHENTICATION HTTP GATEWAY
# Existing frontend contract:
#
#   POST /api/auth/login
#   POST /api/auth/signup/start
#   POST /api/auth/signup/verify
#   POST /api/auth/forgot/start
#   POST /api/auth/forgot/verify
#   POST /api/auth/forgot/reset
#   GET  /api/auth/status
#
# Existing auth owners remain authoritative:
#   PasswordService -> password hashing/verification
#   TokenService    -> authentication token lifecycle
#   UserRepository  -> user-domain persistence
#
# Authentication secrets are intentionally NOT added to UserRecord.
# ============================================================

_AUTH_TOKEN_SERVICE = TokenService()
_AUTH_USER_REPOSITORY = UserRepository()

# Credential authority remains inside the auth boundary.
# The user-domain UserRecord/UserRepository does not receive passwords.
_AUTH_CREDENTIALS: dict[str, object] = {}

# Temporary OTP state.
# Structure:
#   email -> {
#       "purpose": "signup" | "forgot",
#       "otp_hash": "...",
#       "expires_at": epoch_seconds,
#       "display_name": "...",
#       "password_hash": PasswordHash | ...
#   }
_AUTH_OTP_STATE: dict[str, dict] = {}

_AUTH_OTP_TTL_SECONDS = 600
_AUTH_DEMO_EMAIL = "demo@robomlm.io"
_AUTH_DEMO_PASSWORD = "demo123"


class AuthLoginRequest(BaseModel):
    email: str
    password: str


class AuthSignupStartRequest(BaseModel):
    email: str
    password: str
    display_name: str = ""


class AuthSignupVerifyRequest(BaseModel):
    email: str
    otp: str


class AuthForgotStartRequest(BaseModel):
    email: str


class AuthForgotVerifyRequest(BaseModel):
    email: str
    otp: str


class AuthForgotResetRequest(BaseModel):
    email: str
    new_password: str


def _auth_now() -> datetime:
    return datetime.now(timezone.utc)


def _auth_normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _auth_valid_email(email: str) -> bool:
    email = _auth_normalize_email(email)
    return (
        bool(email)
        and "@" in email
        and "." in email.rsplit("@", 1)[-1]
        and len(email) <= 320
    )


def _auth_valid_password(password: str) -> bool:
    return isinstance(password, str) and len(password) >= 6


def _auth_otp_hash(otp: str) -> str:
    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def _auth_generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _auth_issue_token(user_id: str) -> str:
    """
    Use the existing TokenService rather than introducing a new JWT layer.
    TokenService implementations may expose either a direct token result
    or a result object containing .token.
    """
    result = _AUTH_TOKEN_SERVICE.issue(user_id)

    token = getattr(result, "token", None)

    if token is None and isinstance(result, dict):
        token = result.get("token")

    if not token and isinstance(result, str):
        token = result

    if not token:
        raise RuntimeError("TokenService did not return an authentication token.")

    return str(token)


def _auth_find_user(email: str):
    email = _auth_normalize_email(email)

    try:
        return _AUTH_USER_REPOSITORY.get_by_email(email)
    except Exception:
        return None


def _auth_create_user(email: str, display_name: str):
    """
    Creates the existing domain UserRecord through the existing repository.
    Authentication secrets remain outside the domain record.
    """
    record = create_user_record(
        username=email,
        email=email,
        display_name=display_name or email.split("@", 1)[0],
        user_type="buyer",
        status="active",
        email_verified=True,
        timezone="UTC",
        locale="en-IN",
    )

    _AUTH_USER_REPOSITORY.create(record)

    return record

def _auth_user_id(user) -> Optional[str]:
    if user is None:
        return None

    if isinstance(user, dict):
        return user.get("user_id")

    return getattr(user, "user_id", None)


def _auth_user_email(user, fallback: str = "") -> str:
    if user is None:
        return fallback

    if isinstance(user, dict):
        return user.get("email") or fallback

    return getattr(user, "email", None) or fallback


def _auth_display_name(user) -> str:
    if user is None:
        return ""

    if isinstance(user, dict):
        return user.get("display_name") or ""

    return getattr(user, "display_name", None) or ""


def _auth_token_user(token: str):
    """
    Validate through the existing TokenService.

    Different revisions of TokenService can return either a structured
    result or a user_id-like value, so the adapter normalizes both.
    """
    if not token:
        return None

    try:
        result = _AUTH_TOKEN_SERVICE.validate(token)
    except Exception:
        return None

    if result is None or result is False:
        return None

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        if result.get("valid") is False:
            return None
        return (
            result.get("user_id")
            or result.get("subject")
            or result.get("user")
        )

    if getattr(result, "valid", True) is False:
        return None

    return (
        getattr(result, "user_id", None)
        or getattr(result, "subject", None)
        or getattr(result, "user", None)
    )


def _auth_store_otp(
    *,
    email: str,
    purpose: str,
    otp: str,
    display_name: str = "",
    password_hash=None,
):
    _AUTH_OTP_STATE[email] = {
        "purpose": purpose,
        "otp_hash": _auth_otp_hash(otp),
        "expires_at": time.time() + _AUTH_OTP_TTL_SECONDS,
        "display_name": display_name,
        "password_hash": password_hash,
    }


def _auth_verify_otp(email: str, purpose: str, otp: str) -> Optional[dict]:
    email = _auth_normalize_email(email)
    entry = _AUTH_OTP_STATE.get(email)

    if not entry:
        return None

    if entry.get("purpose") != purpose:
        return None

    if time.time() > float(entry.get("expires_at", 0)):
        _AUTH_OTP_STATE.pop(email, None)
        return None

    if not secrets.compare_digest(
        str(entry.get("otp_hash", "")),
        _auth_otp_hash(otp),
    ):
        return None

    _AUTH_OTP_STATE.pop(email, None)
    return entry


def _auth_json_error(message: str):
    return {
        "ok": False,
        "error": message,
    }


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/auth/login")
def auth_login(request: AuthLoginRequest):
    email = _auth_normalize_email(request.email)

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    if not _auth_valid_password(request.password):
        return _auth_json_error("Password must be at least 6 characters")

    user = _auth_find_user(email)

    if email == _AUTH_DEMO_EMAIL:
        if not secrets.compare_digest(
            request.password,
            _AUTH_DEMO_PASSWORD,
        ):
            return _auth_json_error("Invalid email or password")

        if user is None:
            try:
                user = _auth_create_user(
                    email=email,
                    display_name="ROBOMLM Demo",
                )
            except Exception:
                user = _auth_find_user(email)

        if user is not None:
            user_id = _auth_user_id(user)
        else:
            user_id = "demo-user"

    else:
        if user is None:
            return _auth_json_error("Invalid email or password")

        credential = _AUTH_CREDENTIALS.get(email)
        if credential is None:
            return _auth_json_error("Invalid email or password")

        try:
            valid = _AUTH_PASSWORD_SERVICE.verify_password(
                request.password,
                credential,
            )
        except Exception:
            valid = False

        if not valid:
            return _auth_json_error("Invalid email or password")

        user_id = _auth_user_id(user)

    if not user_id:
        return _auth_json_error("Authentication account is invalid")

    try:
        token = _auth_issue_token(user_id)
    except Exception as exc:
        logging.exception("Authentication token issuance failed")
        return _auth_json_error(
            "Unable to create authentication session: " + str(exc)
        )

    try:
        _AUTH_USER_REPOSITORY.record_login(user_id)
    except Exception:
        logging.exception("Unable to record login activity")

    return {
        "ok": True,
        "token": token,
        "user_id": user_id,
        "email": email,
        "display_name": _auth_display_name(user),
        "message": "Login successful.",
    }
# ============================================================
# CONSTITUTION ACCEPTANCE
# ============================================================
  

@app.post("/api/auth/accept-constitution")
def auth_accept_constitution(token: str):
    token = (token or "").strip()

    if not token:
        return _auth_json_error("Authentication token required")

    try:
        result = _AUTH_TOKEN_SERVICE.validate(token)
    except Exception:
        logging.exception("Constitution token validation failed")
        return _auth_json_error("Invalid authentication token")

    success = getattr(result, "success", None)

    if success is None and isinstance(result, dict):
        success = result.get("success", result.get("ok"))

    if not success:
        return _auth_json_error("Invalid or expired authentication token")

    user_id = getattr(result, "user_id", None)

    if user_id is None and isinstance(result, dict):
        user_id = result.get("user_id")

    if not user_id:
        return _auth_json_error("Authentication account is invalid")

    return {
        "ok": True,
        "user_id": str(user_id),
        "constitution_accepted": True,
        "message": "Constitution accepted.",
    }

# ============================================================
# SIGNUP â€” START / SEND OTP
# ============================================================

@app.post("/api/auth/signup/start")
def auth_signup_start(request: AuthSignupStartRequest):
    email = _auth_normalize_email(request.email)
    display_name = (request.display_name or "").strip()

    if not display_name:
        return _auth_json_error("Display name required")

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    if not _auth_valid_password(request.password):
        return _auth_json_error("Password must be at least 6 characters")

    if _auth_find_user(email) is not None:
        return _auth_json_error("An account with this email already exists")

    try:
        password_hash = _AUTH_PASSWORD_SERVICE.hash_password(request.password)
    except Exception as exc:
        logging.exception("Password hashing failed during signup")
        return _auth_json_error(
            "Unable to prepare account credentials: " + str(exc)
        )

    otp = _auth_generate_otp()

    _auth_store_otp(
        email=email,
        purpose="signup",
        otp=otp,
        display_name=display_name,
        password_hash=password_hash,
    )

    # Current frontend explicitly supports dev_otp.
    # This keeps development usable without pretending an email provider
    # already exists.
    return {
        "ok": True,
        "email": email,
        "message": "Signup OTP generated.",
        "dev_otp": otp,
        "expires_in": _AUTH_OTP_TTL_SECONDS,
    }
# ============================================================
# RISK DISCLOSURE ACCEPTANCE
# ============================================================
   

@app.post("/api/auth/accept-risk")
def auth_accept_risk(token: str):
    token = (token or "").strip()

    if not token:
        return _auth_json_error("Authentication token required")

    if _auth_is_dev_token(token):
        return {"ok": True, "user_id": _AUTH_DEV_USER_ID, "risk_accepted": True, "message": "Risk disclosure accepted (development mode)."}

    try:
        result = _AUTH_TOKEN_SERVICE.validate(token)
    except Exception:
        logging.exception("Risk disclosure token validation failed")
        return _auth_json_error("Invalid authentication token")

    success = getattr(result, "success", None)

    if success is None and isinstance(result, dict):
        success = result.get("success", result.get("ok"))

    if not success:
        return _auth_json_error("Invalid or expired authentication token")

    user_id = getattr(result, "user_id", None)

    if user_id is None and isinstance(result, dict):
        user_id = result.get("user_id")

    if not user_id:
        return _auth_json_error("Authentication account is invalid")

    return {
        "ok": True,
        "user_id": str(user_id),
        "risk_accepted": True,
        "message": "Risk disclosure accepted.",
    }

# ============================================================
# SIGNUP â€” VERIFY OTP / CREATE ACCOUNT
# ============================================================

@app.post("/api/auth/signup/verify")
def auth_signup_verify(request: AuthSignupVerifyRequest):
    email = _auth_normalize_email(request.email)
    otp = (request.otp or "").strip()

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    if not otp.isdigit() or len(otp) != 6:
        return _auth_json_error("OTP must be exactly 6 digits")

    if _auth_find_user(email) is not None:
        return _auth_json_error("An account with this email already exists")

    entry = _auth_verify_otp(
        email=email,
        purpose="signup",
        otp=otp,
    )

    if entry is None:
        return _auth_json_error("Invalid or expired OTP")

    password_hash = entry.get("password_hash")

    if password_hash is None:
        return _auth_json_error("Signup credential state is invalid")

    try:
        user = _auth_create_user(
            email=email,
            display_name=entry.get("display_name", ""),
        )
    except Exception as exc:
        logging.exception("User creation failed during signup")

        # Duplicate race: try existing account once.
        user = _auth_find_user(email)

        if user is None:
            return _auth_json_error(
                "Unable to create account: " + str(exc)
            )

    user_id = _auth_user_id(user)

    if not user_id:
        return _auth_json_error("Created account has no user id")

    # Authentication secret stays outside UserRecord/UserRepository.
    _AUTH_CREDENTIALS[email] = password_hash

    token = _auth_issue_token(user_id)

    try:
        _AUTH_USER_REPOSITORY.verify_email(user_id)
    except Exception:
        pass

    return {
        "ok": True,
        "token": token,
        "user_id": user_id,
        "email": email,
        "display_name": _auth_display_name(user),
        "message": "Account created successfully.",
    }


# ============================================================
# FORGOT PASSWORD â€” START / SEND OTP
# ============================================================

@app.post("/api/auth/forgot/start")
def auth_forgot_start(request: AuthForgotStartRequest):
    email = _auth_normalize_email(request.email)

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    user = _auth_find_user(email)

    if user is None:
        return _auth_json_error("No account found for this email")

    otp = _auth_generate_otp()

    _auth_store_otp(
        email=email,
        purpose="forgot",
        otp=otp,
    )

    return {
        "ok": True,
        "email": email,
        "message": "Password reset OTP generated.",
        "dev_otp": otp,
        "expires_in": _AUTH_OTP_TTL_SECONDS,
    }


# ============================================================
# FORGOT PASSWORD â€” VERIFY OTP
# ============================================================

@app.post("/api/auth/forgot/verify")
def auth_forgot_verify(request: AuthForgotVerifyRequest):
    email = _auth_normalize_email(request.email)
    otp = (request.otp or "").strip()

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    if not otp.isdigit() or len(otp) != 6:
        return _auth_json_error("OTP must be exactly 6 digits")

    if _auth_find_user(email) is None:
        return _auth_json_error("No account found for this email")

    entry = _auth_verify_otp(
        email=email,
        purpose="forgot",
        otp=otp,
    )

    if entry is None:
        return _auth_json_error("Invalid or expired OTP")

    # The frontend only needs a successful verification before displaying
    # the password-reset step. Keep a short-lived reset authorization marker.
    _AUTH_OTP_STATE[email] = {
        "purpose": "forgot_reset_authorized",
        "expires_at": time.time() + 600,
    }

    return {
        "ok": True,
        "email": email,
        "message": "OTP verified.",
    }


# ============================================================
# FORGOT PASSWORD â€” RESET
# ============================================================

@app.post("/api/auth/forgot/reset")
def auth_forgot_reset(request: AuthForgotResetRequest):
    email = _auth_normalize_email(request.email)
    new_password = request.new_password

    if not _auth_valid_email(email):
        return _auth_json_error("Valid email required")

    if not _auth_valid_password(new_password):
        return _auth_json_error("Password must be at least 6 characters")

    user = _auth_find_user(email)

    if user is None:
        return _auth_json_error("No account found for this email")

    authorization = _AUTH_OTP_STATE.get(email)

    if not authorization:
        return _auth_json_error("Password reset OTP verification required")

    if authorization.get("purpose") != "forgot_reset_authorized":
        return _auth_json_error("Password reset authorization is invalid")

    if time.time() > float(authorization.get("expires_at", 0)):
        _AUTH_OTP_STATE.pop(email, None)
        return _auth_json_error("Password reset authorization expired")

    try:
        password_hash = _AUTH_PASSWORD_SERVICE.hash_password(new_password)
    except Exception as exc:
        logging.exception("Password hashing failed during password reset")
        return _auth_json_error(
            "Unable to reset password: " + str(exc)
        )

    # Credential remains in the authentication boundary.
    _AUTH_CREDENTIALS[email] = password_hash

    _AUTH_OTP_STATE.pop(email, None)

    # Revoke currently issued tokens so the password reset invalidates
    # existing authentication sessions through the existing token service.
    user_id = _auth_user_id(user)

    if user_id:
        try:
            _AUTH_TOKEN_SERVICE.revoke_all_for_user(user_id)
        except Exception:
            pass

    return {
        "ok": True,
        "email": email,
        "message": "Password reset successful.",
    }


# ============================================================
# AUTH STATUS
# ============================================================
_AUTH_DEV_TOKEN = "robomlm-dev-token"
_AUTH_DEV_USER_ID = "dev-user"


def _auth_dev_bypass_enabled() -> bool:
    return os.getenv("ROBOMLM_DEV_AUTH_BYPASS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _auth_is_dev_token(token: str) -> bool:
    return (
        _auth_dev_bypass_enabled()
        and (token or "").strip() == _AUTH_DEV_TOKEN
    )


def _auth_token_user(token: str):
    """
    Validate through the existing TokenService.

    Development mode provides a deterministic local-only identity.
    Normal mode always uses the real TokenService.
    """
    if not token:
        return None

    if _auth_is_dev_token(token):
        return _AUTH_DEV_USER_ID

    try:
        result = _AUTH_TOKEN_SERVICE.validate(token)
    except Exception:
        return None

    if result is None or result is False:
        return None

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        if result.get("valid") is False:
            return None
        return (
            result.get("user_id")
            or result.get("subject")
            or result.get("user")
        )

    if getattr(result, "valid", True) is False:
        return None

    return getattr(result, "user_id", None)

def _auth_is_dev_token(token: str) -> bool:
    return (
        _auth_dev_bypass_enabled()
        and (token or "").strip() == _AUTH_DEV_TOKEN
    )

@app.get("/api/auth/status")
def auth_status(token: str = ""):
    token = (token or "").strip()

    if not token:
        return {
            "logged_in": False,
            "constitution_accepted": False,
            "risk_accepted": False,
        }

    user_id = _auth_token_user(token)

    if not user_id:
        return {
            "logged_in": False,
            "constitution_accepted": False,
            "risk_accepted": False,
        }

    try:
        user = _AUTH_USER_REPOSITORY.get_by_id(user_id)
    except Exception:
        user = None

    if user is None:
        return {
            "logged_in": False,
            "constitution_accepted": False,
            "risk_accepted": False,
        }

    metadata = (
        user.get("metadata", {})
        if isinstance(user, dict)
        else getattr(user, "metadata", {}) or {}
    )

    if not isinstance(metadata, dict):
        metadata = {}

    return {
        "logged_in": True,
        "user_id": user_id,
        "email": _auth_user_email(user),
        "display_name": _auth_display_name(user),

        # Preserve existing frontend redirect contract.
        "constitution_accepted": bool(
            metadata.get("constitution_accepted", False)
        ),
        "risk_accepted": bool(
            metadata.get("risk_accepted", False)
        ),
    }

# ============================================================
# CONSTANTS
# ============================================================

BYBIT_TF_MAP = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "1H": "60",
    "4H": "240",
}


GRADE_ORDER = {
    "B": 1,
    "B+": 2,
    "A": 3,
    "A+": 4,
}


# ============================================================
# BACKEND MODULE MAP
# ============================================================

BACKEND_MODULES = {
    "market_data": [
        "app.markets.market_service",
        "app.markets.market_session",
        "app.markets.market_state",
        "app.markets.contracts.contract_service",
        "app.markets.contracts.contract_registry",
        "app.markets.instruments.instrument_service",
        "app.markets.instruments.instrument_registry",
        "app.markets.registry.market_registry",
        "app.markets.registry.registry_loader",
        "app.markets.registry.venue_registry",
        "app.markets.venues.venue_service",
    ],

    "data_quality": [
        "app.data_quality.completeness_check",
        "app.data_quality.consistency_check",
        "app.data_quality.data_quality_engine",
        "app.data_quality.freshness_check",
        "app.data_quality.latency_check",
        "app.data_quality.source_health",
    ],

    "intelligence": [
        "app.intelligence.commitment_engine",
        "app.intelligence.confidence_engine",
        "app.intelligence.evidence_orchestrator",
        "app.intelligence.intelligence_orchestrator",
        "app.intelligence.magnitude_engine",
        "app.intelligence.market_context",
        "app.intelligence.opportunity_intelligence",
        "app.intelligence.regime_intelligence",
        "app.intelligence.relationship_intelligence",
        "app.intelligence.strategy_intelligence",
        "app.intelligence.timing_intelligence",
        "app.intelligence.verdict_engine",
    ],

    "evidence": [
        "app.intelligence.evidence.ace",
        "app.intelligence.evidence.dar",
        "app.intelligence.evidence.dcs",
        "app.intelligence.evidence.evidence_confidence",
        "app.intelligence.evidence.evidence_conflict",
        "app.intelligence.evidence.evidence_engine_base",
        "app.intelligence.evidence.evidence_normalizer",
        "app.intelligence.evidence.evidence_orchestrator",
        "app.intelligence.evidence.evidence_package",
        "app.intelligence.evidence.mbc",
        "app.intelligence.evidence.mdil",
        "app.intelligence.evidence.mkn",
        "app.intelligence.evidence.msdl",
        "app.intelligence.evidence.ned",
        "app.intelligence.evidence.oxe",
        "app.intelligence.evidence.source_reliability",
        "app.intelligence.evidence.tv",
    ],

    "metrics": [
        "app.intelligence.metrics.eqe",
        "app.intelligence.metrics.lqs",
        "app.intelligence.metrics.mcs",
        "app.intelligence.metrics.mct",
        "app.intelligence.metrics.mts",
        "app.intelligence.metrics.pfs",
        "app.intelligence.metrics.rds",
        "app.intelligence.metrics.tps",
    ],

    "decision": [
        "app.intelligence.decision.1_Decision_Readiness",
        "app.intelligence.decision.2_decision_condition",
        "app.intelligence.decision.3_decision_confidence",
        "app.intelligence.decision.4_decision_relationships",
        "app.intelligence.decision.5_decision_structure",
        "app.intelligence.decision.6_decision_flow",
        "app.intelligence.decision.7_decision_liquidity_volatility",
        "app.intelligence.decision.8_decision_instrument_mechanics",
        "app.intelligence.decision.9_decision_time_event",
        "app.intelligence.decision.10_decision_market_state",
        "app.intelligence.decision.11_decision_transition",
        "app.intelligence.decision.12_decision_future_scenario",
        "app.intelligence.decision.13_decision_decision",
        "app.intelligence.decision.14_decision_validation",
        "app.intelligence.decision.15_decision_learning",
        "app.intelligence.decision.16_decision_intelligence",
        "app.intelligence.decision.decision_explainer",
        "app.intelligence.decision.decision_state",
        "app.intelligence.decision.htf_scalper_engine",
        "app.intelligence.decision.opportunity_ranker",
        "app.intelligence.decision.timing_engine",
    ],

    "opportunity_scanner": [
        "app.intelligence.opportunity.favorites_engine",
        "app.intelligence.opportunity.intraday_engine",
        "app.intelligence.opportunity.liquidity_filter",
        "app.intelligence.opportunity.opportunity_engine",
        "app.intelligence.opportunity.opportunity_explainer",
        "app.intelligence.opportunity.ranking_engine",
        "app.intelligence.opportunity.risk_filter",
        "app.intelligence.opportunity.scanner_engine",
        "app.intelligence.opportunity.timing_engine",
        "app.intelligence.opportunity.top10_engine",
        "app.intelligence.opportunity.universe_engine",
    ],

    "memory": [
        "app.intelligence.memory.decision_memory",
        "app.intelligence.memory.evidence_memory",
        "app.intelligence.memory.market_memory",
        "app.intelligence.memory.memory_retrieval",
        "app.intelligence.memory.memory_service",
        "app.intelligence.memory.outcome_memory",
        "app.intelligence.memory.pattern_memory",
    ],

    "research": [
        "app.intelligence.research.candidate_manager",
        "app.intelligence.research.dataset",
        "app.intelligence.research.deployment_manager",
        "app.intelligence.research.experiment",
        "app.intelligence.research.hypothesis",
        "app.intelligence.research.research_service",
        "app.intelligence.research.stress_testing",
        "app.intelligence.research.validation",
        "app.intelligence.research.version_manager",
    ],

    "cas": [
        "app.intelligence.cas.cas_audit",
        "app.intelligence.cas.cas_orchestrator",
        "app.intelligence.cas.compliance_gate",
        "app.intelligence.cas.execution_safety_gate",
        "app.intelligence.cas.exposure_gate",
        "app.intelligence.cas.position_gate",
        "app.intelligence.cas.restriction_engine",
        "app.intelligence.cas.risk_gate",
        "app.intelligence.cas.suitability_gate",
    ],

    "robomlm_plus": [
        "app.intelligence.robomlm_plus.advanced_decision",
        "app.intelligence.robomlm_plus.emergency_control",
        "app.intelligence.robomlm_plus.execution_preparation",
        "app.intelligence.robomlm_plus.halt_controller",
        "app.intelligence.robomlm_plus.plus_orchestrator",
        "app.intelligence.robomlm_plus.position_monitor",
        "app.intelligence.robomlm_plus.protection",
        "app.intelligence.robomlm_plus.reconciliation",
    ],

    "autorobomlm": [
        "app.autorobimlm.automation_engine",
        "app.autorobimlm.mode_manager",
        "app.autorobimlm.strategy_runner",
        "app.autorobimlm.execution.order_manager",
        "app.autorobimlm.execution.execution_manager",
        "app.autorobimlm.positions.position_manager",
        "app.autorobimlm.reconciliation.reconciliation_engine",
        "app.autorobimlm.risk.automation_risk",
        "app.autorobimlm.kill_switch.kill_switch",
    ],

    "authorization": [
        "app.auth.auth_service",
        "app.auth.login_service",
        "app.auth.password_service",
        "app.auth.signup_service",
        "app.auth.token_service",
        "app.authorization.access_control",
        "app.authorization.entitlement_gate",
        "app.authorization.permission_service",
        "app.subscription.entitlement_service",
        "app.subscription.plan_service",
        "app.subscription.subscription_service",
    ],

    "terminal": [
        "app.terminal.terminal_service",
        "app.terminal.market_context",
        "app.terminal.evidence_strip",
        "app.terminal.intelligence_panel",
        "app.terminal.decision_outlook",
        "app.terminal.risk_panel",
        "app.terminal.cas_status",
    ],
}


# ============================================================
# SAFE SERIALIZATION
# ============================================================

def json_safe(value: Any) -> Any:
    """
    Convert backend objects into frontend-safe JSON.

    Does not modify backend objects.
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            str(k): json_safe(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            json_safe(v)
            for v in value
        ]

    if hasattr(value, "model_dump"):
        try:
            return json_safe(value.model_dump())
        except Exception:
            pass

    if hasattr(value, "dict"):
        try:
            return json_safe(value.dict())
        except Exception:
            pass

    if hasattr(value, "__dict__"):
        try:
            return {
                str(k): json_safe(v)
                for k, v in vars(value).items()
                if not str(k).startswith("_")
            }
        except Exception:
            pass

    return str(value)


# ============================================================
# MODULE INSPECTION
# ============================================================

def _public_api(module: Any) -> list[str]:
    """
    Return public symbols without executing engine logic.
    """

    try:
        return sorted(
            name
            for name in dir(module)
            if not name.startswith("_")
        )
    except Exception:
        return []


def inspect_backend_modules() -> dict[str, Any]:
    """
    Import every known backend module and report its actual
    import status.

    IMPORTANT:
        This is inspection only.
        It does not execute calculations or place orders.
    """

    result: dict[str, Any] = {}
    total = 0
    loaded = 0

    for category, modules in BACKEND_MODULES.items():
        result[category] = []

        for module_name in modules:
            total += 1

            item = {
                "module": module_name,
                "id": module_name.rsplit(".", 1)[-1],
                "category": category,
                "status": "UNKNOWN",
                "public_api": [],
            }

            try:
                module = importlib.import_module(module_name)

                item["status"] = "LOADED"
                item["public_api"] = _public_api(module)

                loaded += 1

            except Exception as exc:
                item["status"] = "ERROR"
                item["error_type"] = type(exc).__name__
                item["error"] = str(exc)[:300]

            result[category].append(item)

    result["summary"] = {
        "loaded": loaded,
        "total": total,
        "health_pct": round(
            (loaded / total) * 100,
            2,
        ) if total else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return result


# ============================================================
# D1-D16 MANIFEST
# ============================================================

DECISION_MANIFEST = [
    {
        "id": "D1",
        "module": "1_Decision_Readiness",
        "name": "Decision Readiness",
    },
    {
        "id": "D2",
        "module": "2_decision_condition",
        "name": "Decision Condition",
    },
    {
        "id": "D3",
        "module": "3_decision_confidence",
        "name": "Decision Confidence",
    },
    {
        "id": "D4",
        "module": "4_decision_relationships",
        "name": "Decision Relationships",
    },
    {
        "id": "D5",
        "module": "5_decision_structure",
        "name": "Decision Structure",
    },
    {
        "id": "D6",
        "module": "6_decision_flow",
        "name": "Decision Flow / Authoritative Formula Layer",
    },
    {
        "id": "D7",
        "module": "7_decision_liquidity_volatility",
        "name": "Liquidity / Volatility",
    },
    {
        "id": "D8",
        "module": "8_decision_instrument_mechanics",
        "name": "Instrument Mechanics",
    },
    {
        "id": "D9",
        "module": "9_decision_time_event",
        "name": "Time / Event",
    },
    {
        "id": "D10",
        "module": "10_decision_market_state",
        "name": "Market State",
    },
    {
        "id": "D11",
        "module": "11_decision_transition",
        "name": "Transition",
    },
    {
        "id": "D12",
        "module": "12_decision_future_scenario",
        "name": "Future Scenario",
    },
    {
        "id": "D13",
        "module": "13_decision_decision",
        "name": "Final Decision",
    },
    {
        "id": "D14",
        "module": "14_decision_validation",
        "name": "Decision Validation",
    },
    {
        "id": "D15",
        "module": "15_decision_learning",
        "name": "Decision Learning",
    },
    {
        "id": "D16",
        "module": "16_decision_intelligence",
        "name": "Decision Intelligence",
    },
]


# ============================================================
# RESEARCH / EQUATION MANIFEST
# ============================================================

EQUATION_MANIFEST = [
    {
        "id": "EQ-0001",
        "name": "Price Motion",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0002",
        "name": "Volatility",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0003",
        "name": "Liquidity",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0004",
        "name": "Order Flow",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0005",
        "name": "Information",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0006",
        "name": "Entropy",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0007",
        "name": "Decision Readiness",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0008",
        "name": "Uncertainty",
        "decision_role": "D6",
    },
    {
        "id": "EQ-0009",
        "name": "Bayesian Posterior / Decay / Learning",
        "decision_role": "D6",
    },
]


# ============================================================
# FRONTEND BACKEND MANIFEST
# ============================================================

FRONTEND_BACKEND_MAP = {
    "terminal": {
        "route": "/terminal",
        "backend": [
            "Market Context",
            "Data Quality",
            "Evidence Cortex",
            "Intelligence Cortex",
            "D1-D16",
            "Risk",
            "CAS",
            "Chart",
            "Memory lineage",
        ],
    },

    "discovery": {
        "route": "/discovery",
        "backend": [
            "Universe",
            "Liquidity",
            "Timing",
            "Intraday",
            "Scanner",
            "Opportunity",
            "Ranking",
            "Top10",
            "Favorites",
        ],
    },

    "buyer": {
        "route": "/buyer",
        "backend": [
            "Market",
            "Instrument",
            "Contract",
            "Strategy",
            "Intelligence",
            "Decision",
            "Risk",
            "CAS",
            "PLUS",
        ],
    },

    "memory": {
        "route": "/memory",
        "backend": [
            "Decision Memory",
            "Evidence Memory",
            "Market Memory",
            "Outcome Memory",
            "Pattern Memory",
            "Retrieval",
        ],
    },

    "research": {
        "route": "/research",
        "backend": [
            "Dataset",
            "Hypothesis",
            "Experiment",
            "Validation",
            "Stress Testing",
            "Candidate",
            "Version",
            "Controlled Deployment",
        ],
    },

    "automation": {
        "route": "/automation",
        "backend": [
            "CAS Approval",
            "AUTOROBOMLM",
            "Strategy Runner",
            "Order Manager",
            "Execution Manager",
            "Position Manager",
            "Reconciliation",
            "Kill Switch",
        ],
    },

    "account": {
        "route": "/account",
        "backend": [
            "Authentication",
            "Authorization",
            "Subscription",
            "Entitlement",
            "Profile",
            "Security",
        ],
    },
}


# ============================================================
# HTML SERVING
# ============================================================

def serve_html(filename: str) -> HTMLResponse:
    """
    Keep the existing frontend pages and route structure.

    common.js is injected once.

    A small backend bridge script is injected as well. This allows
    the existing frontend to consume the live backend without
    rewriting the page architecture.
    """

    path = WEB / filename

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Frontend page not found: {filename}",
        )

    content = path.read_text(
        encoding="utf-8",
    )

    injection = """
<script>
window.ROBOMLM_BACKEND = {
    version: "FINAL-FRONTEND-BACKEND-WIRING-1.0",

    async getJSON(url, options = {}) {
        const response = await fetch(url, {
            credentials: "same-origin",
            ...options
        });

        const text = await response.text();

        let data;

        try {
            data = text ? JSON.parse(text) : {};
        } catch (error) {
            throw new Error(
                "ROBOMLM backend returned invalid JSON: " +
                response.status
            );
        }

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.detail ||
                ("Backend HTTP " + response.status)
            );
        }

        return data;
    },

    terminal(symbol = "BTC/USDT") {
        return this.getJSON(
            "/api/terminal?symbol=" +
            encodeURIComponent(symbol)
        );
    },

    discovery() {
        return this.getJSON("/api/discovery");
    },

    memory() {
        return this.getJSON("/api/memory");
    },

    research() {
        return this.getJSON("/api/research");
    },

    buyerMarkets() {
        return this.getJSON("/api/buyer/markets");
    },

    buyerStrategies() {
        return this.getJSON("/api/buyer/strategies");
    },

    automation() {
        return this.getJSON("/api/automation");
    },

    account() {
        return this.getJSON("/api/account");
    },

    backendMap() {
        return this.getJSON("/api/backend/map");
    },

    backendHealth() {
        return this.getJSON("/api/backend/health");
    },

    d1d16() {
        return this.getJSON("/api/backend/decision");
    },

    equations() {
        return this.getJSON("/api/backend/equations");
    }
};
</script>
"""

    if "</head>" in content:
        content = content.replace(
            "</head>",
            '<script src="/static/js/common.js"></script>\n'
            + injection
            + "\n</head>",
        )
    else:
        content += injection

    return HTMLResponse(content)


# ============================================================
# EXISTING FRONTEND ROUTES â€” DO NOT CHANGE
# ============================================================

@app.get("/")
def page_login():
    return serve_html("login.html")


@app.get("/login")
def page_login_alias():
    return serve_html("login.html")


@app.get("/constitution")
def page_constitution():
    return serve_html("constitution.html")


@app.get("/risk-disclosure")
def page_risk_disclosure():
    return serve_html("risk-disclosure.html")


@app.get("/terminal")
def page_terminal():
    return serve_html("terminal.html")


@app.get("/discovery")
def page_discovery():
    return serve_html("discovery.html")


@app.get("/memory")
def page_memory():
    return serve_html("memory.html")


@app.get("/research")
def page_research():
    return serve_html("research.html")


@app.get("/buyer")
def page_buyer():
    return serve_html("buyer.html")


@app.get("/automation")
def page_automation():
    return serve_html("automation.html")


@app.get("/account")
def page_account():
    return serve_html("account.html")


# ============================================================
# BACKEND HEALTH
# ============================================================

@app.get("/api/backend/health")
def api_backend_health():
    """
    Full backend import health.

    This endpoint does NOT execute trading logic.
    """

    started = time.perf_counter()

    data = inspect_backend_modules()

    elapsed_ms = (
        time.perf_counter() - started
    ) * 1000.0

    data["request"] = {
        "type": "BACKEND_HEALTH",
        "execution_ms": round(elapsed_ms, 2),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    return JSONResponse(
        json_safe(data)
    )


# ============================================================
# BACKEND MAP
# ============================================================

@app.get("/api/backend/map")
def api_backend_map():
    """
    Complete frontend -> backend capability map.

    This is the UI wiring contract.
    """

    return JSONResponse(
        json_safe({
            "frontend": FRONTEND_BACKEND_MAP,
            "backend_categories": {
                key: len(value)
                for key, value in BACKEND_MODULES.items()
            },
            "decision_pipeline": [
                "DATA",
                "EVIDENCE",
                "CONTEXT",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
                "ACTION",
                "EXECUTION",
                "RESULT",
            ],
            "decision_modules": DECISION_MANIFEST,
            "equations": EQUATION_MANIFEST,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })
    )


# ============================================================
# D1-D16
# ============================================================

@app.get("/api/backend/decision")
def api_backend_decision():
    """
    Expose the complete D1-D16 module map to the frontend.

    No D13 calculation is recreated here.
    """

    health = inspect_backend_modules()

    decision_health = {
        item["module"]: item
        for item in health.get("decision", [])
    }

    output = []

    for item in DECISION_MANIFEST:
        module_health = decision_health.get(
            item["module"],
            {
                "status": "NOT_FOUND",
            },
        )

        output.append({
            **item,
            "status": module_health.get(
                "status",
                "UNKNOWN",
            ),
            "public_api": module_health.get(
                "public_api",
                [],
            ),
            "error": module_health.get(
                "error",
            ),
        })

    return JSONResponse(
        json_safe({
            "pipeline": output,
            "total": len(output),
            "loaded": sum(
                1
                for x in output
                if x["status"] == "LOADED"
            ),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })
    )


# ============================================================
# RESEARCH / EQUATIONS
# ============================================================

@app.get("/api/backend/equations")
def api_backend_equations():
    """
    Research/equation exposure.

    The authoritative formulas stay inside the existing backend.
    """

    return JSONResponse(
        json_safe({
            "equations": EQUATION_MANIFEST,
            "source": "existing ROBOMLM D6 research/formula layer",
            "rule": (
                "Gateway exposes lineage; it does not duplicate "
                "or redefine authoritative equations."
            ),
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        })
    )


# ============================================================
# UTILITY
# ============================================================

def _to_bybit_symbol(symbol: str) -> str:
    symbol = (
        symbol
        .strip()
        .replace("/", "")
        .replace("-", "")
        .upper()
    )

    return symbol


# ============================================================
# LIVE PRICE
# ============================================================

@app.get("/api/live/price/{symbol:path}")
def api_live_price(symbol: str):
    """
    Real market price through the existing Bybit adapter.
    """

    try:
        from app.adapters.bybit.bybit_client import BybitClient
        from app.adapters.bybit.bybit_market_data import BybitMarketData

        client = BybitClient()
        client.connect()

        try:
            market_data = BybitMarketData(client)

            raw = market_data.get_raw_ticker(
                _to_bybit_symbol(symbol)
            )

            return JSONResponse({
                "ok": True,
                "symbol": symbol,
                "last": float(
                    raw.get("lastPrice", 0)
                ),
                "high": float(
                    raw.get("highPrice24h", 0)
                ),
                "low": float(
                    raw.get("lowPrice24h", 0)
                ),
                "volume": float(
                    raw.get("volume24h", 0)
                ),
                "change_pct": float(
                    raw.get("price24hPcnt", 0)
                ) * 100.0,
                "source": "Bybit existing adapter",
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            })

        finally:
            client.close()

    except Exception as exc:
        LOGGER.exception(
            "Live price failed for %s",
            symbol,
        )

        return JSONResponse(
            {
                "ok": False,
                "symbol": symbol,
                "error": str(exc),
            },
            status_code=500,
        )


# ============================================================
# LIVE CANDLES
# ============================================================

@app.get("/api/live/candles/{symbol:path}")
def api_live_candles(
    symbol: str,
    tf: str = "1m",
    limit: int = 200,
):
    """
    Real candles through existing market adapter.

    No synthetic candles.
    """

    limit = max(
        1,
        min(int(limit), 1000),
    )

    interval = BYBIT_TF_MAP.get(
        tf,
        "1",
    )

    try:
        from app.adapters.bybit.bybit_client import BybitClient

        client = BybitClient()
        client.connect()

        try:
            response = client.get(
                "/v5/market/kline",
                {
                    "category": "spot",
                    "symbol": _to_bybit_symbol(symbol),
                    "interval": interval,
                    "limit": limit,
                },
            )

            rows = (
                response
                .get("result", {})
                .get("list", [])
            )

            rows = list(
                reversed(rows)
            )

            candles = []

            for row in rows:
                candles.append({
                    "time": int(
                        int(row[0]) / 1000
                    ),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                })

            return JSONResponse({
                "ok": True,
                "symbol": symbol,
                "tf": tf,
                "source": "Bybit existing adapter",
                "candles": candles,
            })

        finally:
            client.close()

    except Exception as exc:
        LOGGER.exception(
            "Candle request failed for %s",
            symbol,
        )

        return JSONResponse(
            {
                "ok": False,
                "symbol": symbol,
                "tf": tf,
                "candles": [],
                "error": str(exc),
            },
            status_code=500,
        )


# ============================================================
# REAL CHART
# ============================================================

@app.get("/api/chart")
def api_chart(
    symbol: str = "BTC/USDT",
    tf: str = "1m",
    limit: int = 200,
):
    """
    Compatibility endpoint.

    IMPORTANT:
        Previous implementation generated random synthetic candles.
        This endpoint now delegates to real market candles.
    """

    result = api_live_candles(
        symbol=symbol,
        tf=tf,
        limit=limit,
    )

    return result
# ============================================================
# PART 2/5
# ROBOMLM LIVE INTELLIGENCE + TERMINAL PIPELINE
# ============================================================


# ============================================================
# OPTIONAL IMPORT HELPERS
# ============================================================

def _import_optional(module_name: str):
    """
    Import an existing ROBOMLM module without making the gateway
    dependent on one optional implementation.

    The backend module remains the owner of its logic.
    """
    try:
        return importlib.import_module(module_name)
    except Exception as exc:
        LOGGER.debug(
            "Optional backend import failed: %s -> %s",
            module_name,
            exc,
        )
        return None


def _find_callable(
    module_names: list[str],
    callable_names: list[str],
):
    """
    Locate an existing public backend callable.

    No new intelligence calculation is created here.
    """

    for module_name in module_names:
        module = _import_optional(module_name)

        if module is None:
            continue

        for name in callable_names:
            fn = getattr(module, name, None)

            if callable(fn):
                return fn, module_name, name

    return None, None, None


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def _extract_value(
    obj: Any,
    *names: str,
    default: Any = None,
):
    """
    Read a field from dict/object/backend result.
    """

    if obj is None:
        return default

    if isinstance(obj, dict):
        for name in names:
            if name in obj:
                return obj[name]

    for name in names:
        try:
            value = getattr(obj, name)
            return value
        except Exception:
            continue

    return default


def _number(
    value: Any,
    default: Optional[float] = None,
) -> Optional[float]:
    try:
        if value is None:
            return default

        if isinstance(value, bool):
            return float(value)

        return float(value)

    except Exception:
        return default


def _bool(
    value: Any,
    default: bool = False,
) -> bool:
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "1",
            "yes",
            "pass",
            "approved",
            "allow",
            "allowed",
            "ready",
        }

    return bool(value)


def _text(
    value: Any,
    default: str = "",
) -> str:
    if value is None:
        return default

    if isinstance(value, str):
        return value

    return str(value)


# ============================================================
# BACKEND CALL COMPATIBILITY
# ============================================================

def _call_backend(
    fn,
    *,
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    payload: Optional[dict] = None,
):
    """
    Call an existing backend function while adapting to its
    actual signature.

    This prevents the web gateway from assuming one fixed
    signature across existing modules.
    """

    if fn is None:
        return None

    payload = payload or {}

    try:
        signature = inspect.signature(fn)
        params = signature.parameters

        kwargs = {}

        aliases = {
            "symbol": symbol,
            "instrument": symbol,
            "ticker": symbol,
            "asset": symbol,
            "timeframe": timeframe,
            "tf": timeframe,
            "interval": timeframe,
            "request": payload,
            "payload": payload,
            "data": payload,
            "context": payload,
        }

        for name, value in aliases.items():
            if name in params and value is not None:
                kwargs[name] = value

        if kwargs:
            return fn(**kwargs)

        if symbol is not None and len(params) == 1:
            parameter = next(iter(params.values()))

            if parameter.name not in {
                "self",
                "cls",
            }:
                return fn(symbol)

        return fn()

    except TypeError:
        try:
            return fn(payload)
        except Exception:
            return None

    except Exception:
        LOGGER.debug(
            "Backend callable execution failed",
            exc_info=True,
        )
        return None


# ============================================================
# BACKEND ENGINE DISCOVERY
# ============================================================

ENGINE_CANDIDATES = {
    "intelligence": (
        [
            "app.intelligence.intelligence_orchestrator",
            "app.intelligence.opportunity_intelligence",
        ],
        [
            "get_intelligence",
            "analyze",
            "evaluate",
            "run",
            "process",
        ],
    ),

    "evidence": (
        [
            "app.intelligence.evidence.evidence_orchestrator",
            "app.intelligence.evidence.evidence_engine_base",
        ],
        [
            "get_evidence",
            "build_evidence",
            "collect",
            "analyze",
            "run",
            "process",
        ],
    ),

    "market_context": (
        [
            "app.intelligence.market_context",
            "app.terminal.market_context",
        ],
        [
            "get_market_context",
            "build_context",
            "get_context",
            "analyze",
            "run",
        ],
    ),

    "decision": (
        [
            "app.intelligence.decision.decision_orchestrator",
            "app.intelligence.decision.13_decision_decision",
        ],
        [
            "decide",
            "make_decision",
            "evaluate",
            "run",
            "process",
        ],
    ),

    "risk": (
        [
            "app.intelligence.risk.risk_orchestrator",
            "app.risk.risk_engine",
            "app.terminal.risk_panel",
        ],
        [
            "evaluate_risk",
            "assess_risk",
            "calculate_risk",
            "run",
            "evaluate",
        ],
    ),

    "cas": (
        [
            "app.intelligence.cas.cas_orchestrator",
        ],
        [
            "authorize",
            "evaluate",
            "check",
            "run",
            "process",
        ],
    ),

    "opportunity": (
        [
            "app.intelligence.opportunity.opportunity_engine",
            "app.intelligence.opportunity.scanner_engine",
        ],
        [
            "scan",
            "discover",
            "find_opportunities",
            "run",
            "process",
        ],
    ),

    "memory": (
        [
            "app.intelligence.memory.memory_service",
            "app.intelligence.memory.memory_retrieval",
        ],
        [
            "retrieve",
            "search",
            "get_memory",
            "query",
            "run",
        ],
    ),
}


# ============================================================
# ENGINE STATUS
# ============================================================

def _engine_locator(category: str):
    candidate = ENGINE_CANDIDATES.get(category)

    if not candidate:
        return None, None, None

    modules, functions = candidate

    return _find_callable(
        modules,
        functions,
    )


def get_engine_status() -> dict[str, Any]:
    result = {}

    for category in ENGINE_CANDIDATES:
        fn, module_name, fn_name = _engine_locator(
            category
        )

        result[category] = {
            "available": fn is not None,
            "module": module_name,
            "callable": fn_name,
        }

    return result


# ============================================================
# LIVE SIGNAL â€” EXISTING ENGINE FIRST
# ============================================================

def _existing_live_signal(symbol: str):
    """
    Existing live_signal remains an adapter/legacy evidence source.

    It is NOT replaced by a new scoring engine here.
    """

    candidates = [
        "app.intelligence.live_signal",
        "app.intelligence.signal_engine",
    ]

    fn, module_name, fn_name = _find_callable(
        candidates,
        [
            "get_signal",
            "generate_signal",
            "analyze_symbol",
        ],
    )

    if fn is None:
        return None

    try:
        result = _call_backend(
            fn,
            symbol=symbol,
            timeframe="1m",
        )

        return {
            "result": json_safe(result),
            "source": module_name,
            "callable": fn_name,
        }

    except Exception as exc:
        return {
            "result": None,
            "source": module_name,
            "callable": fn_name,
            "error": str(exc),
        }


# ============================================================
# TERMINAL CONTEXT
# ============================================================

def _build_terminal_payload(
    symbol: str,
    timeframe: str,
):
    """
    Build the request context that is passed into existing
    backend engines.

    No decision is made here.
    """

    return {
        "symbol": symbol,
        "instrument": symbol,
        "timeframe": timeframe,
        "tf": timeframe,
        "requested_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": "ROBOMLM_FRONTEND",
    }


# ============================================================
# GENERIC ENGINE EXECUTION
# ============================================================

def _run_existing_engine(
    category: str,
    *,
    symbol: str,
    timeframe: str,
    payload: dict,
):
    """
    Run one existing backend engine if a callable exists.

    Missing optional engines are represented explicitly rather
    than replaced with fake intelligence.
    """

    fn, module_name, fn_name = _engine_locator(
        category
    )

    if fn is None:
        return {
            "status": "NOT_WIRED",
            "category": category,
            "module": module_name,
            "callable": fn_name,
            "data": None,
        }

    started = time.perf_counter()

    try:
        result = _call_backend(
            fn,
            symbol=symbol,
            timeframe=timeframe,
            payload=payload,
        )

        elapsed = (
            time.perf_counter() - started
        ) * 1000.0

        return {
            "status": "EXECUTED",
            "category": category,
            "module": module_name,
            "callable": fn_name,
            "execution_ms": round(
                elapsed,
                2,
            ),
            "data": json_safe(result),
        }

    except Exception as exc:
        elapsed = (
            time.perf_counter() - started
        ) * 1000.0

        LOGGER.exception(
            "%s engine failed",
            category,
        )

        return {
            "status": "ERROR",
            "category": category,
            "module": module_name,
            "callable": fn_name,
            "execution_ms": round(
                elapsed,
                2,
            ),
            "data": None,
            "error": str(exc),
        }


# ============================================================
# DECISION RESULT EXTRACTION
# ============================================================

def _normalize_decision(result: Any) -> dict[str, Any]:
    """
    Normalize existing D13 output for frontend consumption.

    This does NOT calculate D13.
    """

    if isinstance(result, dict):
        source = result
    else:
        source = json_safe(result)

        if not isinstance(source, dict):
            source = {
                "raw": source,
            }

    decision = _text(
        _extract_value(
            source,
            "decision",
            "verdict",
            "action",
            "result",
        ),
        "UNKNOWN",
    ).upper()

    direction = _text(
        _extract_value(
            source,
            "direction",
            "side",
        ),
        "NONE",
    ).upper()

    score = _number(
        _extract_value(
            source,
            "decision_score",
            "score",
            "final_score",
        )
    )

    approved = _bool(
        _extract_value(
            source,
            "approved",
            "is_approved",
            "allow",
        ),
        False,
    )

    confidence = _number(
        _extract_value(
            source,
            "confidence",
            "confidence_score",
        )
    )

    reasons = _extract_value(
        source,
        "gate_reasons",
        "reasons",
        "decision_reasons",
        default=[],
    )

    if reasons is None:
        reasons = []

    if not isinstance(reasons, list):
        reasons = [reasons]

    conflicts = _extract_value(
        source,
        "conflict_flags",
        "conflicts",
        default=[],
    )

    if conflicts is None:
        conflicts = []

    if not isinstance(conflicts, list):
        conflicts = [conflicts]

    return {
        "decision": decision,
        "direction": direction,
        "decision_score": score,
        "approved": approved,
        "confidence": confidence,
        "gate_reasons": json_safe(reasons),
        "conflict_flags": json_safe(conflicts),
        "raw": json_safe(source),
    }


# ============================================================
# EVIDENCE RESULT EXTRACTION
# ============================================================

def _normalize_evidence(result: Any) -> dict[str, Any]:
    if result is None:
        return {
            "status": "NOT_AVAILABLE",
            "items": [],
            "count": 0,
        }

    raw = json_safe(result)

    if isinstance(raw, dict):
        items = _extract_value(
            raw,
            "evidence",
            "items",
            "evidence_items",
            default=[],
        )

        status = _text(
            _extract_value(
                raw,
                "status",
                "package_status",
                "evidence_status",
            ),
            "AVAILABLE",
        )

        score = _number(
            _extract_value(
                raw,
                "evidence_score",
                "score",
                "confidence",
            )
        )

    elif isinstance(raw, list):
        items = raw
        status = "AVAILABLE"
        score = None

    else:
        items = []
        status = "AVAILABLE"
        score = None

    if items is None:
        items = []

    if not isinstance(items, list):
        items = [items]

    normalized_items = []

    for item in items:
        if isinstance(item, dict):
            normalized_items.append(item)
        else:
            normalized_items.append({
                "value": json_safe(item),
            })

    return {
        "status": status,
        "score": score,
        "items": normalized_items,
        "count": len(normalized_items),
    }


# ============================================================
# INTELLIGENCE RESULT EXTRACTION
# ============================================================

def _normalize_intelligence(result: Any) -> dict[str, Any]:
    if result is None:
        return {
            "status": "NOT_AVAILABLE",
            "data": None,
        }

    raw = json_safe(result)

    if isinstance(raw, dict):
        return {
            "status": _text(
                _extract_value(
                    raw,
                    "status",
                    "state",
                ),
                "AVAILABLE",
            ),
            "data": raw,
        }

    return {
        "status": "AVAILABLE",
        "data": raw,
    }


# ============================================================
# RISK RESULT EXTRACTION
# ============================================================

def _normalize_risk(result: Any) -> dict[str, Any]:
    if result is None:
        return {
            "status": "NOT_AVAILABLE",
            "approved": False,
            "data": None,
        }

    raw = json_safe(result)

    if not isinstance(raw, dict):
        return {
            "status": "AVAILABLE",
            "approved": False,
            "data": raw,
        }

    approved = _bool(
        _extract_value(
            raw,
            "approved",
            "allowed",
            "pass",
            "passed",
        ),
        False,
    )

    return {
        "status": _text(
            _extract_value(
                raw,
                "status",
                "state",
            ),
            "AVAILABLE",
        ),
        "approved": approved,
        "score": _number(
            _extract_value(
                raw,
                "risk_score",
                "score",
            )
        ),
        "data": raw,
    }


# ============================================================
# CAS RESULT EXTRACTION
# ============================================================

def _normalize_cas(result: Any) -> dict[str, Any]:
    if result is None:
        return {
            "status": "NOT_AVAILABLE",
            "authorization": "UNKNOWN",
            "allowed": False,
            "gates": {},
        }

    raw = json_safe(result)

    if not isinstance(raw, dict):
        return {
            "status": "AVAILABLE",
            "authorization": "UNKNOWN",
            "allowed": False,
            "gates": {},
            "raw": raw,
        }

    authorization = _text(
        _extract_value(
            raw,
            "authorization",
            "decision",
            "status",
            "verdict",
        ),
        "UNKNOWN",
    ).upper()

    allowed = _bool(
        _extract_value(
            raw,
            "allowed",
            "approved",
            "authorized",
        ),
        False,
    )

    gates = {}

    possible_gate_names = [
        "suitability",
        "risk",
        "exposure",
        "position",
        "execution_safety",
        "compliance",
        "restrictions",
    ]

    for gate in possible_gate_names:
        value = _extract_value(
            raw,
            gate,
            f"{gate}_gate",
        )

        if value is not None:
            gates[gate] = json_safe(value)

    return {
        "status": "AVAILABLE",
        "authorization": authorization,
        "allowed": allowed,
        "gates": gates,
        "raw": raw,
    }


# ============================================================
# TERMINAL PIPELINE
# ============================================================

def build_terminal_intelligence(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    """
    Full terminal backend pipeline.

    DATA
      -> EVIDENCE
      -> CONTEXT
      -> INTELLIGENCE
      -> DECISION
      -> RISK
      -> CAS
      -> RESULT

    The gateway does not invent missing results.
    """

    started = time.perf_counter()

    symbol = symbol.strip() or "BTC/USDT"
    timeframe = timeframe.strip() or "1m"

    payload = _build_terminal_payload(
        symbol,
        timeframe,
    )

    # --------------------------------------------------------
    # 1. EXISTING LIVE SIGNAL / MARKET DATA
    # --------------------------------------------------------

    live_signal = _existing_live_signal(
        symbol
    )

    # --------------------------------------------------------
    # 2. EVIDENCE
    # --------------------------------------------------------

    evidence_result = _run_existing_engine(
        "evidence",
        symbol=symbol,
        timeframe=timeframe,
        payload=payload,
    )

    evidence = _normalize_evidence(
        evidence_result.get("data")
        if evidence_result
        else None
    )

    # --------------------------------------------------------
    # 3. MARKET CONTEXT
    # --------------------------------------------------------

    context_result = _run_existing_engine(
        "market_context",
        symbol=symbol,
        timeframe=timeframe,
        payload=payload,
    )

    context = json_safe(
        context_result.get("data")
        if context_result
        else None
    )

    # --------------------------------------------------------
    # 4. INTELLIGENCE
    # --------------------------------------------------------

    intelligence_result = _run_existing_engine(
        "intelligence",
        symbol=symbol,
        timeframe=timeframe,
        payload={
            **payload,
            "evidence": evidence,
            "market_context": context,
        },
    )

    intelligence = _normalize_intelligence(
        intelligence_result.get("data")
        if intelligence_result
        else None
    )

    # --------------------------------------------------------
    # 5. DECISION
    # --------------------------------------------------------

    decision_result = _run_existing_engine(
        "decision",
        symbol=symbol,
        timeframe=timeframe,
        payload={
            **payload,
            "evidence": evidence,
            "market_context": context,
            "intelligence": intelligence,
        },
    )

    decision = _normalize_decision(
        decision_result.get("data")
        if decision_result
        else None
    )

    # --------------------------------------------------------
    # 6. RISK
    # --------------------------------------------------------

    risk_result = _run_existing_engine(
        "risk",
        symbol=symbol,
        timeframe=timeframe,
        payload={
            **payload,
            "evidence": evidence,
            "market_context": context,
            "intelligence": intelligence,
            "decision": decision,
        },
    )

    risk = _normalize_risk(
        risk_result.get("data")
        if risk_result
        else None
    )

    # --------------------------------------------------------
    # 7. CAS
    # --------------------------------------------------------

    cas_result = _run_existing_engine(
        "cas",
        symbol=symbol,
        timeframe=timeframe,
        payload={
            **payload,
            "evidence": evidence,
            "market_context": context,
            "intelligence": intelligence,
            "decision": decision,
            "risk": risk,
        },
    )

    cas = _normalize_cas(
        cas_result.get("data")
        if cas_result
        else None
    )

    # --------------------------------------------------------
    # 8. FINAL PIPELINE STATE
    # --------------------------------------------------------

    decision_actionable = (
        decision["approved"]
        and decision["decision"]
        not in {
            "HOLD",
            "NEUTRAL",
            "UNKNOWN",
        }
    )

    cas_authorized = cas["allowed"]

    total_ms = (
        time.perf_counter() - started
    ) * 1000.0

    return {
        "ok": True,

        "system": {
            "name": "ROBOMLM_PLUS",
            "version": "FINAL-FRONTEND-BACKEND-WIRING-1.0",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "execution_ms": round(
                total_ms,
                2,
            ),
        },

        "identity": {
            "symbol": symbol,
            "instrument": symbol,
            "timeframe": timeframe,
        },

        "pipeline": [
            "DATA",
            "EVIDENCE",
            "CONTEXT",
            "INTELLIGENCE",
            "DECISION",
            "RISK",
            "CAS",
            "RESULT",
        ],

        "data": {
            "live_signal": live_signal,
        },

        "evidence": evidence,

        "market_context": context,

        "intelligence": intelligence,

        "decision": decision,

        "risk": risk,

        "cas": cas,

        "authorization": {
            "decision_actionable": decision_actionable,
            "risk_approved": risk["approved"],
            "cas_authorized": cas_authorized,

            "action_allowed": bool(
                decision_actionable
                and risk["approved"]
                and cas_authorized
            ),
        },

        "backend_engine_status": get_engine_status(),

        "research_lineage": {
            "equations": EQUATION_MANIFEST,
            "decision_layers": DECISION_MANIFEST,
            "rule": (
                "Existing research and engine outputs remain "
                "authoritative. The frontend gateway exposes "
                "their lineage and result."
            ),
        },
    }


# ============================================================================
# TERMINAL API BRIDGE
# ============================================================================
# Frontend
#    â†“
# /api/terminal
#    â†“
# existing app/api/v1/terminal_api.py contract
#    â†“
# existing Application Service
#    â†“
# existing ROBOMLM_PLUS backend
#
# IMPORTANT:
# - Do NOT calculate D1-D16 here.
# - Do NOT calculate EQE here.
# - Do NOT create BUY/SELL here.
# - Do NOT bypass Risk/CAS.
# - Do NOT call broker SDKs here.
# - Do NOT use live_signal as the terminal authority.
# ============================================================================

@app.get("/api/terminal")
def api_terminal(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
    market: str = "",
    instrument: str = "",
):
    """
    Frontend-compatible Terminal endpoint.

    The web frontend keeps using:
        GET /api/terminal?symbol=BTC/USDT

    Internally this delegates to the existing Terminal API/application
    contract instead of maintaining a second terminal engine inside serve.py.
    """

    from fastapi.responses import JSONResponse

    symbol = (symbol or "BTC/USDT").strip()
    timeframe = (timeframe or "1m").strip()
    market = (market or "").strip()
    instrument = (instrument or "").strip()

    try:
        # ------------------------------------------------------------------
        # Existing Terminal API contract
        # ------------------------------------------------------------------
        from app.api.v1.terminal_api import terminal as _terminal_api

        # Reuse the existing Pydantic request model rather than inventing
        # another request schema in serve.py.
        from app.api.v1.terminal_api import TerminalRequest

        request = TerminalRequest(
            symbol=symbol,
            timeframe=timeframe,
            metadata={
                "market": market,
                "instrument": instrument,
                "source": "web_terminal",
            },
        )

        # terminal_api.terminal() already owns the Application Service
        # boundary. Calling it here keeps serve.py as a web adapter only.
        result = _terminal_api(request)

        # FastAPI endpoint functions can return either a dict/model or a
        # response object. Preserve the response if one is returned.
        if isinstance(result, JSONResponse):
            return result

        # ------------------------------------------------------------------
        # Frontend presentation contract
        # ------------------------------------------------------------------
        try:
            from app.api.v1.terminal_api import _terminal_frontend_contract

            result = _terminal_frontend_contract(
                result,
                symbol=symbol,
                timeframe=timeframe,
                market=market,
                instrument=instrument,
            )
        except ImportError:
            # The terminal API result itself remains authoritative.
            # Do not manufacture missing intelligence here.
            pass

        return JSONResponse(
            content=result
            if isinstance(result, dict)
            else {
                "status": "OK",
                "symbol": symbol,
                "timeframe": timeframe,
                "result": result,
            }
        )

    except Exception as exc:
        # ------------------------------------------------------------------
        # Honest failure boundary
        # ------------------------------------------------------------------
        # Never convert backend failure into fake HOLD/BUY/SELL data.
        # The frontend must know that the Terminal backend is unavailable.
        return JSONResponse(
            status_code=503,
            content={
                "status": "ERROR",
                "ok": False,
                "symbol": symbol,
                "timeframe": timeframe,
                "error": "terminal_backend_unavailable",
                "message": str(exc)[:500],
            },
        )


# ============================================================================
# TERMINAL FRONTEND CONTEXT
# ============================================================================
# Used by terminal.js when it needs the complete backend context separately
# from the main Terminal analysis response.
# ============================================================================

@app.get("/api/terminal/context")
def api_terminal_context(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
    market: str = "",
    instrument: str = "",
):
    """
    Return the existing Terminal Service frontend context.

    This endpoint is presentation-only.
    It does not create a second intelligence/decision engine.
    """

    from fastapi.responses import JSONResponse

    symbol = (symbol or "BTC/USDT").strip()
    timeframe = (timeframe or "1m").strip()
    market = (market or "").strip()
    instrument = (instrument or "").strip()

    try:
        from app.terminal.terminal_service import terminal_frontend_context

        context = terminal_frontend_context(
            symbol=symbol,
            timeframe=timeframe,
            market=market,
            instrument=instrument,
        )

        return JSONResponse(
            content=context
            if isinstance(context, dict)
            else {
                "status": "OK",
                "symbol": symbol,
                "timeframe": timeframe,
                "context": context,
            }
        )

    except TypeError:
        # Some existing Terminal Service implementations may expose the
        # context function with a more generic argument contract.
        try:
            from app.terminal.terminal_service import terminal_frontend_payload

            payload = terminal_frontend_payload(
                symbol=symbol,
                timeframe=timeframe,
                market=market,
                instrument=instrument,
            )

            return JSONResponse(
                content=payload
                if isinstance(payload, dict)
                else {
                    "status": "OK",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "context": payload,
                }
            )

        except Exception as exc:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "ERROR",
                    "ok": False,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "error": "terminal_context_unavailable",
                    "message": str(exc)[:500],
                },
            )

    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "ERROR",
                "ok": False,
                "symbol": symbol,
                "timeframe": timeframe,
                "error": "terminal_context_unavailable",
                "message": str(exc)[:500],
            },
        )


# ============================================================================
# TERMINAL FRONTEND MAP
# ============================================================================
# Allows frontend code to discover the backend â†’ UI mapping without
# duplicating the Terminal Service contract in JavaScript.
# ============================================================================

@app.get("/api/terminal/frontend-map")
def api_terminal_frontend_map():
    """
    Return the authoritative Terminal frontend UI contract/map.
    """

    from fastapi.responses import JSONResponse

    try:
        from app.api.v1.terminal_api import terminal_frontend_map

        result = terminal_frontend_map()

        return JSONResponse(
            content=result
            if isinstance(result, dict)
            else {"status": "OK", "map": result}
        )

    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "ERROR",
                "ok": False,
                "error": "terminal_frontend_map_unavailable",
                "message": str(exc)[:500],
            },
        )

# ============================================================
# TERMINAL COMPONENT ENDPOINTS
# ============================================================

@app.get("/api/terminal/evidence")
def api_terminal_evidence(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],
        "evidence": result["evidence"],
        "live_signal": result["data"]["live_signal"],
    })


@app.get("/api/terminal/intelligence")
def api_terminal_intelligence(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],
        "market_context": result["market_context"],
        "intelligence": result["intelligence"],
    })


@app.get("/api/terminal/decision")
def api_terminal_decision(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],
        "decision": result["decision"],
    })


@app.get("/api/terminal/risk")
def api_terminal_risk(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],
        "risk": result["risk"],
    })


@app.get("/api/terminal/cas")
def api_terminal_cas(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],
        "cas": result["cas"],
        "authorization": result["authorization"],
    })


# ============================================================
# D1-D16 FRONTEND DETAIL
# ============================================================

@app.get("/api/terminal/decision-layers")
def api_terminal_decision_layers(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    """
    Frontend-readable D1-D16 surface.

    Actual D1-D16 engines remain owners of their calculations.
    """

    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    decision = result["decision"]

    layers = []

    for item in DECISION_MANIFEST:
        layers.append({
            "id": item["id"],
            "module": item["module"],
            "name": item["name"],
            "status": "AVAILABLE",
        })

    return JSONResponse({
        "ok": True,
        "identity": result["identity"],
        "layers": layers,
        "final_decision": decision,
        "equations": EQUATION_MANIFEST,
    })


# ============================================================
# PIPELINE TRACE
# ============================================================

@app.get("/api/terminal/pipeline")
def api_terminal_pipeline(
    symbol: str = "BTC/USDT",
    timeframe: str = "1m",
):
    """
    Compact frontend pipeline trace.
    """

    result = build_terminal_intelligence(
        symbol=symbol,
        timeframe=timeframe,
    )

    return JSONResponse({
        "ok": result["ok"],
        "identity": result["identity"],

        "pipeline": [
            {
                "stage": "DATA",
                "status": (
                    "AVAILABLE"
                    if result["data"]["live_signal"]
                    else "PARTIAL"
                ),
            },
            {
                "stage": "EVIDENCE",
                "status": result["evidence"]["status"],
                "count": result["evidence"]["count"],
            },
            {
                "stage": "CONTEXT",
                "status": (
                    "AVAILABLE"
                    if result["market_context"] is not None
                    else "NOT_AVAILABLE"
                ),
            },
            {
                "stage": "INTELLIGENCE",
                "status": result["intelligence"]["status"],
            },
            {
                "stage": "DECISION",
                "status": (
                    "APPROVED"
                    if result["decision"]["approved"]
                    else "HOLD_OR_REVIEW"
                ),
                "decision": result["decision"]["decision"],
                "direction": result["decision"]["direction"],
            },
            {
                "stage": "RISK",
                "status": result["risk"]["status"],
                "approved": result["risk"]["approved"],
            },
            {
                "stage": "CAS",
                "status": result["cas"]["status"],
                "authorization": result["cas"]["authorization"],
            },
            {
                "stage": "RESULT",
                "action_allowed": result[
                    "authorization"
                ]["action_allowed"],
            },
        ],
    })


# ============================================================
# ENGINE DEBUG SURFACE
# ============================================================

@app.get("/api/backend/engines")
def api_backend_engines():
    """
    Shows which existing engine callables are discoverable.

    Useful during final wiring/audit.
    """

    return JSONResponse({
        "ok": True,
        "engines": get_engine_status(),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    })
# ============================================================
# ROBOMLM_PLUS serve.py
# PART 3 / 5
# DISCOVERY + SCANNER + OPPORTUNITY + TOP10 BACKEND WIRING
# ============================================================

# ------------------------------------------------------------
# Discovery backend helpers
# ------------------------------------------------------------

_DISCOVERY_ENGINE_CANDIDATES = {
    "universe": [
        "app.intelligence.opportunity.universe_engine",
    ],
    "liquidity": [
        "app.intelligence.opportunity.liquidity_filter",
    ],
    "risk": [
        "app.intelligence.opportunity.risk_filter",
    ],
    "timing": [
        "app.intelligence.opportunity.timing_engine",
        "app.intelligence.decision.timing_engine",
    ],
    "intraday": [
        "app.intelligence.opportunity.intraday_engine",
    ],
    "scanner": [
        "app.intelligence.opportunity.scanner_engine",
    ],
    "ranking": [
        "app.intelligence.opportunity.ranking_engine",
        "app.intelligence.decision.opportunity_ranker",
    ],
    "top10": [
        "app.intelligence.opportunity.top10_engine",
    ],
    "opportunity": [
        "app.intelligence.opportunity.opportunity_engine",
    ],
    "explainer": [
        "app.intelligence.opportunity.opportunity_explainer",
    ],
    "favorites": [
        "app.intelligence.opportunity.favorites_engine",
    ],
}


def _safe_import_module(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def _get_module_class_or_object(module, names):
    if module is None:
        return None

    for name in names:
        try:
            obj = getattr(module, name, None)
            if obj is not None:
                return obj
        except Exception:
            continue

    return None


def _discover_public_callables(module):
    """
    Introspection only.

    This function does NOT execute anything.
    It is used to understand what an existing backend module exposes.
    """
    if module is None:
        return []

    names = []

    try:
        for name in dir(module):
            if name.startswith("_"):
                continue

            try:
                obj = getattr(module, name)
            except Exception:
                continue

            if callable(obj):
                names.append(name)
    except Exception:
        pass

    return sorted(set(names))


def _module_runtime_info(module_name: str):
    module = _safe_import_module(module_name)

    if module is None:
        return {
            "module": module_name,
            "available": False,
            "callables": [],
            "error": "MODULE_IMPORT_FAILED",
        }

    return {
        "module": module_name,
        "available": True,
        "callables": _discover_public_callables(module),
        "error": None,
    }


# ------------------------------------------------------------
# Explicit scanner invocation candidates
# ------------------------------------------------------------

_SCANNER_METHOD_NAMES = (
    "scan",
    "run_scan",
    "run",
    "execute",
    "discover",
    "discover_opportunities",
    "find_opportunities",
    "build_opportunities",
    "generate",
    "process",
)


def _candidate_modules_for_discovery(kind: str):
    return _DISCOVERY_ENGINE_CANDIDATES.get(kind, [])


def _find_safe_callable(module, names):
    if module is None:
        return None, None

    for name in names:
        try:
            fn = getattr(module, name, None)
        except Exception:
            fn = None

        if callable(fn):
            return fn, name

    return None, None


def _call_with_supported_kwargs(fn, kwargs):
    """
    Call an existing backend callable without inventing positional
    arguments.

    Only keyword parameters that the callable actually accepts are used.
    """
    if fn is None:
        return None, {
            "ok": False,
            "error": "CALLABLE_NOT_FOUND",
        }

    try:
        signature = inspect.signature(fn)
    except Exception as exc:
        return None, {
            "ok": False,
            "error": f"SIGNATURE_UNAVAILABLE:{type(exc).__name__}",
        }

    accepted = {}
    has_var_kwargs = False

    for param in signature.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            has_var_kwargs = True
            break

        if param.name in kwargs:
            accepted[param.name] = kwargs[param.name]

    if has_var_kwargs:
        accepted = dict(kwargs)

    try:
        result = fn(**accepted)

        return result, {
            "ok": True,
            "error": None,
            "function": getattr(fn, "__name__", str(fn)),
            "arguments_used": sorted(accepted.keys()),
        }

    except TypeError as exc:
        return None, {
            "ok": False,
            "error": f"TYPE_ERROR:{exc}",
            "function": getattr(fn, "__name__", str(fn)),
            "arguments_used": sorted(accepted.keys()),
        }

    except Exception as exc:
        return None, {
            "ok": False,
            "error": f"{type(exc).__name__}:{exc}",
            "function": getattr(fn, "__name__", str(fn)),
            "arguments_used": sorted(accepted.keys()),
        }


def _execute_existing_discovery_engine(
    kind: str,
    symbol: str = None,
    market: str = None,
    timeframe: str = None,
    payload: dict = None,
):
    """
    Existing-engine bridge.

    Important:
    - does not duplicate scanner formulas;
    - does not create Buy/Sell decisions;
    - does not bypass Decision/Risk/CAS;
    - returns backend result + provenance.
    """
    payload = payload or {}

    kwargs = dict(payload)

    if symbol:
        kwargs.setdefault("symbol", symbol)

    if market:
        kwargs.setdefault("market", market)

    if timeframe:
        kwargs.setdefault("timeframe", timeframe)

    for module_name in _candidate_modules_for_discovery(kind):

        module = _safe_import_module(module_name)

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _SCANNER_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, call_info = _call_with_supported_kwargs(
            fn,
            kwargs,
        )

        if call_info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": call_info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_SAFE_EXISTING_ENGINE_ENTRYPOINT",
        },
    }


# ------------------------------------------------------------
# Discovery result extraction
# ------------------------------------------------------------

def _as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    if isinstance(value, dict):
        for key in (
            "items",
            "rows",
            "results",
            "opportunities",
            "candidates",
            "assets",
            "data",
            "top10",
            "signals",
        ):
            candidate = value.get(key)

            if isinstance(candidate, (list, tuple, set)):
                return list(candidate)

        return [value]

    return [value]


def _extract_discovery_rows(raw):
    if raw is None:
        return []

    if isinstance(raw, dict):
        for key in (
            "opportunities",
            "results",
            "rows",
            "items",
            "candidates",
            "assets",
            "top10",
            "signals",
            "data",
        ):
            if key in raw:
                return _as_list(raw.get(key))

    return _as_list(raw)


def _row_get(row, *names, default=None):
    if row is None:
        return default

    if isinstance(row, dict):
        for name in names:
            if name in row:
                return row[name]

        return default

    for name in names:
        try:
            value = getattr(row, name, None)

            if value is not None:
                return value
        except Exception:
            continue

    return default


def _normalize_discovery_row(row, index=0):
    symbol = _row_get(
        row,
        "symbol",
        "ticker",
        "instrument",
        "asset",
        "pair",
        default="",
    )

    market = _row_get(
        row,
        "market",
        "asset_class",
        "market_type",
        "venue",
        default="",
    )

    direction = _row_get(
        row,
        "direction",
        "bias",
        "side",
        "signal",
        default="HOLD",
    )

    grade = _row_get(
        row,
        "grade",
        "quality_grade",
        "opportunity_grade",
        default="",
    )

    eqe = _row_get(
        row,
        "eqe",
        "EQE",
        "eqe_score",
        "quality_score",
        "opportunity_score",
        default=None,
    )

    confidence = _row_get(
        row,
        "confidence",
        "confidence_score",
        "probability",
        default=None,
    )

    rr = _row_get(
        row,
        "rr",
        "risk_reward",
        "risk_reward_ratio",
        default=None,
    )

    risk = _row_get(
        row,
        "risk",
        "risk_score",
        "risk_level",
        default=None,
    )

    timing = _row_get(
        row,
        "timing",
        "timing_status",
        "timing_score",
        default=None,
    )

    price = _row_get(
        row,
        "price",
        "last_price",
        "entry_price",
        "mark_price",
        default=None,
    )

    reason = _row_get(
        row,
        "reason",
        "explanation",
        "thesis",
        "summary",
        default="",
    )

    status = _row_get(
        row,
        "status",
        "state",
        "opportunity_status",
        default="UNKNOWN",
    )

    evidence = _row_get(
        row,
        "evidence",
        "evidence_score",
        "evidence_quality",
        default=None,
    )

    return {
        "rank": index + 1,
        "symbol": str(symbol or ""),
        "market": str(market or ""),
        "direction": str(direction or "HOLD").upper(),
        "grade": str(grade or ""),
        "eqe": _number(eqe, None),
        "confidence": _number(confidence, None),
        "rr": _number(rr, None),
        "risk": _number(risk, None),
        "timing": (
            timing
            if isinstance(timing, str)
            else _number(timing, None)
        ),
        "price": _number(price, None),
        "evidence": _number(evidence, None),
        "status": str(status or "UNKNOWN").upper(),
        "reason": str(reason or ""),
        "raw": json_safe(row),
    }


# ------------------------------------------------------------
# Grade calculation
# ------------------------------------------------------------

def _grade_from_eqe(eqe):
    """
    Uses the existing ROBOMLM acceptance bands.

    This is presentation/ranking normalization only.
    It is NOT an auto-entry rule.
    """
    if eqe is None:
        return ""

    try:
        value = float(eqe)
    except Exception:
        return ""

    if value >= 74:
        return "A+"

    if value >= 65:
        return "A"

    if value >= 45:
        return "B+"

    if value >= 35:
        return "B"

    return "NO TRADE"


def _apply_grade_if_missing(rows):
    output = []

    for row in rows:
        item = dict(row)

        if not item.get("grade"):
            item["grade"] = _grade_from_eqe(
                item.get("eqe")
            )

        output.append(item)

    return output


# ------------------------------------------------------------
# User-selected minimum grade
# ------------------------------------------------------------

def _valid_min_grade(value):
    if value is None:
        return "B"

    value = str(value).upper().strip()

    if value not in GRADE_ORDER:
        return "B"

    return value


def _grade_allowed(grade, minimum_grade):
    if not grade:
        return False

    grade = str(grade).upper().strip()
    minimum_grade = _valid_min_grade(minimum_grade)

    if grade not in GRADE_ORDER:
        return False

    return (
        GRADE_ORDER[grade]
        >= GRADE_ORDER[minimum_grade]
    )


# ------------------------------------------------------------
# Scanner pipeline
# ------------------------------------------------------------

def build_discovery_pipeline(
    market=None,
    symbol=None,
    timeframe=None,
    minimum_grade="B",
):
    minimum_grade = _valid_min_grade(
        minimum_grade
    )

    scanner = _execute_existing_discovery_engine(
        "scanner",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "minimum_grade": minimum_grade,
        },
    )

    raw_rows = _extract_discovery_rows(
        scanner.get("result")
    )

    rows = [
        _normalize_discovery_row(
            row,
            index=i,
        )
        for i, row in enumerate(raw_rows)
    ]

    rows = _apply_grade_if_missing(rows)

    for row in rows:
        row["meets_minimum_grade"] = _grade_allowed(
            row.get("grade"),
            minimum_grade,
        )

    # If the existing scanner returned nothing, inspect the
    # opportunity engine rather than fabricating rows.
    if not rows:
        opportunity = _execute_existing_discovery_engine(
            "opportunity",
            symbol=symbol,
            market=market,
            timeframe=timeframe,
            payload={
                "minimum_grade": minimum_grade,
            },
        )

        raw_rows = _extract_discovery_rows(
            opportunity.get("result")
        )

        rows = [
            _normalize_discovery_row(
                row,
                index=i,
            )
            for i, row in enumerate(raw_rows)
        ]

        rows = _apply_grade_if_missing(rows)

        for row in rows:
            row["meets_minimum_grade"] = _grade_allowed(
                row.get("grade"),
                minimum_grade,
            )

    # Ranking is delegated to existing backend where possible.
    ranking = _execute_existing_discovery_engine(
        "ranking",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "rows": rows,
            "opportunities": rows,
            "minimum_grade": minimum_grade,
        },
    )

    ranked_rows = _extract_discovery_rows(
        ranking.get("result")
    )

    if ranked_rows:
        rows = [
            _normalize_discovery_row(
                row,
                index=i,
            )
            for i, row in enumerate(ranked_rows)
        ]

        rows = _apply_grade_if_missing(rows)

        for row in rows:
            row["meets_minimum_grade"] = _grade_allowed(
                row.get("grade"),
                minimum_grade,
            )

    # Top10 is also an existing owner.
    top10 = _execute_existing_discovery_engine(
        "top10",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "rows": rows,
            "opportunities": rows,
            "minimum_grade": minimum_grade,
        },
    )

    top10_rows = _extract_discovery_rows(
        top10.get("result")
    )

    if top10_rows:
        top10_normalized = [
            _normalize_discovery_row(
                row,
                index=i,
            )
            for i, row in enumerate(top10_rows)
        ]

        top10_normalized = _apply_grade_if_missing(
            top10_normalized
        )

        for row in top10_normalized:
            row["meets_minimum_grade"] = _grade_allowed(
                row.get("grade"),
                minimum_grade,
            )

        rows = top10_normalized

    return {
        "status": "READY" if rows else "NO_DATA",
        "minimum_grade": minimum_grade,
        "count": len(rows),
        "rows": rows[:10],
        "engines": {
            "scanner": scanner,
            "ranking": ranking,
            "top10": top10,
        },
    }


# ------------------------------------------------------------
# Discovery backend map
# ------------------------------------------------------------

@app.get("/api/discovery/engines")
def api_discovery_engines():
    result = {}

    for kind, modules in _DISCOVERY_ENGINE_CANDIDATES.items():
        result[kind] = [
            _module_runtime_info(module_name)
            for module_name in modules
        ]

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "engines": result,
        })
    )


# ------------------------------------------------------------
# Main Discovery endpoint
# ------------------------------------------------------------

@app.get("/api/discovery")
def api_discovery(
    market: str = None,
    symbol: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    try:
        result = build_discovery_pipeline(
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            minimum_grade=minimum_grade,
        )

        return JSONResponse(
            content=json_safe(result)
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=json_safe({
                "status": "ERROR",
                "error": str(exc),
                "count": 0,
                "rows": [],
            }),
        )


# ------------------------------------------------------------
# Discovery / Scanner explicit endpoints
# ------------------------------------------------------------

@app.get("/api/discovery/scanner")
def api_discovery_scanner(
    market: str = None,
    symbol: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    result = _execute_existing_discovery_engine(
        "scanner",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "minimum_grade": _valid_min_grade(
                minimum_grade
            )
        },
    )

    return JSONResponse(
        content=json_safe(result)
    )


@app.get("/api/discovery/opportunities")
def api_discovery_opportunities(
    market: str = None,
    symbol: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    result = _execute_existing_discovery_engine(
        "opportunity",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "minimum_grade": _valid_min_grade(
                minimum_grade
            )
        },
    )

    return JSONResponse(
        content=json_safe(result)
    )


@app.get("/api/discovery/top10")
def api_discovery_top10(
    market: str = None,
    symbol: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    pipeline = build_discovery_pipeline(
        market=market,
        symbol=symbol,
        timeframe=timeframe,
        minimum_grade=minimum_grade,
    )

    return JSONResponse(
        content=json_safe({
            "status": pipeline.get("status"),
            "minimum_grade": pipeline.get(
                "minimum_grade"
            ),
            "count": min(
                10,
                len(pipeline.get("rows", [])),
            ),
            "top10": pipeline.get("rows", [])[:10],
        })
    )


# ------------------------------------------------------------
# Discovery asset detail
# ------------------------------------------------------------

@app.get("/api/discovery/asset")
def api_discovery_asset(
    symbol: str,
    market: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    """
    Asset detail is assembled through the existing backend
    pipeline.

    It does not manufacture a Buy/Sell result.
    """
    terminal = build_terminal_intelligence(
        symbol
    )

    discovery = build_discovery_pipeline(
        market=market,
        symbol=symbol,
        timeframe=timeframe,
        minimum_grade=minimum_grade,
    )

    selected = None

    for row in discovery.get("rows", []):
        if str(row.get("symbol", "")).upper() == str(
            symbol
        ).upper():
            selected = row
            break

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "symbol": symbol,
            "discovery": selected,
            "terminal": terminal,
            "minimum_grade": _valid_min_grade(
                minimum_grade
            ),
        })
    )


# ------------------------------------------------------------
# Opportunity explanation
# ------------------------------------------------------------

@app.get("/api/discovery/explain")
def api_discovery_explain(
    symbol: str,
    market: str = None,
    timeframe: str = "1m",
):
    result = _execute_existing_discovery_engine(
        "explainer",
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload={
            "symbol": symbol,
            "market": market,
            "timeframe": timeframe,
        },
    )

    return JSONResponse(
        content=json_safe(result)
    )


# ------------------------------------------------------------
# Timing / liquidity / risk discovery gates
# ------------------------------------------------------------

@app.get("/api/discovery/gates")
def api_discovery_gates(
    symbol: str,
    market: str = None,
    timeframe: str = "1m",
):
    result = {}

    for kind in (
        "universe",
        "liquidity",
        "risk",
        "timing",
        "intraday",
    ):
        result[kind] = _execute_existing_discovery_engine(
            kind,
            symbol=symbol,
            market=market,
            timeframe=timeframe,
            payload={
                "symbol": symbol,
                "market": market,
                "timeframe": timeframe,
            },
        )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "symbol": symbol,
            "gates": result,
        })
    )


# ------------------------------------------------------------
# Favorites
# ------------------------------------------------------------

@app.get("/api/discovery/favorites")
def api_discovery_favorites(
    symbol: str = None,
    action: str = "list",
):
    result = _execute_existing_discovery_engine(
        "favorites",
        symbol=symbol,
        payload={
            "symbol": symbol,
            "action": action,
        },
    )

    return JSONResponse(
        content=json_safe(result)
    )


# ------------------------------------------------------------
# Scanner research/provenance endpoint
# ------------------------------------------------------------

@app.get("/api/discovery/provenance")
def api_discovery_provenance():
    """
    Gives the frontend the real backend ownership map.

    This is intentionally separate from opportunity values so
    the UI can show which existing engine supplied each layer.
    """
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "pipeline": [
                "MARKET_DATA",
                "EVIDENCE",
                "STRUCTURE",
                "ACCUMULATION_DISTRIBUTION",
                "BOUNDARY",
                "BREAKOUT_PROBABILITY",
                "RANKING",
                "PROFIT_CONVERSION",
                "TOP10",
            ],
            "owners": _DISCOVERY_ENGINE_CANDIDATES,
            "decision_boundary": (
                "SCANNER_IS_DISCOVERY_ONLY"
            ),
            "execution_boundary": (
                "DECISION -> RISK -> CAS -> AUTHORIZED_ACTION"
            ),
        })
    )


# ------------------------------------------------------------
# Discovery health
# ------------------------------------------------------------

@app.get("/api/discovery/health")
def api_discovery_health():
    health = {}

    for kind, modules in _DISCOVERY_ENGINE_CANDIDATES.items():
        module_results = []

        for module_name in modules:
            info = _module_runtime_info(
                module_name
            )

            module_results.append(info)

        health[kind] = module_results

    available = 0
    total = 0

    for values in health.values():
        for item in values:
            total += 1

            if item.get("available"):
                available += 1

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if available
                else "NO_ENGINE_AVAILABLE"
            ),
            "available_modules": available,
            "checked_modules": total,
            "engines": health,
        })
    )


# ============================================================
# END PART 3
# ============================================================
# ============================================================
# ROBOMLM_PLUS serve.py
# PART 4 / 5
# BUYER -> STRATEGY -> INTELLIGENCE -> DECISION
# -> RISK -> CAS -> PLUS / AUTOROBOMLM
#
# IMPORTANT:
# - Existing engines remain the owners of calculations.
# - This layer is an application/API bridge only.
# - No duplicate D13.
# - No duplicate Risk engine.
# - No duplicate CAS gates.
# - No direct broker order from Buyer.
# - ANALYSIS != EXECUTION.
# ============================================================


# ------------------------------------------------------------
# BUYER BACKEND OWNERS
# ------------------------------------------------------------

_BUYER_ENGINE_CANDIDATES = {
    "strategy": [
        "app.intelligence.strategy_intelligence",
    ],
    "intelligence": [
        "app.intelligence.intelligence_orchestrator",
        "app.intelligence.opportunity_intelligence",
        "app.intelligence.regime_intelligence",
        "app.intelligence.relationship_intelligence",
        "app.intelligence.magnitude_engine",
        "app.intelligence.confidence_engine",
        "app.intelligence.commitment_engine",
        "app.intelligence.timing_intelligence",
        "app.intelligence.strategy_intelligence",
    ],
    "decision": [
        "app.intelligence.decision_orchestrator",
        "app.intelligence.decision.decision_state",
        "app.intelligence.decision.decision_explainer",
        "app.intelligence.decision.13_decision_decision",
    ],
    "risk": [
        "app.intelligence.risk",
        "app.intelligence.decision.risk_engine",
        "app.intelligence.cas.risk_gate",
    ],
    "cas": [
        "app.intelligence.cas.cas_orchestrator",
    ],
    "suitability": [
        "app.intelligence.cas.suitability_gate",
    ],
    "exposure": [
        "app.intelligence.cas.exposure_gate",
    ],
    "position": [
        "app.intelligence.cas.position_gate",
    ],
    "execution_safety": [
        "app.intelligence.cas.execution_safety_gate",
    ],
    "compliance": [
        "app.intelligence.cas.compliance_gate",
    ],
    "restriction": [
        "app.intelligence.cas.restriction_engine",
    ],
    "plus": [
        "app.intelligence.robomlm_plus.plus_orchestrator",
        "app.intelligence.robomlm_plus.advanced_decision",
        "app.intelligence.robomlm_plus.execution_preparation",
        "app.intelligence.robomlm_plus.position_monitor",
        "app.intelligence.robomlm_plus.protection",
        "app.intelligence.robomlm_plus.reconciliation",
        "app.intelligence.robomlm_plus.emergency_control",
        "app.intelligence.robomlm_plus.halt_controller",
    ],
    "autorobomlm": [
        "app.autorobimlm.automation_engine",
        "app.autorobimlm.mode_manager",
        "app.autorobimlm.strategy_runner",
        "app.autorobimlm.execution.order_manager",
        "app.autorobimlm.execution.execution_manager",
        "app.autorobimlm.kill_switch",
        "app.autorobimlm.reconciliation",
    ],
}


# ------------------------------------------------------------
# BUYER MARKET / INSTRUMENT / CONTRACT / STRATEGY
# ------------------------------------------------------------

_BUYER_MARKETS = [
    "EQUITY",
    "INDEX",
    "CRYPTO",
    "FX",
    "COMMODITY",
    "FUTURES",
]

_BUYER_INSTRUMENTS = {
    "EQUITY": [
        "STOCK",
        "ETF",
    ],
    "INDEX": [
        "INDEX",
        "INDEX_FUTURE",
        "INDEX_OPTION",
    ],
    "CRYPTO": [
        "SPOT",
        "PERPETUAL",
        "FUTURE",
        "OPTION",
    ],
    "FX": [
        "SPOT",
        "FUTURE",
        "OPTION",
    ],
    "COMMODITY": [
        "SPOT",
        "FUTURE",
        "OPTION",
    ],
    "FUTURES": [
        "FUTURE",
        "OPTION",
    ],
}

_BUYER_CONTRACTS = {
    "SPOT": ["SPOT"],
    "STOCK": ["CASH_EQUITY"],
    "ETF": ["ETF"],
    "INDEX": ["INDEX"],
    "INDEX_FUTURE": ["FUTURE"],
    "INDEX_OPTION": [
        "ATM",
        "ITM",
        "OTM",
    ],
    "PERPETUAL": ["PERPETUAL"],
    "FUTURE": ["FUTURE"],
    "OPTION": [
        "ATM",
        "ITM",
        "OTM",
    ],
    "CASH_EQUITY": ["CASH_EQUITY"],
}


def _buyer_normalize_market(value):
    if value is None:
        return ""

    value = str(value).upper().strip()

    aliases = {
        "STOCK": "EQUITY",
        "STOCKS": "EQUITY",
        "EQUITIES": "EQUITY",
        "INDEXES": "INDEX",
        "INDICES": "INDEX",
        "CRYPTOCURRENCY": "CRYPTO",
        "CRYPTOS": "CRYPTO",
        "COMMODITIES": "COMMODITY",
    }

    return aliases.get(value, value)


def _buyer_validate_selection(
    market,
    instrument,
    contract,
    strategy,
):
    market = _buyer_normalize_market(market)

    errors = []

    if market not in _BUYER_MARKETS:
        errors.append("INVALID_MARKET")

    allowed_instruments = _BUYER_INSTRUMENTS.get(
        market,
        [],
    )

    if instrument:
        instrument_upper = str(
            instrument
        ).upper().strip()

        if (
            allowed_instruments
            and instrument_upper
            not in allowed_instruments
        ):
            errors.append("INVALID_INSTRUMENT")
    else:
        instrument_upper = ""

    if contract:
        contract_upper = str(
            contract
        ).upper().strip()

        allowed_contracts = _BUYER_CONTRACTS.get(
            instrument_upper,
            [],
        )

        if (
            allowed_contracts
            and contract_upper
            not in allowed_contracts
        ):
            errors.append("INVALID_CONTRACT")
    else:
        contract_upper = ""

    if not strategy:
        errors.append("STRATEGY_REQUIRED")

    return {
        "valid": not errors,
        "errors": errors,
        "market": market,
        "instrument": instrument_upper,
        "contract": contract_upper,
        "strategy": (
            str(strategy).upper().strip()
            if strategy
            else ""
        ),
    }


# ------------------------------------------------------------
# BUYER STRATEGY LIST
# ------------------------------------------------------------

@app.get("/api/buyer/markets")
def api_buyer_markets():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "markets": _BUYER_MARKETS,
            "instruments": _BUYER_INSTRUMENTS,
            "contracts": _BUYER_CONTRACTS,
        })
    )


@app.get("/api/buyer/strategies")
def api_buyer_strategies():
    """
    Preserve the existing strategy registry when it exists.
    """
    existing = globals().get(
        "_BUYER_STRATEGIES",
        None,
    )

    if existing is not None:
        return JSONResponse(
            content=json_safe({
                "status": "READY",
                "strategies": existing,
            })
        )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "strategies": [],
            "source": "NO_STATIC_STRATEGY_REGISTRY",
        })
    )


# ------------------------------------------------------------
# BUYER REQUEST NORMALIZATION
# ------------------------------------------------------------

def _buyer_request_payload(
    symbol,
    market,
    instrument,
    contract,
    strategy,
    timeframe="1m",
    mode="ANALYSIS",
    metadata=None,
):
    return {
        "symbol": symbol,
        "market": _buyer_normalize_market(
            market
        ),
        "instrument": (
            str(instrument).upper().strip()
            if instrument
            else ""
        ),
        "contract": (
            str(contract).upper().strip()
            if contract
            else ""
        ),
        "strategy": (
            str(strategy).upper().strip()
            if strategy
            else ""
        ),
        "timeframe": timeframe,
        "mode": (
            str(mode).upper().strip()
            if mode
            else "ANALYSIS"
        ),
        "metadata": metadata or {},
    }


# ------------------------------------------------------------
# BUYER BACKEND INVOCATION
# ------------------------------------------------------------

_BUYER_METHOD_NAMES = (
    "analyze",
    "analyse",
    "evaluate",
    "process",
    "run",
    "execute_analysis",
    "build",
    "orchestrate",
)


def _buyer_engine_call(
    kind,
    payload,
):
    """
    Existing-owner invocation.

    The function first imports the actual existing module.
    It never creates a replacement engine.
    """
    modules = _BUYER_ENGINE_CANDIDATES.get(
        kind,
        [],
    )

    for module_name in modules:
        module = _safe_import_module(
            module_name
        )

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _BUYER_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, info = _call_with_supported_kwargs(
            fn,
            payload,
        )

        if info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_EXISTING_BUYER_ENTRYPOINT",
        },
    }


# ------------------------------------------------------------
# BUYER OUTPUT NORMALIZATION
# ------------------------------------------------------------

def _buyer_extract(raw, *keys):
    if raw is None:
        return None

    if isinstance(raw, dict):
        for key in keys:
            if key in raw:
                return raw[key]

        # Nested common result containers.
        for container_key in (
            "result",
            "output",
            "data",
            "analysis",
            "decision",
            "intelligence",
        ):
            nested = raw.get(
                container_key
            )

            if isinstance(nested, dict):
                for key in keys:
                    if key in nested:
                        return nested[key]

    else:
        for key in keys:
            try:
                value = getattr(
                    raw,
                    key,
                    None,
                )

                if value is not None:
                    return value
            except Exception:
                continue

    return None


def _buyer_normalize_intelligence(raw):
    return {
        "status": (
            str(
                _buyer_extract(
                    raw,
                    "status",
                    "state",
                )
                or "UNKNOWN"
            ).upper()
        ),
        "score": _number(
            _buyer_extract(
                raw,
                "intelligence_score",
                "score",
            ),
            None,
        ),
        "confidence": _number(
            _buyer_extract(
                raw,
                "confidence",
                "confidence_score",
            ),
            None,
        ),
        "magnitude": _number(
            _buyer_extract(
                raw,
                "magnitude",
                "magnitude_score",
            ),
            None,
        ),
        "commitment": _number(
            _buyer_extract(
                raw,
                "commitment",
                "commitment_score",
            ),
            None,
        ),
        "timing": _buyer_extract(
            raw,
            "timing",
            "timing_status",
            "timing_score",
        ),
        "regime": _buyer_extract(
            raw,
            "regime",
            "regime_state",
        ),
        "relationship": _buyer_extract(
            raw,
            "relationship",
            "relationship_state",
        ),
        "raw": json_safe(raw),
    }


def _buyer_normalize_decision(raw):
    decision = _buyer_extract(
        raw,
        "decision",
        "action",
    )

    direction = _buyer_extract(
        raw,
        "direction",
        "side",
    )

    approved = _buyer_extract(
        raw,
        "approved",
        "is_approved",
    )

    score = _buyer_extract(
        raw,
        "decision_score",
        "score",
    )

    confidence = _buyer_extract(
        raw,
        "confidence",
        "confidence_score",
    )

    return {
        "decision": (
            str(decision).upper()
            if decision is not None
            else "UNKNOWN"
        ),
        "direction": (
            str(direction).upper()
            if direction is not None
            else "HOLD"
        ),
        "approved": (
            _bool(approved, False)
            if approved is not None
            else False
        ),
        "decision_score": _number(
            score,
            None,
        ),
        "confidence": _number(
            confidence,
            None,
        ),
        "raw": json_safe(raw),
    }


def _buyer_normalize_risk(raw):
    return {
        "status": (
            str(
                _buyer_extract(
                    raw,
                    "status",
                    "state",
                    "risk_status",
                )
                or "UNKNOWN"
            ).upper()
        ),
        "approved": _bool(
            _buyer_extract(
                raw,
                "approved",
                "allowed",
                "passed",
            ),
            False,
        ),
        "risk_score": _number(
            _buyer_extract(
                raw,
                "risk_score",
                "score",
            ),
            None,
        ),
        "risk_level": _buyer_extract(
            raw,
            "risk_level",
            "level",
        ),
        "reasons": _buyer_extract(
            raw,
            "reasons",
            "gate_reasons",
            "errors",
        ) or [],
        "raw": json_safe(raw),
    }


def _buyer_normalize_cas(raw):
    status = _buyer_extract(
        raw,
        "status",
        "decision",
        "authorization",
    )

    return {
        "status": (
            str(status).upper()
            if status is not None
            else "UNKNOWN"
        ),
        "allowed": _bool(
            _buyer_extract(
                raw,
                "allowed",
                "approved",
                "authorized",
            ),
            False,
        ),
        "restriction": _buyer_extract(
            raw,
            "restriction",
            "restrictions",
        ),
        "gate_reasons": _buyer_extract(
            raw,
            "gate_reasons",
            "reasons",
            "errors",
        ) or [],
        "raw": json_safe(raw),
    }


# ------------------------------------------------------------
# BUYER PIPELINE
# ------------------------------------------------------------

def build_buyer_pipeline(
    symbol,
    market,
    instrument,
    contract,
    strategy,
    timeframe="1m",
    mode="ANALYSIS",
    metadata=None,
):
    selection = _buyer_validate_selection(
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
    )

    if not selection["valid"]:
        return {
            "status": "INVALID_REQUEST",
            "selection": selection,
            "pipeline": {},
        }

    payload = _buyer_request_payload(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode=mode,
        metadata=metadata,
    )

    # --------------------------------------------------------
    # 1. STRATEGY
    # --------------------------------------------------------

    strategy_result = _buyer_engine_call(
        "strategy",
        payload,
    )

    # --------------------------------------------------------
    # 2. INTELLIGENCE
    # --------------------------------------------------------

    intelligence_payload = dict(payload)

    intelligence_payload.update({
        "strategy_result": (
            strategy_result.get("result")
        ),
    })

    intelligence_result = _buyer_engine_call(
        "intelligence",
        intelligence_payload,
    )

    intelligence = (
        _buyer_normalize_intelligence(
            intelligence_result.get("result")
        )
    )

    # --------------------------------------------------------
    # 3. DECISION
    #
    # D13 remains the decision owner.
    # No local score formula is created here.
    # --------------------------------------------------------

    decision_payload = dict(payload)

    decision_payload.update({
        "strategy_result": (
            strategy_result.get("result")
        ),
        "intelligence_result": (
            intelligence_result.get("result")
        ),
    })

    decision_result = _buyer_engine_call(
        "decision",
        decision_payload,
    )

    decision = _buyer_normalize_decision(
        decision_result.get("result")
    )

    # --------------------------------------------------------
    # 4. RISK
    #
    # Risk only receives the decision/intelligence context.
    # --------------------------------------------------------

    risk_payload = dict(payload)

    risk_payload.update({
        "strategy_result": (
            strategy_result.get("result")
        ),
        "intelligence_result": (
            intelligence_result.get("result")
        ),
        "decision_result": (
            decision_result.get("result")
        ),
    })

    risk_result = _buyer_engine_call(
        "risk",
        risk_payload,
    )

    risk = _buyer_normalize_risk(
        risk_result.get("result")
    )

    # --------------------------------------------------------
    # 5. CAS
    #
    # CAS is the authorization boundary.
    # --------------------------------------------------------

    cas_payload = dict(payload)

    cas_payload.update({
        "strategy_result": (
            strategy_result.get("result")
        ),
        "intelligence_result": (
            intelligence_result.get("result")
        ),
        "decision_result": (
            decision_result.get("result")
        ),
        "risk_result": (
            risk_result.get("result")
        ),
    })

    cas_result = _buyer_engine_call(
        "cas",
        cas_payload,
    )

    cas = _buyer_normalize_cas(
        cas_result.get("result")
    )

    # --------------------------------------------------------
    # 6. PLUS
    #
    # PLUS is exposed only after CAS.
    # --------------------------------------------------------

    plus = {
        "status": "NOT_AUTHORIZED",
        "available": False,
        "executed": False,
        "result": None,
    }

    cas_allows_plus = (
        cas.get("allowed") is True
        and str(
            cas.get("status", "")
        ).upper()
        in (
            "ALLOW",
            "ALLOW_WITH_RESTRICTION",
            "APPROVED",
            "AUTHORIZED",
        )
    )

    if cas_allows_plus:
        plus_payload = dict(
            cas_payload
        )

        plus_payload["cas_result"] = (
            cas_result.get("result")
        )

        plus = _buyer_engine_call(
            "plus",
            plus_payload,
        )

        if not plus.get("available"):
            plus["status"] = (
                "CAS_ALLOWED_PLUS_UNAVAILABLE"
            )

    # --------------------------------------------------------
    # 7. AUTOROBOMLM
    #
    # NEVER call it unless CAS has authorized.
    #
    # ANALYSIS/SIMULATION remain non-execution modes.
    # --------------------------------------------------------

    autorobomlm = {
        "status": "NOT_AUTHORIZED",
        "available": False,
        "executed": False,
        "result": None,
    }

    execution_mode = str(
        mode or "ANALYSIS"
    ).upper()

    execution_requested = (
        execution_mode
        in (
            "AUTHORIZED_EXECUTION",
            "EXECUTION",
            "LIVE",
            "DEMO",
            "PAPER",
        )
    )

    if cas_allows_plus and execution_requested:
        auto_payload = dict(
            cas_payload
        )

        auto_payload.update({
            "cas_result": (
                cas_result.get("result")
            ),
            "plus_result": (
                plus.get("result")
            ),
            "execution_mode": execution_mode,
        })

        autorobomlm = _buyer_engine_call(
            "autorobomlm",
            auto_payload,
        )

    elif cas_allows_plus:
        autorobomlm["status"] = (
            "ANALYSIS_ONLY"
        )

    # --------------------------------------------------------
    # FINAL BUYER RESULT
    # --------------------------------------------------------

    return {
        "status": "READY",
        "symbol": symbol,
        "selection": selection,
        "mode": execution_mode,

        "pipeline": {
            "strategy": strategy_result,
            "intelligence": intelligence_result,
            "decision": decision_result,
            "risk": risk_result,
            "cas": cas_result,
            "plus": plus,
            "autorobomlm": autorobomlm,
        },

        "normalized": {
            "strategy": json_safe(
                strategy_result.get(
                    "result"
                )
            ),
            "intelligence": intelligence,
            "decision": decision,
            "risk": risk,
            "cas": cas,
        },

        "authorization": {
            "cas_allowed": cas_allows_plus,
            "execution_requested": (
                execution_requested
            ),
            "autorobomlm_invoked": (
                autorobomlm.get(
                    "executed",
                    False,
                )
            ),
        },

        "lifecycle": [
            "BUYER_REQUEST",
            "MARKET",
            "INSTRUMENT",
            "CONTRACT",
            "STRATEGY",
            "INTELLIGENCE",
            "DECISION",
            "RISK",
            "CAS",
            "PLUS",
            "AUTOROBOMLM",
        ],
    }


# ------------------------------------------------------------
# EXISTING BUYER ANALYZE ENDPOINT
# ------------------------------------------------------------

# NOTE:
# If Part 1â€“3 already contains an older /api/buyer/analyze
# implementation, this definition intentionally becomes the
# active definition in the final assembled serve.py.

if "BuyerAnalyzeRequest" not in globals():

    class BuyerAnalyzeRequest(BaseModel):
        symbol: str
        market: str
        instrument: str
        contract: str
        strategy: str
        timeframe: str = "1m"
        mode: str = "ANALYSIS"
        metadata: dict = {}


@app.post("/api/buyer/analyze")
def api_buyer_analyze(
    request: BuyerAnalyzeRequest,
):
    try:
        result = build_buyer_pipeline(
            symbol=request.symbol,
            market=request.market,
            instrument=request.instrument,
            contract=request.contract,
            strategy=request.strategy,
            timeframe=request.timeframe,
            mode=request.mode,
            metadata=request.metadata,
        )

        return JSONResponse(
            content=json_safe(result)
        )

    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content=json_safe({
                "status": "ERROR",
                "error": str(exc),
                "symbol": getattr(
                    request,
                    "symbol",
                    "",
                ),
            }),
        )


# ------------------------------------------------------------
# BUYER PIPELINE DETAIL
# ------------------------------------------------------------

@app.get("/api/buyer/pipeline")
def api_buyer_pipeline(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
    mode: str = "ANALYSIS",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode=mode,
    )

    return JSONResponse(
        content=json_safe(result)
    )


# ------------------------------------------------------------
# BUYER DECISION ONLY
# ------------------------------------------------------------

@app.get("/api/buyer/decision")
def api_buyer_decision(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode="ANALYSIS",
    )

    return JSONResponse(
        content=json_safe({
            "status": result.get(
                "status"
            ),
            "symbol": symbol,
            "decision": result.get(
                "normalized",
                {},
            ).get(
                "decision",
                {},
            ),
            "intelligence": result.get(
                "normalized",
                {},
            ).get(
                "intelligence",
                {},
            ),
        })
    )


# ------------------------------------------------------------
# BUYER RISK
# ------------------------------------------------------------

@app.get("/api/buyer/risk")
def api_buyer_risk(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode="ANALYSIS",
    )

    return JSONResponse(
        content=json_safe({
            "status": result.get(
                "status"
            ),
            "symbol": symbol,
            "risk": result.get(
                "normalized",
                {},
            ).get(
                "risk",
                {},
            ),
        })
    )


# ------------------------------------------------------------
# BUYER CAS
# ------------------------------------------------------------

@app.get("/api/buyer/cas")
def api_buyer_cas(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode="ANALYSIS",
    )

    return JSONResponse(
        content=json_safe({
            "status": result.get(
                "status"
            ),
            "symbol": symbol,
            "cas": result.get(
                "normalized",
                {},
            ).get(
                "cas",
                {},
            ),
            "authorization": result.get(
                "authorization",
                {},
            ),
        })
    )


# ------------------------------------------------------------
# CAS GATE DETAIL
# ------------------------------------------------------------

@app.get("/api/buyer/cas/gates")
def api_buyer_cas_gates(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
):
    payload = _buyer_request_payload(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode="ANALYSIS",
    )

    gate_results = {}

    for gate in (
        "suitability",
        "risk",
        "exposure",
        "position",
        "execution_safety",
        "compliance",
        "restriction",
    ):
        gate_results[gate] = (
            _buyer_engine_call(
                gate,
                payload,
            )
        )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "symbol": symbol,
            "gates": gate_results,
        })
    )


# ------------------------------------------------------------
# PLUS STATUS
# ------------------------------------------------------------

@app.get("/api/buyer/plus")
def api_buyer_plus(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode="ANALYSIS",
    )

    plus = result.get(
        "pipeline",
        {},
    ).get(
        "plus",
        {},
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "symbol": symbol,
            "plus": plus,
            "authorization": result.get(
                "authorization",
                {},
            ),
        })
    )


# ------------------------------------------------------------
# AUTOROBOMLM STATUS
# ------------------------------------------------------------

@app.get("/api/buyer/autorobomlm")
def api_buyer_autorobomlm(
    symbol: str,
    market: str,
    instrument: str,
    contract: str,
    strategy: str,
    timeframe: str = "1m",
    mode: str = "ANALYSIS",
):
    result = build_buyer_pipeline(
        symbol=symbol,
        market=market,
        instrument=instrument,
        contract=contract,
        strategy=strategy,
        timeframe=timeframe,
        mode=mode,
    )

    auto = result.get(
        "pipeline",
        {},
    ).get(
        "autorobomlm",
        {},
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "symbol": symbol,
            "mode": mode,
            "autorobomlm": auto,
            "authorization": result.get(
                "authorization",
                {},
            ),
        })
    )


# ------------------------------------------------------------
# BUYER OWNERSHIP MAP
# ------------------------------------------------------------

@app.get("/api/buyer/backend-map")
def api_buyer_backend_map():
    return JSONResponse(
        content=json_safe({
            "status": "READY",

            "flow": [
                "BUYER",
                "MARKET",
                "INSTRUMENT",
                "CONTRACT",
                "STRATEGY",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
                "PLUS",
                "AUTOROBOMLM",
            ],

            "owners": _BUYER_ENGINE_CANDIDATES,

            "execution_boundary": {
                "analysis": (
                    "NO_EXECUTION"
                ),
                "simulation": (
                    "NO_LIVE_EXECUTION"
                ),
                "authorized_execution": (
                    "CAS_REQUIRED"
                ),
            },

            "cas_gates": [
                "SUITABILITY",
                "RISK",
                "EXPOSURE",
                "POSITION",
                "EXECUTION_SAFETY",
                "COMPLIANCE",
                "RESTRICTIONS",
            ],
        })
    )


# ------------------------------------------------------------
# BUYER RUNTIME HEALTH
# ------------------------------------------------------------

@app.get("/api/buyer/health")
def api_buyer_health():
    health = {}

    for kind, modules in (
        _BUYER_ENGINE_CANDIDATES.items()
    ):
        health[kind] = []

        for module_name in modules:
            health[kind].append(
                _module_runtime_info(
                    module_name
                )
            )

    available = 0
    checked = 0

    for values in health.values():
        for item in values:
            checked += 1

            if item.get("available"):
                available += 1

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if available
                else "NO_ENGINE_AVAILABLE"
            ),
            "available_modules": available,
            "checked_modules": checked,
            "owners": health,
        })
    )


# ============================================================
# BUYER SAFETY INVARIANTS
# ============================================================

_BUYER_SAFETY_INVARIANTS = {
    "decision_owner": (
        "EXISTING_D13_DECISION_ENGINE"
    ),
    "risk_owner": (
        "EXISTING_RISK_ENGINE"
    ),
    "cas_owner": (
        "EXISTING_CAS_ORCHESTRATOR"
    ),
    "execution_owner": (
        "EXISTING_AUTOROBOMLM_EXECUTION_STACK"
    ),
    "scanner_boundary": (
        "DISCOVERY_ONLY"
    ),
    "buyer_analysis": (
        "DOES_NOT_EQUAL_EXECUTION"
    ),
    "cas_bypass": False,
    "direct_broker_order_from_buyer": False,
    "duplicate_decision_formula": False,
    "duplicate_risk_formula": False,
    "duplicate_cas_formula": False,
}


@app.get("/api/buyer/invariants")
def api_buyer_invariants():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "invariants": (
                _BUYER_SAFETY_INVARIANTS
            ),
        })
    )


# ============================================================
# END PART 4 / 5
# ============================================================
# ============================================================
# ROBOMLM_PLUS serve.py
# PART 5 / 5
#
# MEMORY + RESEARCH + AUTOMATION + ACCOUNT
# + BLACKBOX + EXECUTION VISIBILITY
# + FINAL SYSTEM BACKEND MAP / HEALTH
#
# FINAL PIPELINE VISIBILITY:
#
# DATA
#  -> EVIDENCE
#  -> CONTEXT
#  -> INTELLIGENCE
#  -> DECISION
#  -> RISK
#  -> CAS
#  -> ACTION
#  -> EXECUTION
#  -> RESULT
#  -> MEMORY / LEARNING
#  -> RESEARCH
#
# Existing backend engines remain owners.
# This file exposes them to the existing frontend.
# ============================================================


# ------------------------------------------------------------
# REMAINING BACKEND OWNERS
# ------------------------------------------------------------

_REMAINING_BACKEND_CANDIDATES = {
    "memory": [
        "app.intelligence.memory.memory_service",
        "app.intelligence.memory.memory_retrieval",
        "app.intelligence.memory.decision_memory",
        "app.intelligence.memory.evidence_memory",
        "app.intelligence.memory.market_memory",
        "app.intelligence.memory.outcome_memory",
        "app.intelligence.memory.pattern_memory",
    ],

    "research": [
        "app.intelligence.research.research_service",
        "app.intelligence.research.experiment",
        "app.intelligence.research.hypothesis",
        "app.intelligence.research.validation",
        "app.intelligence.research.stress_testing",
        "app.intelligence.research.candidate_manager",
        "app.intelligence.research.version_manager",
        "app.intelligence.research.deployment_manager",
        "app.intelligence.research.dataset",
    ],

    "automation": [
        "app.autorobimlm.automation_engine",
        "app.autorobimlm.mode_manager",
        "app.autorobimlm.strategy_runner",
    ],

    "execution": [
        "app.autorobimlm.execution.order_manager",
        "app.autorobimlm.execution.execution_manager",
        "app.autorobimlm.positions",
        "app.autorobimlm.reconciliation",
    ],

    "risk": [
        "app.autorobimlm.risk",
        "app.intelligence.cas.risk_gate",
    ],

    "security": [
        "app.core.security",
        "app.auth",
        "app.authorization",
    ],

    "account": [
        "app.users",
        "app.subscription",
        "app.database.models.user",
        "app.database.models.subscription",
    ],

    "blackbox": [
        "app.database.models.audit",
        "app.database.models.decision",
        "app.database.models.evidence",
        "app.database.models.market",
        "app.database.models.trade",
    ],
}


# ------------------------------------------------------------
# GENERIC EXISTING-OWNER STATUS
# ------------------------------------------------------------

def _backend_owner_status(owner_map):
    result = {}

    for domain, modules in owner_map.items():
        result[domain] = []

        for module_name in modules:
            result[domain].append(
                _module_runtime_info(
                    module_name
                )
            )

    return result


# ============================================================
# MEMORY
# ============================================================

_MEMORY_METHOD_NAMES = (
    "retrieve",
    "search",
    "query",
    "get",
    "load",
    "read",
    "record",
    "store",
    "save",
    "remember",
    "recall",
    "run",
    "process",
)


def _memory_call(
    payload,
    preferred=None,
):
    modules = []

    if preferred:
        modules.extend(
            _REMAINING_BACKEND_CANDIDATES.get(
                preferred,
                [],
            )
        )

    if not modules:
        modules.extend(
            _REMAINING_BACKEND_CANDIDATES[
                "memory"
            ]
        )

    for module_name in modules:
        module = _safe_import_module(
            module_name
        )

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _MEMORY_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, info = _call_with_supported_kwargs(
            fn,
            payload,
        )

        if info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_EXISTING_MEMORY_ENTRYPOINT",
        },
    }


def _memory_rows(raw):
    return _extract_discovery_rows(
        raw
    )


@app.get("/api/memory")
def api_memory(
    symbol: str = None,
    limit: int = 50,
):
    limit = max(
        1,
        min(
            int(limit or 50),
            500,
        ),
    )

    payload = {
        "symbol": symbol,
        "limit": limit,
    }

    result = _memory_call(
        payload
    )

    raw = result.get(
        "result"
    )

    rows = _memory_rows(
        raw
    )

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_MEMORY_ENGINE"
            ),
            "symbol": symbol,
            "limit": limit,
            "count": len(rows),
            "rows": rows[:limit],
            "backend": result,
        })
    )


@app.get("/api/memory/search")
def api_memory_search(
    query: str,
    symbol: str = None,
    limit: int = 50,
):
    limit = max(
        1,
        min(
            int(limit or 50),
            500,
        ),
    )

    result = _memory_call({
        "query": query,
        "symbol": symbol,
        "limit": limit,
    })

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_MEMORY_ENGINE"
            ),
            "query": query,
            "symbol": symbol,
            "results": _memory_rows(
                result.get(
                    "result"
                )
            )[:limit],
            "backend": result,
        })
    )


@app.get("/api/memory/decision")
def api_memory_decision(
    symbol: str = None,
    limit: int = 50,
):
    result = _memory_call(
        {
            "symbol": symbol,
            "limit": limit,
            "memory_type": "DECISION",
        },
        preferred="memory",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "memory_type": "DECISION",
            "symbol": symbol,
            "data": result,
        })
    )


@app.get("/api/memory/evidence")
def api_memory_evidence(
    symbol: str = None,
    limit: int = 50,
):
    result = _memory_call(
        {
            "symbol": symbol,
            "limit": limit,
            "memory_type": "EVIDENCE",
        },
        preferred="memory",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "memory_type": "EVIDENCE",
            "symbol": symbol,
            "data": result,
        })
    )


@app.get("/api/memory/outcome")
def api_memory_outcome(
    symbol: str = None,
    limit: int = 50,
):
    result = _memory_call(
        {
            "symbol": symbol,
            "limit": limit,
            "memory_type": "OUTCOME",
        },
        preferred="memory",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "memory_type": "OUTCOME",
            "symbol": symbol,
            "data": result,
        })
    )


@app.get("/api/memory/pattern")
def api_memory_pattern(
    symbol: str = None,
    limit: int = 50,
):
    result = _memory_call(
        {
            "symbol": symbol,
            "limit": limit,
            "memory_type": "PATTERN",
        },
        preferred="memory",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "memory_type": "PATTERN",
            "symbol": symbol,
            "data": result,
        })
    )


@app.get("/api/memory/backend-map")
def api_memory_backend_map():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "owners": {
                "memory": (
                    _REMAINING_BACKEND_CANDIDATES[
                        "memory"
                    ]
                ),
                "decision_memory": [
                    "app.intelligence.memory.decision_memory"
                ],
                "evidence_memory": [
                    "app.intelligence.memory.evidence_memory"
                ],
                "market_memory": [
                    "app.intelligence.memory.market_memory"
                ],
                "outcome_memory": [
                    "app.intelligence.memory.outcome_memory"
                ],
                "pattern_memory": [
                    "app.intelligence.memory.pattern_memory"
                ],
            },
            "learning_chain": [
                "DECISION",
                "OUTCOME",
                "MEMORY",
                "PATTERN",
                "LEARNING",
                "INTELLIGENCE",
            ],
        })
    )


# ============================================================
# RESEARCH
# ============================================================

_RESEARCH_METHOD_NAMES = (
    "research",
    "run_research",
    "run",
    "execute",
    "experiment",
    "validate",
    "stress_test",
    "evaluate",
    "search",
    "create",
    "process",
)


def _research_call(
    kind,
    payload,
):
    modules = _REMAINING_BACKEND_CANDIDATES.get(
        "research",
        [],
    )

    preferred_modules = []

    mapping = {
        "experiment": [
            "app.intelligence.research.experiment",
        ],
        "hypothesis": [
            "app.intelligence.research.hypothesis",
        ],
        "validation": [
            "app.intelligence.research.validation",
        ],
        "stress": [
            "app.intelligence.research.stress_testing",
        ],
        "candidate": [
            "app.intelligence.research.candidate_manager",
        ],
        "version": [
            "app.intelligence.research.version_manager",
        ],
        "deployment": [
            "app.intelligence.research.deployment_manager",
        ],
        "dataset": [
            "app.intelligence.research.dataset",
        ],
        "service": [
            "app.intelligence.research.research_service",
        ],
    }

    preferred_modules.extend(
        mapping.get(
            kind,
            [],
        )
    )

    preferred_modules.extend(
        [
            x
            for x in modules
            if x not in preferred_modules
        ]
    )

    for module_name in preferred_modules:
        module = _safe_import_module(
            module_name
        )

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _RESEARCH_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, info = _call_with_supported_kwargs(
            fn,
            payload,
        )

        if info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_EXISTING_RESEARCH_ENTRYPOINT",
        },
    }


@app.get("/api/research")
def api_research(
    query: str = None,
    symbol: str = None,
    limit: int = 50,
):
    result = _research_call(
        "service",
        {
            "query": query,
            "symbol": symbol,
            "limit": limit,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_RESEARCH_ENGINE"
            ),
            "query": query,
            "symbol": symbol,
            "limit": limit,
            "result": result,
        })
    )


@app.get("/api/research/hypothesis")
def api_research_hypothesis(
    symbol: str = None,
    hypothesis: str = None,
):
    result = _research_call(
        "hypothesis",
        {
            "symbol": symbol,
            "hypothesis": hypothesis,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "HYPOTHESIS",
            "result": result,
        })
    )


@app.get("/api/research/experiment")
def api_research_experiment(
    symbol: str = None,
    hypothesis: str = None,
):
    result = _research_call(
        "experiment",
        {
            "symbol": symbol,
            "hypothesis": hypothesis,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "EXPERIMENT",
            "result": result,
        })
    )


@app.get("/api/research/validation")
def api_research_validation(
    symbol: str = None,
    experiment_id: str = None,
):
    result = _research_call(
        "validation",
        {
            "symbol": symbol,
            "experiment_id": experiment_id,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "VALIDATION",
            "result": result,
        })
    )


@app.get("/api/research/stress")
def api_research_stress(
    symbol: str = None,
    experiment_id: str = None,
):
    result = _research_call(
        "stress",
        {
            "symbol": symbol,
            "experiment_id": experiment_id,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "STRESS_TEST",
            "result": result,
        })
    )


@app.get("/api/research/candidate")
def api_research_candidate(
    candidate_id: str = None,
):
    result = _research_call(
        "candidate",
        {
            "candidate_id": candidate_id,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "CANDIDATE",
            "result": result,
        })
    )


@app.get("/api/research/version")
def api_research_version(
    candidate_id: str = None,
):
    result = _research_call(
        "version",
        {
            "candidate_id": candidate_id,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "VERSION",
            "result": result,
        })
    )


@app.get("/api/research/deployment")
def api_research_deployment(
    candidate_id: str = None,
):
    result = _research_call(
        "deployment",
        {
            "candidate_id": candidate_id,
        },
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "type": "CONTROLLED_DEPLOYMENT",
            "result": result,
        })
    )


@app.get("/api/research/backend-map")
def api_research_backend_map():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "research_lifecycle": [
                "RESEARCH",
                "HYPOTHESIS",
                "EXPERIMENT",
                "VALIDATION",
                "STRESS_TEST",
                "ADMIN_REVIEW",
                "CANDIDATE",
                "VERSION",
                "CONTROLLED_DEPLOYMENT",
            ],
            "owners": (
                _REMAINING_BACKEND_CANDIDATES[
                    "research"
                ]
            ),
            "production_boundary": (
                "RESEARCH_MUST_NOT_DIRECTLY_MUTATE_PRODUCTION"
            ),
        })
    )


# ============================================================
# AUTOMATION / AUTOROBOMLM
# ============================================================

_AUTOMATION_METHOD_NAMES = (
    "status",
    "get_status",
    "state",
    "run",
    "cycle",
    "start",
    "stop",
    "execute",
    "process",
    "authorize",
    "prepare",
)


def _automation_call(
    payload,
    kind="automation",
):
    modules = (
        _REMAINING_BACKEND_CANDIDATES.get(
            kind,
            [],
        )
    )

    for module_name in modules:
        module = _safe_import_module(
            module_name
        )

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _AUTOMATION_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, info = _call_with_supported_kwargs(
            fn,
            payload,
        )

        if info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_EXISTING_AUTOMATION_ENTRYPOINT",
        },
    }


@app.get("/api/automation")
def api_automation():
    result = _automation_call(
        {
            "action": "status",
        },
        "automation",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "automation": result,
            "execution_boundary": (
                "CAS_REQUIRED"
            ),
        })
    )


@app.get("/api/automation/mode")
def api_automation_mode():
    result = _automation_call(
        {
            "action": "status",
        },
        "automation",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "mode": result,
            "allowed_modes": [
                "PAPER",
                "DEMO",
                "LIVE",
            ],
        })
    )


@app.get("/api/automation/execution")
def api_automation_execution():
    result = _automation_call(
        {
            "action": "status",
        },
        "execution",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "execution": result,
        })
    )


@app.get("/api/automation/kill-switch")
def api_automation_kill_switch():
    result = _automation_call(
        {
            "action": "status",
        },
        "automation",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "kill_switch": result,
            "mandatory": True,
        })
    )


@app.get("/api/automation/reconciliation")
def api_automation_reconciliation():
    result = _automation_call(
        {
            "action": "status",
        },
        "execution",
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "reconciliation": result,
        })
    )


# ============================================================
# ACCOUNT / SECURITY VISIBILITY
# ============================================================

@app.get("/api/account/backend-map")
def api_account_backend_map():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "owners": {
                "account": (
                    _REMAINING_BACKEND_CANDIDATES[
                        "account"
                    ]
                ),
                "security": (
                    _REMAINING_BACKEND_CANDIDATES[
                        "security"
                    ]
                ),
                "authorization": [
                    "app.authorization"
                ],
                "subscription": [
                    "app.subscription"
                ],
            },
            "security_boundary": [
                "AUTHENTICATION",
                "AUTHORIZATION",
                "SUBSCRIPTION",
                "ACCOUNT_ISOLATION",
                "EXECUTION_AUTHORIZATION",
            ],
        })
    )


@app.get("/api/account/status")
def api_account_status():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "backend": _backend_owner_status({
                "account": (
                    _REMAINING_BACKEND_CANDIDATES[
                        "account"
                    ]
                ),
                "security": (
                    _REMAINING_BACKEND_CANDIDATES[
                        "security"
                    ]
                ),
            }),
        })
    )


# ============================================================
# BLACKBOX
# ============================================================

_BLACKBOX_METHOD_NAMES = (
    "get",
    "read",
    "query",
    "search",
    "retrieve",
    "history",
    "audit",
    "load",
)


def _blackbox_call(
    payload,
):
    modules = (
        _REMAINING_BACKEND_CANDIDATES[
            "blackbox"
        ]
    )

    for module_name in modules:
        module = _safe_import_module(
            module_name
        )

        if module is None:
            continue

        fn, fn_name = _find_safe_callable(
            module,
            _BLACKBOX_METHOD_NAMES,
        )

        if fn is None:
            continue

        result, info = _call_with_supported_kwargs(
            fn,
            payload,
        )

        if info.get("ok"):
            return {
                "available": True,
                "executed": True,
                "module": module_name,
                "function": fn_name,
                "result": json_safe(result),
                "call": info,
            }

    return {
        "available": False,
        "executed": False,
        "module": None,
        "function": None,
        "result": None,
        "call": {
            "ok": False,
            "error": "NO_EXISTING_BLACKBOX_ENTRYPOINT",
        },
    }


@app.get("/api/blackbox")
def api_blackbox(
    symbol: str = None,
    limit: int = 100,
):
    limit = max(
        1,
        min(
            int(limit or 100),
            1000,
        ),
    )

    result = _blackbox_call({
        "symbol": symbol,
        "limit": limit,
    })

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if result.get(
                    "available"
                )
                else "NO_BLACKBOX_ENGINE"
            ),
            "symbol": symbol,
            "limit": limit,
            "lifecycle": [
                "DATA",
                "EVIDENCE",
                "CONTEXT",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
                "ACTION",
                "EXECUTION",
                "RESULT",
            ],
            "result": result,
        })
    )


@app.get("/api/blackbox/lifecycle")
def api_blackbox_lifecycle():
    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "lifecycle": [
                {
                    "stage": 1,
                    "name": "DATA",
                },
                {
                    "stage": 2,
                    "name": "EVIDENCE",
                },
                {
                    "stage": 3,
                    "name": "CONTEXT",
                },
                {
                    "stage": 4,
                    "name": "INTELLIGENCE",
                },
                {
                    "stage": 5,
                    "name": "DECISION",
                },
                {
                    "stage": 6,
                    "name": "RISK",
                },
                {
                    "stage": 7,
                    "name": "CAS",
                },
                {
                    "stage": 8,
                    "name": "ACTION",
                },
                {
                    "stage": 9,
                    "name": "EXECUTION",
                },
                {
                    "stage": 10,
                    "name": "RESULT",
                },
            ],
            "memory_after_result": [
                "OUTCOME_MEMORY",
                "PATTERN_MEMORY",
                "LEARNING",
            ],
        })
    )


# ============================================================
# COMPLETE BACKEND OWNERSHIP MAP
# ============================================================

@app.get("/api/backend/complete-map")
def api_backend_complete_map():
    """
    Single frontend-readable map of the entire backend.

    This does not claim every Python file is executable through
    an HTTP endpoint. It maps domains to their existing owners
    so no major backend domain is silently hidden from UI.
    """

    combined = {}

    # Part 1/2/3/4 maps, if already defined.
    if "BACKEND_MODULES" in globals():
        combined["core"] = json_safe(
            BACKEND_MODULES
        )

    if (
        "_DISCOVERY_ENGINE_CANDIDATES"
        in globals()
    ):
        combined["discovery"] = json_safe(
            _DISCOVERY_ENGINE_CANDIDATES
        )

    if (
        "_BUYER_ENGINE_CANDIDATES"
        in globals()
    ):
        combined["buyer"] = json_safe(
            _BUYER_ENGINE_CANDIDATES
        )

    combined["remaining"] = json_safe(
        _REMAINING_BACKEND_CANDIDATES
    )

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "architecture": {
                "frontend": "EXISTING_UI",
                "api": "SERVE_API_BRIDGE",
                "backend": "EXISTING_ROBOMLM_PLUS",
                "engines": "EXISTING_ENGINE_OWNERS",
            },
            "domains": combined,
            "principle": (
                "UI -> API -> EXISTING BACKEND OWNER"
            ),
        })
    )


# ============================================================
# COMPLETE SYSTEM HEALTH
# ============================================================

@app.get("/api/backend/complete-health")
def api_backend_complete_health():
    """
    Runtime import/ownership health.

    Import failure is reported; it is not silently converted
    into fake READY data.
    """

    domains = {}

    if "BACKEND_MODULES" in globals():
        domains["core"] = (
            _backend_owner_status(
                {
                    "core": list(
                        BACKEND_MODULES.values()
                    )
                    if isinstance(
                        BACKEND_MODULES,
                        dict,
                    )
                    else []
                }
            )
        )

    domains["discovery"] = (
        _backend_owner_status({
            "discovery": [
                module
                for modules
                in _DISCOVERY_ENGINE_CANDIDATES.values()
                for module in modules
            ]
        })
    )

    domains["buyer"] = (
        _backend_owner_status({
            "buyer": [
                module
                for modules
                in _BUYER_ENGINE_CANDIDATES.values()
                for module in modules
            ]
        })
    )

    domains["remaining"] = (
        _backend_owner_status(
            _REMAINING_BACKEND_CANDIDATES
        )
    )

    available = 0
    checked = 0

    def count_status(obj):
        nonlocal available
        nonlocal checked

        if isinstance(obj, dict):
            if (
                "available" in obj
                and "module" in obj
            ):
                checked += 1

                if obj.get(
                    "available"
                ):
                    available += 1

            for value in obj.values():
                count_status(value)

        elif isinstance(obj, list):
            for value in obj:
                count_status(value)

    count_status(domains)

    return JSONResponse(
        content=json_safe({
            "status": (
                "READY"
                if available
                else "NO_BACKEND_MODULES_AVAILABLE"
            ),
            "available": available,
            "checked": checked,
            "domains": domains,
        })
    )


# ============================================================
# FRONTEND DATA CONTRACT
# ============================================================

@app.get("/api/frontend/backend-contract")
def api_frontend_backend_contract():
    """
    Stable contract consumed by the existing frontend.

    Frontend does not need to know Python module internals.
    """

    return JSONResponse(
        content=json_safe({
            "status": "READY",

            "routes": {
                "terminal": [
                    "/api/terminal",
                    "/api/terminal/evidence",
                    "/api/terminal/intelligence",
                    "/api/terminal/decision",
                    "/api/terminal/risk",
                    "/api/terminal/cas",
                    "/api/terminal/pipeline",
                ],

                "discovery": [
                    "/api/discovery",
                    "/api/discovery/scanner",
                    "/api/discovery/opportunities",
                    "/api/discovery/top10",
                    "/api/discovery/asset",
                    "/api/discovery/explain",
                    "/api/discovery/gates",
                    "/api/discovery/favorites",
                ],

                "buyer": [
                    "/api/buyer/markets",
                    "/api/buyer/strategies",
                    "/api/buyer/analyze",
                    "/api/buyer/pipeline",
                    "/api/buyer/decision",
                    "/api/buyer/risk",
                    "/api/buyer/cas",
                    "/api/buyer/cas/gates",
                    "/api/buyer/plus",
                    "/api/buyer/autorobomlm",
                ],

                "memory": [
                    "/api/memory",
                    "/api/memory/search",
                    "/api/memory/decision",
                    "/api/memory/evidence",
                    "/api/memory/outcome",
                    "/api/memory/pattern",
                ],

                "research": [
                    "/api/research",
                    "/api/research/hypothesis",
                    "/api/research/experiment",
                    "/api/research/validation",
                    "/api/research/stress",
                    "/api/research/candidate",
                    "/api/research/version",
                    "/api/research/deployment",
                ],

                "automation": [
                    "/api/automation",
                    "/api/automation/mode",
                    "/api/automation/execution",
                    "/api/automation/kill-switch",
                    "/api/automation/reconciliation",
                ],

                "blackbox": [
                    "/api/blackbox",
                    "/api/blackbox/lifecycle",
                ],
            },

            "frontend_routes_preserved": [
                "/",
                "/login",
                "/constitution",
                "/risk-disclosure",
                "/terminal",
                "/discovery",
                "/memory",
                "/research",
                "/buyer",
                "/automation",
                "/account",
            ],
        })
    )


# ============================================================
# FINAL PIPELINE CONTRACT
# ============================================================

@app.get("/api/backend/final-pipeline")
def api_backend_final_pipeline():
    return JSONResponse(
        content=json_safe({
            "status": "READY",

            "market_intelligence": [
                "MARKET_DATA",
                "DATA_QUALITY",
                "EVIDENCE",
                "MARKET_CONTEXT",
                "INTELLIGENCE",
            ],

            "decision": [
                "D1_READINESS",
                "D2_CONDITION",
                "D3_CONFIDENCE",
                "D4_RELATIONSHIPS",
                "D5_STRUCTURE",
                "D6_FLOW",
                "D7_LIQUIDITY_VOLATILITY",
                "D8_INSTRUMENT_MECHANICS",
                "D9_TIME_EVENT",
                "D10_MARKET_STATE",
                "D11_TRANSITION",
                "D12_FUTURE_SCENARIO",
                "D13_DECISION",
                "D14_VALIDATION",
                "D15_LEARNING",
                "D16_INTELLIGENCE",
            ],

            "discovery": [
                "UNIVERSE",
                "LIQUIDITY",
                "RISK_FILTER",
                "TIMING",
                "INTRADAY",
                "SCANNER",
                "RANKING",
                "TOP10",
                "OPPORTUNITY",
            ],

            "buyer": [
                "MARKET",
                "INSTRUMENT",
                "CONTRACT",
                "STRATEGY",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
            ],

            "cas": [
                "SUITABILITY",
                "RISK",
                "EXPOSURE",
                "POSITION",
                "EXECUTION_SAFETY",
                "COMPLIANCE",
                "RESTRICTIONS",
            ],

            "execution": [
                "CAS_APPROVAL",
                "AUTOROBOMLM",
                "STRATEGY_RUNNER",
                "ORDER_MANAGER",
                "EXECUTION_MANAGER",
                "POSITION_MANAGER",
                "RECONCILIATION",
                "EXECUTION_AUDIT",
            ],

            "plus": [
                "ADVANCED_DECISION",
                "EXECUTION_PREPARATION",
                "POSITION_MONITORING",
                "PROTECTION",
                "RECONCILIATION",
                "EMERGENCY_CONTROL",
                "HALT_CONTROLLER",
            ],

            "learning": [
                "OUTCOME_MEMORY",
                "PATTERN_MEMORY",
                "D15_LEARNING",
                "D16_INTELLIGENCE",
            ],

            "research": [
                "HYPOTHESIS",
                "EXPERIMENT",
                "VALIDATION",
                "STRESS_TEST",
                "CANDIDATE",
                "VERSION",
                "CONTROLLED_DEPLOYMENT",
            ],

            "blackbox": [
                "DATA",
                "EVIDENCE",
                "CONTEXT",
                "INTELLIGENCE",
                "DECISION",
                "RISK",
                "CAS",
                "ACTION",
                "EXECUTION",
                "RESULT",
            ],
        })
    )


# ============================================================
# FINAL NO-SILENT-OMISSION REPORT
# ============================================================

@app.get("/api/backend/coverage")
def api_backend_coverage():
    """
    Frontend coverage declaration.

    A domain can be:
      AVAILABLE  = existing module imports
      PARTIAL    = some owners import, others do not
      UNAVAILABLE = no owner currently importable

    No fake data is inserted to turn an unavailable domain into
    READY.
    """

    owner_groups = {
        "terminal": {
            "modules": [
                "app.terminal.terminal_service",
                "app.terminal.market_context",
                "app.terminal.evidence_strip",
                "app.terminal.intelligence_panel",
                "app.terminal.decision_outlook",
                "app.terminal.risk_panel",
                "app.terminal.cas_status",
            ]
        },

        "discovery": {
            "modules": [
                module
                for modules
                in _DISCOVERY_ENGINE_CANDIDATES.values()
                for module in modules
            ]
        },

        "buyer": {
            "modules": [
                module
                for modules
                in _BUYER_ENGINE_CANDIDATES.values()
                for module in modules
            ]
        },

        "memory": {
            "modules": (
                _REMAINING_BACKEND_CANDIDATES[
                    "memory"
                ]
            )
        },

        "research": {
            "modules": (
                _REMAINING_BACKEND_CANDIDATES[
                    "research"
                ]
            )
        },

        "automation": {
            "modules": (
                _REMAINING_BACKEND_CANDIDATES[
                    "automation"
                ]
            )
        },

        "execution": {
            "modules": (
                _REMAINING_BACKEND_CANDIDATES[
                    "execution"
                ]
            )
        },

        "security": {
            "modules": (
                _REMAINING_BACKEND_CANDIDATES[
                    "security"
                ]
            )
        },
    }

    output = {}

    for domain, config in owner_groups.items():
        modules = config.get(
            "modules",
            [],
        )

        checked = []
        available_count = 0

        for module_name in modules:
            info = _module_runtime_info(
                module_name
            )

            checked.append(info)

            if info.get(
                "available"
            ):
                available_count += 1

        if not modules:
            status = "UNAVAILABLE"
        elif available_count == len(
            modules
        ):
            status = "AVAILABLE"
        elif available_count:
            status = "PARTIAL"
        else:
            status = "UNAVAILABLE"

        output[domain] = {
            "status": status,
            "available": available_count,
            "checked": len(modules),
            "modules": checked,
        }

    return JSONResponse(
        content=json_safe({
            "status": "READY",
            "coverage": output,

            "rule": (
                "NO_DEMO_DATA_IS_USED_TO_CLAIM_BACKEND_COVERAGE"
            ),

            "execution_rule": (
                "DECISION -> RISK -> CAS -> AUTHORIZED_ACTION"
            ),
        })
    )


# ============================================================
# END PART 5 / 5
# ============================================================


from app.api.account_routes import router as account_router
app.include_router(account_router)


from app.api.account_routes import bot_router
app.include_router(bot_router)


# ============================================================================
# COMPATIBILITY LAYER — TEST-ONLY (not production intelligence)
# ============================================================================
#
# Ye endpoints frontend ke liye hain jo pehle se UI mein wired hain.
# Inme koi real engine nahi hai — sirf in-memory test state.
#
# REAL engines (D1-D16, CAS, Evidence, Intelligence) yahan nahi hain —
# woh apne original modules mein hain aur un endpoints se serve hote hain
# jo pehle se server.py mein hain.
#
# Agar production chahiye: in endpoints ko real backend engines se wire karo.
# ============================================================================

# --- Test state (in-memory only) ---
from typing import List as _List_t
import uuid as _uuid_t
import csv as _csv_t
from pathlib import Path as _Path_t

_CSV_DIR = _Path_t(r"C:\Users\Administrator\ROBOMLM_PLUS\robomlm_data\csv")
_CSV_DIR.mkdir(parents=True, exist_ok=True)

_CSV_FILES = [
    "trade_history.csv", "decision_lifecycle.csv", "position_history.csv",
    "reject_log.csv", "eqe_history.csv", "mtf_history.csv",
    "tick_snapshot.csv", "phase_history.csv", "learning_journal.csv",
]
_CSV_HEADERS = {
    "trade_history.csv": ["timestamp","symbol","direction","entry","exit","sl","tp","pnl","reason","grade"],
    "decision_lifecycle.csv": ["timestamp","signal","grade","rr","mtf_consensus","eqe","verdict"],
    "position_history.csv": ["timestamp","symbol","direction","size","entry","sl","tp","status"],
    "reject_log.csv": ["timestamp","symbol","reason","eqe","latency_ms"],
    "eqe_history.csv": ["timestamp","symbol","eqe"],
    "mtf_history.csv": ["timestamp","symbol","tf_1m","tf_5m","tf_15m","tf_1h","tf_4h"],
    "tick_snapshot.csv": ["timestamp","symbol","price","signal","phase","consensus","eqe"],
    "phase_history.csv": ["timestamp","symbol","phase"],
    "learning_journal.csv": ["timestamp","lesson","category"],
}
for _f in _CSV_FILES:
    _p = _CSV_DIR / _f
    if not _p.exists():
        with _p.open("w", newline="", encoding="utf-8") as _fh:
            _csv_t.writer(_fh).writerow(_CSV_HEADERS[_f])

_ACCOUNT = {
    "seed_inr": 100000.0, "seed_usd": 1200.0,
    "capital": 100000.0, "balance": 100000.0,
    "today_pnl": 0.0, "open_positions": 0,
    "mode": "PAPER", "currency": "INR",
    "usd_inr_rate": 83.33,
    "auto_alloc_pct": 50.0, "mission_alloc_pct": 50.0,
}
_POSITIONS: _List_t = []
_ACTIVITY: _List_t = []

_BOTS = {
    "auto": {"status": "IDLE", "action_text": "Bot not started",
             "last_signal": None, "last_grade": None, "last_rr": None, "last_confidence": None},
    "mission": {"status": "IDLE", "action_text": "No active mission",
                "target_price": None, "current_price": None,
                "progress_pct": 0.0, "compounded_pnl": 0.0},
}

_AUTO = {"status": "STOPPED", "min_grade": "B", "min_rr": 2.0,
         "sl_pct": 1.5, "tp_pct": 3.0, "started_at": None}

_MISSION = {"active": False, "target_price": None, "current_price": None,
            "progress_pct": 0.0, "capital": 100000.0, "compounded_profit": 0.0,
            "allocation_pct": 10.0, "position_size": 0.0,
            "trades_attempted": 0, "trades_won": 0, "trades_lost": 0,
            "started_at": None, "note": ""}


def _log_activity(kind: str, msg: str, bot: str = "auto"):
    from datetime import datetime as _dt_x, timezone as _tz_x
    _ACTIVITY.append({
        "ts": _dt_x.now(_tz_x.utc).strftime("%H:%M:%S"),
        "kind": kind, "msg": msg, "bot": bot,
    })
    if len(_ACTIVITY) > 400:
        del _ACTIVITY[:-400]


def _fetch_price(symbol: str = "BTCUSDT") -> float:
    try:
        import urllib.request as _u, json as _j
        sym = symbol.replace("/", "").upper()
        url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={sym}"
        with _u.urlopen(url, timeout=4) as r:
            d = _j.loads(r.read())
        lst = (d.get("result") or {}).get("list") or []
        return float(lst[0]["lastPrice"]) if lst else 0.0
    except Exception:
        return 0.0


def _compute_pnl(pos, exit_price):
    try:
        size = float(pos.get("size", 0) or 0)
        entry = float(pos.get("entry", 0) or 0)
        if entry <= 0 or size <= 0 or exit_price <= 0:
            return 0.0
        if pos.get("direction") == "LONG":
            return round((exit_price - entry) * size, 4)
        return round((entry - exit_price) * size, 4)
    except Exception:
        return 0.0


def _close_position(pos, exit_price, reason):
    from datetime import datetime as _dt_x, timezone as _tz_x
    pos["status"] = "closed"
    pos["exit_price"] = exit_price
    pos["closed_at"] = _dt_x.now(_tz_x.utc).isoformat()
    pos["exit_reason"] = reason
    pnl = _compute_pnl(pos, exit_price)
    pos["pnl"] = pnl
    _ACCOUNT["balance"] = round(_ACCOUNT["balance"] + pnl, 4)
    _log_activity("CLOSE", f"{pos['direction']} {pos['symbol']} @ {exit_price} - {reason} - pnl {pnl}",
                  bot=pos.get("bot", "auto"))


def _monitor_positions():
    op = [p for p in _POSITIONS if p.get("status") == "open"]
    if not op:
        return
    cache = {}
    for p in op:
        sym = p.get("symbol", "BTCUSDT")
        if sym not in cache:
            cache[sym] = _fetch_price(sym)
        price = cache[sym]
        if price <= 0:
            continue
        p["pnl"] = _compute_pnl(p, price)
        p["current_price"] = price
        is_long = p.get("direction") == "LONG"
        sl = float(p.get("sl", 0) or 0)
        tp = float(p.get("tp", 0) or 0)
        if is_long:
            if sl > 0 and price <= sl: _close_position(p, price, "SL_HIT")
            elif tp > 0 and price >= tp: _close_position(p, price, "TP_HIT")
        else:
            if sl > 0 and price >= sl: _close_position(p, price, "SL_HIT")
            elif tp > 0 and price <= tp: _close_position(p, price, "TP_HIT")


# --- Pydantic request models (COMPAT) ---
class _AccountModeReq(BaseModel):
    mode: str

class _AccountCurrencyReq(BaseModel):
    currency: str

class _BotAllocReq(BaseModel):
    auto_alloc_pct: float
    mission_alloc_pct: float

class _NewPosReq(BaseModel):
    symbol: str
    direction: str
    entry: float
    sl: float
    tp: float
    size: float = 0.0
    grade: str = "B"
    strategy: str = ""
    bot: str = "auto"

class _TradeReq(BaseModel):
    symbol: str
    side: str
    tp: Optional[float] = None
    sl: Optional[float] = None
    qty: Optional[float] = None
    note: Optional[str] = None

class _AutoReq(BaseModel):
    min_grade: str = "B+"
    min_rr: float = 2.0
    sl_pct: float = 1.5
    tp_pct: float = 3.0

class _MissionReq(BaseModel):
    target_price: float
    capital: float = 100000.0
    allocation_pct: float = 10.0
    min_grade: str = "A"
    min_rr: float = 2.0
    sl_pct: float = 1.5


# --- ACCOUNT ---
@app.get("/api/account/summary")
def _compat_account_summary():
    return JSONResponse({"ok": True, "capital": _ACCOUNT["capital"], "balance": _ACCOUNT["balance"],
        "today_pnl": _ACCOUNT["today_pnl"], "open_positions": _ACCOUNT["open_positions"],
        "mode": _ACCOUNT["mode"], "currency": _ACCOUNT["currency"],
        "usd_inr_rate": _ACCOUNT["usd_inr_rate"], "seed_inr": _ACCOUNT["seed_inr"], "seed_usd": _ACCOUNT["seed_usd"]})

@app.post("/api/account/mode")
def _compat_account_mode(req: _AccountModeReq):
    m = req.mode.upper().strip()
    if m not in ("PAPER", "LIVE"):
        return JSONResponse({"ok": False, "error": "mode must be PAPER or LIVE"}, status_code=400)
    _ACCOUNT["mode"] = m
    return JSONResponse({"ok": True, "mode": m})

@app.post("/api/account/currency")
def _compat_account_currency(req: _AccountCurrencyReq):
    c = req.currency.upper().strip()
    if c not in ("INR", "USD"):
        return JSONResponse({"ok": False, "error": "currency must be INR or USD"}, status_code=400)
    _ACCOUNT["currency"] = c
    return JSONResponse({"ok": True, "currency": c})

@app.post("/api/account/reset-seed")
def _compat_account_reset():
    _ACCOUNT["capital"] = _ACCOUNT["seed_inr"] if _ACCOUNT["currency"] == "INR" else _ACCOUNT["seed_usd"]
    _ACCOUNT["balance"] = _ACCOUNT["capital"]
    _ACCOUNT["today_pnl"] = 0.0
    return JSONResponse({"ok": True, "capital": _ACCOUNT["capital"], "balance": _ACCOUNT["balance"]})

@app.get("/api/account/equity")
def _compat_account_equity():
    from datetime import datetime as _dt_x, timezone as _tz_x
    pts = []
    try:
        with (_CSV_DIR / "trade_history.csv").open("r", encoding="utf-8") as f:
            rows = list(_csv_t.DictReader(f))
        running = _ACCOUNT["capital"]
        for r in rows[-90:]:
            try:
                running += float(r.get("pnl") or 0)
                pts.append({"t": r.get("timestamp", ""), "v": running})
            except Exception:
                continue
    except Exception:
        pass
    if not pts:
        pts = [{"t": _dt_x.now(_tz_x.utc).isoformat(), "v": _ACCOUNT["capital"]}]
    return JSONResponse({"ok": True, "points": pts})

@app.get("/api/account/allocation")
def _compat_account_allocation():
    b = {"crypto": 0, "fx": 0, "commodity": 0, "equity": 0, "index": 0}
    for p in _POSITIONS:
        if p.get("status") != "open":
            continue
        s = (p.get("symbol") or "").upper()
        if any(c in s for c in ["BTC","ETH","SOL","BNB","XRP","DOGE","ADA"]): b["crypto"] += 1
        elif any(c in s for c in ["USD","EUR","GBP","JPY"]): b["fx"] += 1
        elif any(c in s for c in ["GOLD","SILVER","OIL","COPPER","GAS"]): b["commodity"] += 1
        elif any(c in s for c in ["NIFTY","SENSEX","SPX","NASDAQ"]): b["index"] += 1
        else: b["equity"] += 1
    return JSONResponse({"ok": True, "allocation": b})

@app.get("/api/account/download/{csv_name}")
def _compat_account_download(csv_name: str):
    if csv_name not in _CSV_FILES:
        return JSONResponse({"ok": False, "error": "unknown file"}, status_code=404)
    path = _CSV_DIR / csv_name
    if not path.exists():
        return JSONResponse({"ok": False, "error": "file missing"}, status_code=404)
    return Response(content=path.read_text(encoding="utf-8"), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{csv_name}"'})


# --- PORTFOLIO / POSITIONS ---
@app.get("/api/portfolio/overview")
def _compat_portfolio():
    op = [p for p in _POSITIONS if p.get("status") == "open"]
    cl = [p for p in _POSITIONS if p.get("status") == "closed"]
    realized = sum(p.get("pnl", 0) for p in cl)
    unrealized = sum(p.get("pnl", 0) for p in op)
    total = len(cl)
    wins = len([p for p in cl if p.get("pnl", 0) > 0])
    wr = (wins / total * 100) if total else 0.0
    return JSONResponse({"ok": True, "capital": _ACCOUNT["capital"], "balance": _ACCOUNT["balance"],
        "today_pnl": round(realized + unrealized, 4), "realized_pnl": round(realized, 4),
        "unrealized_pnl": round(unrealized, 4), "open_positions": len(op),
        "total_trades": total, "win_rate": round(wr, 1),
        "mode": _ACCOUNT["mode"], "currency": _ACCOUNT["currency"]})

@app.get("/api/positions")
def _compat_positions_list():
    try:
        _monitor_positions()
    except Exception as e:
        _log_activity("ERR", f"Monitor error: {e}", bot="auto")
    return JSONResponse({"ok": True, "positions": _POSITIONS})

@app.get("/api/activity")
def _compat_activity(limit: int = 50):
    return JSONResponse({"ok": True, "activity": _ACTIVITY[-limit:][::-1]})

@app.post("/api/positions/open")
def _compat_positions_open(p: _NewPosReq):
    from datetime import datetime as _dt_x, timezone as _tz_x
    d = p.direction.upper()
    if d == "LONG" and not (p.sl < p.entry < p.tp):
        return JSONResponse({"ok": False, "error": "LONG: SL < Entry < TP required"}, status_code=400)
    if d == "SHORT" and not (p.tp < p.entry < p.sl):
        return JSONResponse({"ok": False, "error": "SHORT: TP < Entry < SL required"}, status_code=400)
    pos = {"id": str(_uuid_t.uuid4())[:8], "symbol": p.symbol, "direction": d,
           "entry": p.entry, "sl": p.sl, "tp": p.tp, "size": p.size, "grade": p.grade,
           "bot": (p.bot or "auto").lower(), "status": "open", "pnl": 0.0,
           "opened_at": _dt_x.now(_tz_x.utc).isoformat()}
    _POSITIONS.append(pos)
    _log_activity("OPEN", f"{pos['direction']} {p.symbol} @ {p.entry}", bot=pos["bot"])
    return JSONResponse({"ok": True, "position": pos})

@app.post("/api/positions/{pos_id}/close")
def _compat_positions_close(pos_id: str):
    for pos in _POSITIONS:
        if pos["id"] == pos_id and pos.get("status") == "open":
            price = _fetch_price(pos.get("symbol", "BTCUSDT")) or float(pos.get("entry", 0))
            _close_position(pos, price, "MANUAL")
            return JSONResponse({"ok": True, "position": pos})
    return JSONResponse({"ok": False, "error": "position not found"}, status_code=404)


# --- BOT FINANCE / TRADES / ACTIVITY / ALLOCATION ---
def _compat_recalc_bot():
    op = [p for p in _POSITIONS if p.get("status") == "open"]
    cl = [p for p in _POSITIONS if p.get("status") == "closed"]
    used = sum(p.get("size", 0) * p.get("entry", 0) for p in op)
    cap = _ACCOUNT["capital"]
    return {
        "allocated_capital": cap, "used_capital": round(used, 2),
        "realized_pnl": round(sum(p.get("pnl", 0) for p in cl), 4),
        "unrealized_pnl": round(sum(p.get("pnl", 0) for p in op), 4),
        "exposure_pct": round(used / cap * 100, 2) if cap else 0,
        "max_exposure_pct": 30.0,
        "trades_today": len(cl),
        "wins_today": len([p for p in cl if p.get("pnl", 0) > 0]),
        "losses_today": len([p for p in cl if p.get("pnl", 0) < 0]),
    }

@app.get("/api/bot/finance")
def _compat_bot_finance():
    return JSONResponse({"ok": True, **_compat_recalc_bot()})

@app.get("/api/bot/trades")
def _compat_bot_trades(status: str = "all", limit: int = 50):
    rows = _POSITIONS
    if status == "open": rows = [p for p in rows if p.get("status") == "open"]
    elif status == "closed": rows = [p for p in rows if p.get("status") == "closed"]
    return JSONResponse({"ok": True, "trades": rows[-limit:][::-1]})

@app.get("/api/bot/activity")
def _compat_bot_activity(limit: int = 30):
    return JSONResponse({"ok": True, "activity": _ACTIVITY[-limit:][::-1]})

@app.get("/api/bot/allocation")
def _compat_bot_alloc_get():
    a = _ACCOUNT["auto_alloc_pct"]; m = _ACCOUNT["mission_alloc_pct"]; cap = _ACCOUNT["capital"]
    return JSONResponse({"ok": True, "total_capital": cap, "currency": _ACCOUNT["currency"],
        "auto_alloc_pct": a, "mission_alloc_pct": m,
        "auto_capital": round(cap * a / 100, 2), "mission_capital": round(cap * m / 100, 2),
        "unallocated_pct": round(100 - a - m, 2),
        "unallocated_capital": round(cap * (1 - (a + m) / 100), 2)})

@app.post("/api/bot/allocation")
def _compat_bot_alloc_set(req: _BotAllocReq):
    a = max(0.0, min(100.0, float(req.auto_alloc_pct)))
    m = max(0.0, min(100.0, float(req.mission_alloc_pct)))
    if a + m > 100.0:
        return JSONResponse({"ok": False, "error": "total cannot exceed 100%"}, status_code=400)
    _ACCOUNT["auto_alloc_pct"] = a
    _ACCOUNT["mission_alloc_pct"] = m
    return JSONResponse({"ok": True, "auto_alloc_pct": a, "mission_alloc_pct": m})

@app.get("/api/bot/{bot_name}/status")
def _compat_bot_status(bot_name: str):
    if bot_name not in _BOTS:
        return JSONResponse({"ok": False, "error": "unknown bot"}, status_code=404)
    b = dict(_BOTS[bot_name])
    pos = [p for p in _POSITIONS if p.get("bot", "auto") == bot_name]
    alloc = _ACCOUNT["capital"] * (_ACCOUNT.get(f"{bot_name}_alloc_pct", 50) / 100)
    used = sum(p.get("size", 0) * p.get("entry", 0) for p in pos if p.get("status") == "open")
    return JSONResponse({"ok": True, "bot": bot_name, **b,
        "allocated_capital": round(alloc, 2), "used_capital": round(used, 2),
        "free_capital": round(alloc - used, 2),
        "realized_pnl": round(sum(p.get("pnl", 0) for p in pos if p.get("status") == "closed"), 2),
        "unrealized_pnl": round(sum(p.get("pnl", 0) for p in pos if p.get("status") == "open"), 2),
        "open_trades": len([p for p in pos if p.get("status") == "open"]),
        "trades_total": len([p for p in pos if p.get("status") == "closed"]),
        "currency": _ACCOUNT["currency"]})

@app.get("/api/bot/{bot_name}/trades")
def _compat_bot_trades_named(bot_name: str, status: str = "all"):
    if bot_name not in _BOTS:
        return JSONResponse({"ok": False, "error": "unknown bot"}, status_code=404)
    rows = [p for p in _POSITIONS if p.get("bot", "auto") == bot_name]
    if status == "open": rows = [p for p in rows if p.get("status") == "open"]
    elif status == "closed": rows = [p for p in rows if p.get("status") == "closed"]
    return JSONResponse({"ok": True, "trades": rows[::-1]})

@app.get("/api/bot/{bot_name}/activity")
def _compat_bot_activity_named(bot_name: str, limit: int = 20):
    if bot_name not in _BOTS:
        return JSONResponse({"ok": False, "error": "unknown bot"}, status_code=404)
    rows = [a for a in _ACTIVITY if a.get("bot", "auto") == bot_name]
    return JSONResponse({"ok": True, "activity": rows[-limit:][::-1]})


# --- AUTOROBOMLM ---
@app.get("/api/autorobomlm/status")
def _compat_auto_status():
    return JSONResponse({"status": _AUTO["status"], "min_grade": _AUTO["min_grade"],
        "min_rr": _AUTO["min_rr"], "sl_pct": _AUTO["sl_pct"], "tp_pct": _AUTO["tp_pct"]})

@app.post("/api/autorobomlm/start")
def _compat_auto_start(cfg: _AutoReq):
    _AUTO.update({"status": "RUNNING", "min_grade": cfg.min_grade, "min_rr": cfg.min_rr,
                  "sl_pct": cfg.sl_pct, "tp_pct": cfg.tp_pct})
    _BOTS["auto"]["status"] = "SCANNING"
    _BOTS["auto"]["action_text"] = "Bot started - scanning market"
    _log_activity("SIGNAL", f"Bot started - Grade {cfg.min_grade}+ - RR {cfg.min_rr}", bot="auto")
    return JSONResponse({"ok": True, "config": _AUTO})

@app.post("/api/autorobomlm/pause")
def _compat_auto_pause():
    if _AUTO["status"] == "RUNNING":
        _AUTO["status"] = "PAUSED"
    return JSONResponse({"ok": True, "status": _AUTO["status"]})

@app.post("/api/autorobomlm/stop")
def _compat_auto_stop():
    _AUTO["status"] = "STOPPED"
    _BOTS["auto"]["status"] = "IDLE"
    _BOTS["auto"]["action_text"] = "Bot stopped"
    _log_activity("STOP", "Bot stopped by user", bot="auto")
    return JSONResponse({"ok": True, "status": "STOPPED"})

@app.get("/api/autorobomlm/mission/status")
def _compat_mission_status():
    return JSONResponse(_MISSION)

@app.post("/api/autorobomlm/mission/start")
def _compat_mission_start(cfg: _MissionReq):
    from datetime import datetime as _dt_x, timezone as _tz_x
    if cfg.target_price <= 0:
        return JSONResponse({"ok": False, "error": "invalid target"}, status_code=400)
    alloc = max(1.0, min(cfg.allocation_pct, 50.0))
    _MISSION.update({"active": True, "target_price": cfg.target_price, "capital": cfg.capital,
        "allocation_pct": alloc, "started_at": _dt_x.now(_tz_x.utc).isoformat(),
        "note": f"Mission active - Grade {cfg.min_grade} - RR {cfg.min_rr}",
        "position_size": cfg.capital * (alloc / 100)})
    return JSONResponse({"ok": True, "mission": _MISSION})

@app.post("/api/autorobomlm/mission/stop")
def _compat_mission_stop():
    _MISSION["active"] = False
    _MISSION["note"] = "Mission stopped by user"
    return JSONResponse({"ok": True, "mission": _MISSION})

@app.get("/api/autorobomlm/mission/progress")
def _compat_mission_progress():
    if not _MISSION["active"] or not _MISSION["target_price"]:
        return JSONResponse({"ok": True, "active": False})
    return JSONResponse({"ok": True, "active": True, "mission": _MISSION})


# --- TRADE PLACE ---
@app.post("/api/trade/place")
def _compat_trade_place(req: _TradeReq):
    from datetime import datetime as _dt_x, timezone as _tz_x
    side = (req.side or "").upper()
    if side not in ("CALL", "PUT", "BUY", "SELL"):
        return JSONResponse({"ok": False, "error": "invalid side"}, status_code=400)
    return JSONResponse({"ok": True,
        "trade_id": f"MT-{_uuid_t.uuid4().hex[:10].upper()}",
        "symbol": req.symbol, "side": side, "tp": req.tp, "sl": req.sl, "qty": req.qty,
        "note": req.note or "", "placed_at": _dt_x.now(_tz_x.utc).isoformat(),
        "status": "ACCEPTED", "mode": "MANUAL"})


# ============================================================================
# END COMPATIBILITY LAYER
# ============================================================================


# ============================================================================
# SCANNER ADAPTER — patch for class-based engine discovery
# ============================================================================
# Server ka default discovery module-level function dhundh raha hai.
# Par ScannerEngine class-based hai. Yeh override class instance banata hai.
#
# Yeh patch _execute_existing_discovery_engine ko wrap karta hai —
# sirf jab "scanner" kind ho, aur module-level function na mile.
# ============================================================================

_original_execute_discovery = _execute_existing_discovery_engine


def _execute_existing_discovery_engine(kind, symbol=None, market=None, timeframe=None, payload=None):
    """
    Wrapper: pehle original try karo. Agar scanner fail ho, class-based
    ScannerEngine use karo.
    """
    result = _original_execute_discovery(
        kind,
        symbol=symbol,
        market=market,
        timeframe=timeframe,
        payload=payload,
    )

    if result.get("executed"):
        return result

    # Class-based fallback for scanner
    if kind == "scanner":
        try:
            from app.intelligence.opportunity.scanner_engine import (
                create_scanner_engine,
            )

            engine = create_scanner_engine()

            scan_kwargs = {}
            if symbol:
                scan_kwargs["symbol"] = symbol
            if market:
                scan_kwargs["market"] = market

            # Try scan with minimal args
            try:
                scan_result = engine.scan(**scan_kwargs)
            except TypeError:
                try:
                    scan_result = engine.scan()
                except Exception as e:
                    return {
                        "available": True,
                        "executed": False,
                        "module": "app.intelligence.opportunity.scanner_engine",
                        "function": "ScannerEngine.scan",
                        "result": None,
                        "call": {"ok": False, "error": f"scan call failed: {e}"},
                    }

            return {
                "available": True,
                "executed": True,
                "module": "app.intelligence.opportunity.scanner_engine",
                "function": "ScannerEngine.scan",
                "result": json_safe(scan_result),
                "call": {"ok": True},
            }
        except Exception as e:
            return {
                "available": True,
                "executed": False,
                "module": "app.intelligence.opportunity.scanner_engine",
                "function": "create_scanner_engine",
                "result": None,
                "call": {"ok": False, "error": f"engine init failed: {e}"},
            }

    return result


# ============================================================================
# END SCANNER ADAPTER
# ============================================================================



# ============================================================================
# CLEAN OVERRIDES — memory / discovery / terminal
# ============================================================================

# --- MEMORY: use memory_service.*_service function names ---
@app.get("/api/memory-fixed")
def _memory_fixed(symbol: str = None, limit: int = 50):
    try:
        from app.intelligence.memory import memory_service as _ms
        result = None
        used_fn = None
        for fn_name in (
            "search_memory_service",
            "retrieve_memory_service",
            "review_memory_service",
            "evaluate_memory_service",
        ):
            fn = getattr(_ms, fn_name, None)
            if callable(fn):
                try:
                    result = fn()
                    used_fn = fn_name
                    break
                except Exception:
                    continue
        return JSONResponse({
            "status": "READY" if used_fn else "NO_ENTRYPOINT",
            "function_used": used_fn,
            "result": json_safe(result),
        })
    except Exception as e:
        return JSONResponse({"status": "ERROR", "error": str(e)})


# --- DISCOVERY: pass candidates to ScannerEngine.scan ---
@app.get("/api/discovery-fixed")
def _discovery_fixed(
    market: str = None,
    symbol: str = None,
    timeframe: str = "1m",
    minimum_grade: str = "B",
):
    try:
        from app.intelligence.opportunity.scanner_engine import create_scanner_engine
        engine = create_scanner_engine()

        candidates = [
            {"symbol": "BTCUSDT", "market": "CRYPTO"},
            {"symbol": "ETHUSDT", "market": "CRYPTO"},
            {"symbol": "SOLUSDT", "market": "CRYPTO"},
            {"symbol": "NIFTY", "market": "INDEX"},
            {"symbol": "BANKNIFTY", "market": "INDEX"},
            {"symbol": "GOLD", "market": "COMMODITY"},
            {"symbol": "EURUSD", "market": "FX"},
        ]

        scan_result = engine.scan(candidates=candidates)

        rows = []
        if hasattr(scan_result, "candidates"):
            rows = scan_result.candidates
        elif isinstance(scan_result, dict):
            rows = scan_result.get("candidates") or scan_result.get("rows") or []

        return JSONResponse({
            "status": "READY",
            "count": len(rows),
            "rows": json_safe(rows),
            "scanner_module": "app.intelligence.opportunity.scanner_engine",
            "scanner_function": "ScannerEngine.scan",
        })
    except Exception as e:
        return JSONResponse({"status": "ERROR", "error": str(e)})


# --- TERMINAL: merge real service data with UI contract ---
@app.get("/api/terminal-fixed")
def _terminal_fixed(symbol: str = "BTC/USDT", timeframe: str = "1m"):
    # Real data from terminal_service
    real = _call_existing_terminal_service(symbol, timeframe)
    # UI contract
    ui = {}
    try:
        from app.api.v1.terminal_api import terminal as _tapi, TerminalRequest
        req = TerminalRequest(symbol=symbol, timeframe=timeframe)
        r = _tapi(req)
        if isinstance(r, dict):
            ui = r
    except Exception:
        pass

    return JSONResponse({
        "ok": True,
        "symbol": symbol,
        "timeframe": timeframe,
        "ui": ui.get("ui", {}),
        "authority": ui.get("authority", {}),
        "data": real if isinstance(real, dict) else {},
    })


# --- TERMINAL: use correct function name ---
@app.get("/api/terminal-fixed")
def _terminal_fixed_v2(symbol: str = "BTC/USDT", timeframe: str = "1m"):
    try:
        from app.terminal import terminal_service as _ts

        data = None
        used_fn = None

        for fn_name in (
            "terminal_frontend_context",
            "get_terminal_frontend_context",
            "terminal_frontend_payload",
        ):
            fn = getattr(_ts, fn_name, None)
            if not callable(fn):
                continue
            try:
                data = fn(symbol=symbol, timeframe=timeframe)
                used_fn = fn_name
                break
            except TypeError:
                try:
                    data = fn(symbol, timeframe)
                    used_fn = fn_name
                    break
                except Exception:
                    continue
            except Exception:
                continue

        if data is None:
            return JSONResponse({
                "ok": False,
                "status": "NO_DATA",
                "error": "terminal_frontend_context returned None or failed",
            })

        return JSONResponse({
            "ok": True,
            "symbol": symbol,
            "timeframe": timeframe,
            "function_used": used_fn,
            "data": json_safe(data),
        })
    except Exception as e:
        return JSONResponse({"ok": False, "status": "ERROR", "error": str(e)})