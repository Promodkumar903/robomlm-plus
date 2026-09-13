"""
ROBOMLM PLUS
Market Constants
Module: app/core/constants/market_constants.py

Purpose:
    Centralized market, instrument, venue, session and
    market-data constants.

    This module contains constants only.
    Market intelligence and decision logic must not live here.
"""

from __future__ import annotations


# ==================================================
# MARKET TYPES
# ==================================================

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


# ==================================================
# INSTRUMENT TYPES
# ==================================================

INSTRUMENT_EQUITY = "EQUITY"
INSTRUMENT_INDEX = "INDEX"
INSTRUMENT_FUTURE = "FUTURE"
INSTRUMENT_OPTION = "OPTION"
INSTRUMENT_SPOT = "SPOT"
INSTRUMENT_PERPETUAL = "PERPETUAL"
INSTRUMENT_CFD = "CFD"


SUPPORTED_INSTRUMENT_TYPES = (
    INSTRUMENT_EQUITY,
    INSTRUMENT_INDEX,
    INSTRUMENT_FUTURE,
    INSTRUMENT_OPTION,
    INSTRUMENT_SPOT,
    INSTRUMENT_PERPETUAL,
    INSTRUMENT_CFD,
)


# ==================================================
# OPTION TYPES
# ==================================================

OPTION_CALL = "CALL"
OPTION_PUT = "PUT"

SUPPORTED_OPTION_TYPES = (
    OPTION_CALL,
    OPTION_PUT,
)


# ==================================================
# POSITION SIDES
# ==================================================

SIDE_BUY = "BUY"
SIDE_SELL = "SELL"

SUPPORTED_SIDES = (
    SIDE_BUY,
    SIDE_SELL,
)


# ==================================================
# POSITION STATES
# ==================================================

POSITION_FLAT = "FLAT"
POSITION_LONG = "LONG"
POSITION_SHORT = "SHORT"
POSITION_CLOSED = "CLOSED"


# ==================================================
# ORDER TYPES
# ==================================================

ORDER_MARKET = "MARKET"
ORDER_LIMIT = "LIMIT"
ORDER_STOP = "STOP"
ORDER_STOP_LIMIT = "STOP_LIMIT"


SUPPORTED_ORDER_TYPES = (
    ORDER_MARKET,
    ORDER_LIMIT,
    ORDER_STOP,
    ORDER_STOP_LIMIT,
)


# ==================================================
# ORDER STATES
# ==================================================

ORDER_PENDING = "PENDING"
ORDER_NEW = "NEW"
ORDER_OPEN = "OPEN"
ORDER_PARTIALLY_FILLED = "PARTIALLY_FILLED"
ORDER_FILLED = "FILLED"
ORDER_CANCELLED = "CANCELLED"
ORDER_REJECTED = "REJECTED"
ORDER_EXPIRED = "EXPIRED"
ORDER_FAILED = "FAILED"


SUPPORTED_ORDER_STATES = (
    ORDER_PENDING,
    ORDER_NEW,
    ORDER_OPEN,
    ORDER_PARTIALLY_FILLED,
    ORDER_FILLED,
    ORDER_CANCELLED,
    ORDER_REJECTED,
    ORDER_EXPIRED,
    ORDER_FAILED,
)


# ==================================================
# TIMEFRAMES
# ==================================================

TIMEFRAME_TICK = "TICK"

TIMEFRAME_1M = "1M"
TIMEFRAME_3M = "3M"
TIMEFRAME_5M = "5M"
TIMEFRAME_15M = "15M"
TIMEFRAME_30M = "30M"

TIMEFRAME_1H = "1H"
TIMEFRAME_2H = "2H"
TIMEFRAME_4H = "4H"

TIMEFRAME_1D = "1D"
TIMEFRAME_1W = "1W"
TIMEFRAME_1MO = "1MO"


SUPPORTED_TIMEFRAMES = (
    TIMEFRAME_TICK,
    TIMEFRAME_1M,
    TIMEFRAME_3M,
    TIMEFRAME_5M,
    TIMEFRAME_15M,
    TIMEFRAME_30M,
    TIMEFRAME_1H,
    TIMEFRAME_2H,
    TIMEFRAME_4H,
    TIMEFRAME_1D,
    TIMEFRAME_1W,
    TIMEFRAME_1MO,
)


# ==================================================
# MARKET DATA TYPES
# ==================================================

DATA_TICK = "TICK"
DATA_QUOTE = "QUOTE"
DATA_OHLC = "OHLC"
DATA_ORDERBOOK = "ORDERBOOK"
DATA_TRADE = "TRADE"
DATA_VOLUME = "VOLUME"
DATA_OPEN_INTEREST = "OPEN_INTEREST"
DATA_FUNDING = "FUNDING"
DATA_MARKET_DEPTH = "MARKET_DEPTH"


SUPPORTED_DATA_TYPES = (
    DATA_TICK,
    DATA_QUOTE,
    DATA_OHLC,
    DATA_ORDERBOOK,
    DATA_TRADE,
    DATA_VOLUME,
    DATA_OPEN_INTEREST,
    DATA_FUNDING,
    DATA_MARKET_DEPTH,
)


# ==================================================
# MARKET DATA QUALITY
# ==================================================

DATA_QUALITY_UNKNOWN = "UNKNOWN"
DATA_QUALITY_GOOD = "GOOD"
DATA_QUALITY_DEGRADED = "DEGRADED"
DATA_QUALITY_STALE = "STALE"
DATA_QUALITY_INVALID = "INVALID"
DATA_QUALITY_UNAVAILABLE = "UNAVAILABLE"


# ==================================================
# MARKET STATE
# ==================================================

MARKET_STATE_PRE_OPEN = "PRE_OPEN"
MARKET_STATE_OPEN = "OPEN"
MARKET_STATE_CLOSED = "CLOSED"
MARKET_STATE_HALT = "HALT"
MARKET_STATE_AUCTION = "AUCTION"
MARKET_STATE_UNKNOWN = "UNKNOWN"


# ==================================================
# VENUES
# ==================================================

VENUE_DHAN = "DHAN"
VENUE_KOTAK = "KOTAK"
VENUE_BINANCE = "BINANCE"
VENUE_BYBIT = "BYBIT"


SUPPORTED_VENUES = (
    VENUE_DHAN,
    VENUE_KOTAK,
    VENUE_BINANCE,
    VENUE_BYBIT,
)


# ==================================================
# REGIONS
# ==================================================

REGION_INDIA = "INDIA"
REGION_US = "US"
REGION_EUROPE = "EUROPE"
REGION_GLOBAL = "GLOBAL"


# ==================================================
# CURRENCY CODES
# ==================================================

CURRENCY_INR = "INR"
CURRENCY_USD = "USD"
CURRENCY_EUR = "EUR"
CURRENCY_GBP = "GBP"
CURRENCY_JPY = "JPY"


# ==================================================
# MARKET SESSIONS
# ==================================================

SESSION_PRE_MARKET = "PRE_MARKET"
SESSION_REGULAR = "REGULAR"
SESSION_POST_MARKET = "POST_MARKET"
SESSION_24X7 = "24X7"


# ==================================================
# DERIVATIVE STATES
# ==================================================

DERIVATIVE_ACTIVE = "ACTIVE"
DERIVATIVE_EXPIRED = "EXPIRED"
DERIVATIVE_SUSPENDED = "SUSPENDED"


# ==================================================
# EXPIRY TYPES
# ==================================================

EXPIRY_NONE = "NONE"
EXPIRY_DAILY = "DAILY"
EXPIRY_WEEKLY = "WEEKLY"
EXPIRY_MONTHLY = "MONTHLY"
EXPIRY_QUARTERLY = "QUARTERLY"


# ==================================================
# PRICE / QUANTITY VALIDATION
# ==================================================

MIN_PRICE = 0.0
MIN_QUANTITY = 0.0


# ==================================================
# MARKET DATA LIMITS
# ==================================================

DEFAULT_MARKET_DATA_TIMEOUT_SECONDS = 10

DEFAULT_MARKET_DATA_RETRY_COUNT = 3

DEFAULT_MARKET_DATA_MAX_STALE_SECONDS = 120


# ==================================================
# ORDERBOOK
# ==================================================

ORDERBOOK_DEFAULT_DEPTH = 10

ORDERBOOK_MAX_DEPTH = 500


# ==================================================
# IDENTIFICATION
# ==================================================

IDENTITY_FIELD_MARKET = "market"
IDENTITY_FIELD_VENUE = "venue"
IDENTITY_FIELD_INSTRUMENT = "instrument"
IDENTITY_FIELD_SYMBOL = "symbol"
IDENTITY_FIELD_CONTRACT = "contract"
IDENTITY_FIELD_EXPIRY = "expiry"


# ==================================================
# MARKET SNAPSHOT STATUS
# ==================================================

SNAPSHOT_VALID = "VALID"
SNAPSHOT_STALE = "STALE"
SNAPSHOT_INVALID = "INVALID"
SNAPSHOT_INCOMPLETE = "INCOMPLETE"
SNAPSHOT_UNAVAILABLE = "UNAVAILABLE"


# ==================================================
# UTILITY GROUPS
# ==================================================

SPOT_MARKETS = (
    MARKET_STOCK,
    MARKET_INDEX,
    MARKET_FX,
    MARKET_CRYPTO,
    MARKET_COMMODITY,
)


DERIVATIVE_INSTRUMENTS = (
    INSTRUMENT_FUTURE,
    INSTRUMENT_OPTION,
    INSTRUMENT_PERPETUAL,
    INSTRUMENT_CFD,
)


OPTION_INSTRUMENTS = (
    INSTRUMENT_OPTION,
)


# ==================================================
# CONSTANT VALIDATION HELPERS
# ==================================================

def is_supported_market(value: str) -> bool:
    """Return True when the market type is supported."""
    return value.upper() in SUPPORTED_MARKETS


def is_supported_venue(value: str) -> bool:
    """Return True when the venue is supported."""
    return value.upper() in SUPPORTED_VENUES


def is_supported_instrument_type(value: str) -> bool:
    """Return True when the instrument type is supported."""
    return value.upper() in SUPPORTED_INSTRUMENT_TYPES


def is_supported_timeframe(value: str) -> bool:
    """Return True when the timeframe is supported."""
    return value.upper() in SUPPORTED_TIMEFRAMES