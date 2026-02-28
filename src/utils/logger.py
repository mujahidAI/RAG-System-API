"""Structured logging configuration for the RAG system.

This module provides a centralized logging setup using Python's logging module
with structured output support. All modules in the RAG system use this logger
for consistent log formatting and observability.
"""

import logging
import sys
from datetime import datetime
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs logs in a structured format.

    Outputs JSON-like format with timestamp, level, module, and message.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return str(log_data)


def setup_logger(name: str, level: str = "INFO", format_type: str = "json") -> logging.Logger:
    """Create and configure a logger instance.

    Args:
        name: Logger name, typically __name__ of the module
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type - "json" for structured or "text" for plain

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        if format_type == "json":
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with default configuration.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    from src.utils.config import get_settings

    settings = get_settings()
    return setup_logger(name, settings.log.level, settings.log.format)


def log_function_call(logger: logging.Logger):
    """Decorator to log function calls with arguments and return values.

    Args:
        logger: Logger instance to use

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned: {type(result)}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
                raise

        return wrapper

    return decorator
