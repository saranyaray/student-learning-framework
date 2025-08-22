"""
Utility functions for the Student Learning Framework
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Try to import settings, fallback to simple config if it fails
try:
    from config.settings import settings

    LOG_LEVEL = settings.LOG_LEVEL
    LOG_FORMAT = settings.LOG_FORMAT
except ImportError:
    # Fallback configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging(
    name: str, level: Optional[str] = None, log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting and optional file output

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Common loggers
ingestion_logger = get_logger("ingestion")
retrieval_logger = get_logger("retrieval")
orchestration_logger = get_logger("orchestration")
api_logger = get_logger("api")
