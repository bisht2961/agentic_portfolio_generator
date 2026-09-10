import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_LOGGING_INITIALIZED = False

def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = "logs/app.log",
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
) -> None:
    """
    Initializes root and application logging handlers.
    Configures a console handler (stdout) and an optional rotating file handler.
    """
    global _LOGGING_INITIALIZED
    if _LOGGING_INITIALIZED:
        return

    level_str = (log_level or "INFO").upper()
    numeric_level = getattr(logging, level_str, logging.INFO)

    # Base formatter
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate lines
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Rotating File Handler
    if log_file:
        file_path = Path(log_file).resolve()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(file_path),
            maxBytes=10 * 1024 * 1024,  # 10 MB per log file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress overly chatty third-party loggers unless debugging
    if numeric_level > logging.DEBUG:
        for noisy_lib in ("httpcore", "httpcore2", "httpx", "httpx2"):
            logging.getLogger(noisy_lib).setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    _LOGGING_INITIALIZED = True
    root_logger.debug(f"Logging initialized at level {level_str}. File logging target: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance with the specified name."""
    return logging.getLogger(name)
