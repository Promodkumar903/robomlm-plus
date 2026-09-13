"""
ROBOMLM PLUS
Application Constants
Module: app/core/constants/app_constants.py

Purpose:
    Central application-level constants.
"""

from __future__ import annotations


# --------------------------------------------------
# APPLICATION IDENTITY
# --------------------------------------------------

APP_NAME = "ROBOMLM_PLUS"

APP_VERSION = "1.0.0"

PRODUCT_NAME = "ROBOMLM"

AUTOMATION_PRODUCT_NAME = "AUTOROBIMLM"


# --------------------------------------------------
# APPLICATION MODES
# --------------------------------------------------

MODE_PAPER = "PAPER"
MODE_DEMO = "DEMO"
MODE_LIVE = "LIVE"

SUPPORTED_MODES = (
    MODE_PAPER,
    MODE_DEMO,
    MODE_LIVE,
)


# --------------------------------------------------
# APPLICATION STATUS
# --------------------------------------------------

STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"
STATUS_INITIALIZING = "INITIALIZING"
STATUS_READY = "READY"
STATUS_DEGRADED = "DEGRADED"
STATUS_ERROR = "ERROR"
STATUS_STOPPED = "STOPPED"


# --------------------------------------------------
# SYSTEM STATES
# --------------------------------------------------

SYSTEM_STATE_STARTING = "STARTING"
SYSTEM_STATE_READY = "READY"
SYSTEM_STATE_RUNNING = "RUNNING"
SYSTEM_STATE_DEGRADED = "DEGRADED"
SYSTEM_STATE_STOPPING = "STOPPING"
SYSTEM_STATE_STOPPED = "STOPPED"
SYSTEM_STATE_ERROR = "ERROR"


# --------------------------------------------------
# USER TYPES
# --------------------------------------------------

USER_TYPE_BUYER = "BUYER"
USER_TYPE_ADMIN = "ADMIN"


# --------------------------------------------------
# CORE PRODUCT AREAS
# --------------------------------------------------

AREA_TERMINAL = "TERMINAL"
AREA_DISCOVERY = "DISCOVERY"
AREA_MEMORY = "MEMORY"
AREA_RESEARCH = "RESEARCH"
AREA_AUTOMATION = "AUTOMATION"
AREA_ACCOUNT = "ACCOUNT"


# --------------------------------------------------
# MARKET CATEGORIES
# --------------------------------------------------

MARKET_STOCK = "STOCK"
MARKET_INDEX = "INDEX"
MARKET_FX = "FX"
MARKET_CRYPTO = "CRYPTO"
MARKET_COMMODITY = "COMMODITY"


SUPPORTED_MARKETS = (
    MARKET_STOCK,
    MARKET_INDEX,
    MARKET_FX,
    MARKET_CRYPTO,
    MARKET_COMMODITY,
)


# --------------------------------------------------
# CORE INTELLIGENCE STATES
# --------------------------------------------------

INTELLIGENCE_PENDING = "PENDING"
INTELLIGENCE_PROCESSING = "PROCESSING"
INTELLIGENCE_READY = "READY"
INTELLIGENCE_UNAVAILABLE = "UNAVAILABLE"
INTELLIGENCE_ERROR = "ERROR"


# --------------------------------------------------
# DECISION STATES
# --------------------------------------------------

DECISION_PENDING = "PENDING"
DECISION_BUY = "BUY"
DECISION_SELL = "SELL"
DECISION_HOLD = "HOLD"
DECISION_NO_TRADE = "NO_TRADE"
DECISION_REJECTED = "REJECTED"


# --------------------------------------------------
# EVIDENCE STATES
# --------------------------------------------------

EVIDENCE_PENDING = "PENDING"
EVIDENCE_READY = "READY"
EVIDENCE_CONFLICT = "CONFLICT"
EVIDENCE_INSUFFICIENT = "INSUFFICIENT"
EVIDENCE_UNAVAILABLE = "UNAVAILABLE"


# --------------------------------------------------
# RISK STATES
# --------------------------------------------------

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"
RISK_BLOCKED = "BLOCKED"


# --------------------------------------------------
# EXECUTION STATES
# --------------------------------------------------

EXECUTION_PENDING = "PENDING"
EXECUTION_AUTHORIZED = "AUTHORIZED"
EXECUTION_SUBMITTED = "SUBMITTED"
EXECUTION_PARTIAL = "PARTIAL"
EXECUTION_FILLED = "FILLED"
EXECUTION_CANCELLED = "CANCELLED"
EXECUTION_REJECTED = "REJECTED"
EXECUTION_FAILED = "FAILED"


# --------------------------------------------------
# AUTOMATION STATES
# --------------------------------------------------

AUTOMATION_DISABLED = "DISABLED"
AUTOMATION_READY = "READY"
AUTOMATION_RUNNING = "RUNNING"
AUTOMATION_PAUSED = "PAUSED"
AUTOMATION_HALTED = "HALTED"
AUTOMATION_ERROR = "ERROR"


# --------------------------------------------------
# COMMON BOOLEAN / CONTROL VALUES
# --------------------------------------------------

ENABLED = "ENABLED"
DISABLED = "DISABLED"

YES = "YES"
NO = "NO"


# --------------------------------------------------
# TIME / DEFAULT LIMITS
# --------------------------------------------------

DEFAULT_REQUEST_TIMEOUT_SECONDS = 30

DEFAULT_RETRY_COUNT = 3

DEFAULT_PAGE_SIZE = 50

MAX_PAGE_SIZE = 500


# --------------------------------------------------
# SECURITY
# --------------------------------------------------

MIN_PASSWORD_LENGTH = 8

MAX_PASSWORD_LENGTH = 128


# --------------------------------------------------
# API
# --------------------------------------------------

API_VERSION_V1 = "v1"

API_PREFIX_V1 = "/api/v1"


# --------------------------------------------------
# WEBSOCKET
# --------------------------------------------------

WEBSOCKET_MARKET_STREAM = "MARKET_STREAM"


# --------------------------------------------------
# SPECIAL CONTROL
# --------------------------------------------------

KILL_SWITCH_ENABLED = "ENABLED"

KILL_SWITCH_DISABLED = "DISABLED"


# --------------------------------------------------
# ENVIRONMENT NAMES
# --------------------------------------------------

ENV_DEV = "DEV"
ENV_TEST = "TEST"
ENV_STAGING = "STAGING"
ENV_PROD = "PROD"


SUPPORTED_ENVIRONMENTS = (
    ENV_DEV,
    ENV_TEST,
    ENV_STAGING,
    ENV_PROD,
)