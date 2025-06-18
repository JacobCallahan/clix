"""Module handling internal and dependency logging."""
import logging
from pathlib import Path
import sys

from loguru import logger


def setup_loguru(level="INFO", path="logs/clix.log"):
    """Set up loguru logger."""
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        " - <level>{message}</level>"
    )

    # Console logger
    logger.add(
        sys.stderr,
        level=level.upper(),
        format=log_format,
        colorize=True,
    )

    # File logger
    # create the directory if it doesn't exist
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logger.add(
        path,
        level=level.upper(),
        format=log_format,
        rotation="10 MB",  # Corresponds to maxBytes=1e7, using 10 MB for simplicity
        retention="3 days",  # Corresponds to backupCount=3, assuming daily logs
        enqueue=True,  # For async logging
        colorize=False,  # No colors in file logs
    )

    # Map standard logging levels to loguru levels
    # This is a basic example; you might need a more comprehensive mapping
    logging_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    effective_level = logging_level_map.get(level.upper(), logging.INFO)

    # Intercept standard logging
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=effective_level, force=True)


setup_loguru()
