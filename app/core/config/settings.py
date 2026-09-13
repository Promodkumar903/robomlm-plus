"""
ROBOMLM PLUS
Settings Configuration
Module: app/core/config/settings.py
"""

from dataclasses import dataclass
from pathlib import Path
import os


# --------------------------------------------------
# PROJECT ROOT
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = PROJECT_ROOT / "robomlm_data"

LOGS_DIR = DATA_DIR / "logs"
BLACKBOX_DIR = DATA_DIR / "blackbox"
EXPORTS_DIR = DATA_DIR / "exports"
BACKUPS_DIR = DATA_DIR / "backups"
CACHE_DIR = DATA_DIR / "cache"


# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------

@dataclass(frozen=True)
class AppConfig:
    app_name: str
    app_version: str
    environment: str
    debug: bool
    timezone: str


# --------------------------------------------------
# DATABASE CONFIG
# --------------------------------------------------

@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str


# --------------------------------------------------
# AUTH CONFIG
# --------------------------------------------------

@dataclass(frozen=True)
class AuthConfig:
    jwt_secret: str
    token_expiry_hours: int


# --------------------------------------------------
# MARKET CONFIG
# --------------------------------------------------

@dataclass(frozen=True)
class MarketConfig:
    refresh_interval: int
    max_stale_seconds: int


# --------------------------------------------------
# SYSTEM CONFIG
# --------------------------------------------------

@dataclass(frozen=True)
class SystemConfig:
    app: AppConfig
    database: DatabaseConfig
    auth: AuthConfig
    market: MarketConfig


# --------------------------------------------------
# DEFAULT CONFIG
# --------------------------------------------------

CONFIG = SystemConfig(
    app=AppConfig(
        app_name=os.getenv("APP_NAME", "ROBOMLM_PLUS"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("APP_ENV", "DEV"),
        debug=os.getenv("DEBUG", "True").lower() == "true",
        timezone=os.getenv("TIMEZONE", "Asia/Kolkata"),
    ),
    database=DatabaseConfig(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        name=os.getenv("DB_NAME", "robomlm"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", ""),
    ),
    auth=AuthConfig(
        jwt_secret=os.getenv("JWT_SECRET", "CHANGE_ME"),
        token_expiry_hours=int(os.getenv("TOKEN_EXPIRY_HOURS", "24")),
    ),
    market=MarketConfig(
        refresh_interval=int(os.getenv("REFRESH_INTERVAL", "5")),
        max_stale_seconds=int(os.getenv("MAX_STALE_SECONDS", "120")),
    ),
)