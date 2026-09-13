"""
ROBOMLM PLUS
Application Logger
Module: app/core/logging/application_logger.py

Purpose:
    Application-level logging interface for ROBOMLM PLUS.

    This module provides a consistent logging facade for application
    events. It does not implement audit or blackbox recording.
"""

from __future__ import annotations

import logging
from typing import Any, Optional


LOGGER_NAME = "ROBOMLM.application"


def get_application_logger(
    name: Optional[str] = None,
) -> logging.Logger:
    """
    Return the application logger.

    When a name is supplied, it becomes a child logger of the
    ROBOMLM application logger.
    """
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")

    return logging.getLogger(LOGGER_NAME)


class ApplicationLogger:
    """
    Structured application logging facade.

    The logger deliberately keeps business decisions, audit records,
    blackbox records and application diagnostics as separate concerns.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._logger = logger or get_application_logger(name)

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying Python logger."""
        return self._logger

    def debug(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a debug-level application event."""
        self._logger.debug(message, *args, **kwargs)

    def info(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an informational application event."""
        self._logger.info(message, *args, **kwargs)

    def warning(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a warning-level application event."""
        self._logger.warning(message, *args, **kwargs)

    def error(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log an error-level application event."""
        self._logger.error(message, *args, **kwargs)

    def critical(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log a critical application event."""
        self._logger.critical(message, *args, **kwargs)

    def exception(
        self,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Log an exception with traceback information.

        Intended to be called from an active exception handler.
        """
        self._logger.exception(message, *args, **kwargs)

    def log(
        self,
        level: int,
        message: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Log using an explicit Python logging level."""
        self._logger.log(level, message, *args, **kwargs)


application_logger = ApplicationLogger()


def get_logger(name: Optional[str] = None) -> ApplicationLogger:
    """
    Return an ApplicationLogger instance.

    A named logger is useful for individual modules or services.
    """
    return ApplicationLogger(name=name)