"""
Centralized logging configuration for AllTalk TTS.

This module provides a consistent logging setup using Loguru,
replacing the standard library logging module.
"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "INFO", log_file: str = "alltalk.log"):
    """
    Configure Loguru logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file for persistent logging
    """
    # Remove default handler
    logger.remove()

    # Add console handler with colorized output
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler for persistent logging
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    # Suppress noisy third-party loggers
    logger.disable("httpx")
    logger.disable("httpcore")
    logger.disable("urllib3")
    logger.disable("uvicorn")


def get_logger(name: str = "alltalk"):
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Loguru logger instance
    """
    return logger.bind(name=name)


# Initialize logging on import
setup_logging()
