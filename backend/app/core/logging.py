"""Logging configuration foundation."""

import logging
import sys

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_level: str = "INFO", environment: str = "local") -> None:
    """Configure timestamped application logging."""

    handlers: list[logging.Handler] = []

    if environment == "production":
        try:
            from pythonjsonlogger.json import JsonFormatter

            handler = logging.StreamHandler(sys.stdout)
            formatter = JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
                datefmt=DEFAULT_DATE_FORMAT,
            )
            handler.setFormatter(formatter)
            handlers.append(handler)
        except ImportError:
            # Fallback if not installed
            handler = logging.StreamHandler(sys.stdout)
            handlers.append(handler)
    else:
        handlers.append(logging.StreamHandler(sys.stdout))

    logging.basicConfig(
        level=log_level.upper(),
        format=DEFAULT_LOG_FORMAT if environment != "production" else None,
        datefmt=DEFAULT_DATE_FORMAT if environment != "production" else None,
        handlers=handlers,
        force=True,
    )


def get_logger(name: str = "medvision_ai") -> logging.Logger:
    """Return a named application logger."""
    return logging.getLogger(name)
