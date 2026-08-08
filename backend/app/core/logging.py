"""Logging configuration foundation."""

import logging
import sys

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_level: str = "INFO") -> None:
    """Configure timestamped application logging."""
    logging.basicConfig(
        level=log_level.upper(),
        format=DEFAULT_LOG_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )


def get_logger(name: str = "medvision_ai") -> logging.Logger:
    """Return a named application logger."""
    return logging.getLogger(name)
