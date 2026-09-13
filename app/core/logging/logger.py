"""
ROBOMLM PLUS
Central Logger
Module: app/core/logging/logger.py

Purpose:
    Central logging facade for ROBOMLM PLUS.

    Provides one common interface for application diagnostics,
    warnings, errors and critical events while keeping dedicated
    audit and blackbox logging separate.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from .application_logger import ApplicationLogger
from .audit_logger import AuditLogger
from .blackbox_logger import BlackboxLogger


LOGGER_NAME = "ROBOMLM"


def get_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """
    Return the central Python logger.

    Named loggers become children of the ROBOMLM root logger.
    """
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")

    return logging.getLogger(LOGGER_NAME)


class Logger:
    """
    Central ROBOMLM logging facade.

    Responsibilities are intentionally separated:

        Logger             -> general application diagnostics
        ApplicationLogger  -> application-level events
        AuditLogger       -> accountability/security audit events
        BlackboxLogger     -> reconstruction/event trace

    This class does not implement logging configuration.
    Handler and formatter configuration belongs to startup/system
    initialization.
    """

    def __init__(
        self,
        name: Optional[str] = None,
    ) -> None:
        self._logger = get_logger(name)

        logger_name = name or LOGGER_NAME

        self._application = ApplicationLogger(
            name=f"{logger_name}.application"
        )

        self._audit = AuditLogger(
            name=f"{logger_name}.audit"
        )

        self._blackbox = BlackboxLogger(
            name=f"{logger_name}.blackbox"
        )

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying Python logger."""
        return self._logger

    @property
    def application(self) -> ApplicationLogger:
        """Return the application logger."""
        return self._application

    @property
    def audit(self) -> AuditLogger:
        """Return the audit logger."""
        return self._audit

    @property
    def blackbox(self) -> BlackboxLogger:
        """Return the blackbox logger."""
        return self._blackbox

    def debug(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a debug message."""
        self._logger.debug(message, *args, **kwargs)

    def info(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an informational message."""
        self._logger.info(message, *args, **kwargs)

    def warning(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a warning message."""
        self._logger.warning(message, *args, **kwargs)

    def error(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an error message."""
        self._logger.error(message, *args, **kwargs)

    def critical(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a critical message."""
        self._logger.critical(message, *args, **kwargs)

    def exception(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an exception with traceback information."""
        self._logger.exception(message, *args, **kwargs)

    def log(
        self,
        level: int,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log using an explicit logging level."""
        self._logger.log(level, message, *args, **kwargs)


# ============================================================
# GLOBAL LOGGER
# ============================================================

logger = Logger()


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def debug(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log a debug message through the central logger."""
    logger.debug(message, *args, **kwargs)


def info(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log an informational message through the central logger."""
    logger.info(message, *args, **kwargs)


def warning(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log a warning message through the central logger."""
    logger.warning(message, *args, **kwargs)


def error(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log an error message through the central logger."""
    logger.error(message, *args, **kwargs)


def critical(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log a critical message through the central logger."""
    logger.critical(message, *args, **kwargs)


def exception(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Log an exception through the central logger."""
    logger.exception(message, *args, **kwargs)


def get_module_logger(
    name: str,
) -> Logger:
    """
    Return a Logger facade for a specific application module.
    """
    return Logger(name=name)