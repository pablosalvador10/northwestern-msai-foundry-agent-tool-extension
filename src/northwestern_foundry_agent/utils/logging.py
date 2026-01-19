"""Structured logging utilities for Northwestern Foundry Agent.

This module provides centralized logging configuration with support
for both JSON and text output formats, suitable for development and production.
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import MutableMapping
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from northwestern_foundry_agent.config.settings import Settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging.

    Outputs log records as JSON objects for easy parsing by log aggregation
    systems like Azure Monitor, Datadog, or ELK stack.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: The log record to format.

        Returns:
            JSON-formatted log string.
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development.

    Outputs log records in a readable format suitable for console output
    during development and debugging.
    """

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        """Initialize the text formatter."""
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)


def setup_logging(settings: Settings | None = None) -> None:
    """Configure application-wide logging.

    Sets up logging based on the provided settings or defaults.
    Should be called once at application startup.

    Args:
        settings: Optional Settings instance. If None, uses defaults.

    Example:
        >>> from northwestern_foundry_agent.config import Settings
        >>> settings = Settings(log_level="DEBUG", log_format="text")
        >>> setup_logging(settings)
    """
    # Import here to avoid circular imports
    if settings is None:
        from northwestern_foundry_agent.config.settings import get_settings

        settings = get_settings()

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level))

    # Select formatter based on settings
    if settings.log_format == "json":
        formatter: logging.Formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["httpx", "httpcore", "azure", "urllib3"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Creates or retrieves a logger for the given module/component name.
    The logger inherits settings from the root logger configured by setup_logging.

    Args:
        name: Name for the logger, typically __name__ of the calling module.

    Returns:
        Configured Logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", extra={"request_id": "abc123"})
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    """Logger adapter for adding contextual information to log records.

    Allows attaching extra context (like request IDs, user IDs) to all
    log messages without repeating the context in each call.

    Example:
        >>> base_logger = get_logger(__name__)
        >>> logger = LoggerAdapter(base_logger, {"request_id": "abc123"})
        >>> logger.info("Processing request")  # Includes request_id in output
    """

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Process the logging message and kwargs.

        Args:
            msg: The log message.
            kwargs: Additional keyword arguments.

        Returns:
            Tuple of processed message and kwargs.
        """
        extra = dict(kwargs.get("extra", {}))
        if self.extra:
            extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
