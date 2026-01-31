"""
Logging configuration for the mouse clock system.

This module sets up file-based logging to make debugging easier without
needing to check the Talon log. Each new instance creates a separate
timestamped log file.
"""

import logging
from datetime import datetime
from pathlib import Path

# Get the mouse-clock directory (two levels up from this file)
MOUSE_CLOCK_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = MOUSE_CLOCK_DIR / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Create logger
logger = logging.getLogger("mouse_clock")
logger.setLevel(logging.DEBUG)

# Prevent propagation to avoid duplicate logs
logger.propagate = False

# Global variable to track current log file
_current_log_file = None


def _create_new_log_file():
    """Create a new timestamped log file and return its path."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return LOGS_DIR / f"mouse_clock_{timestamp}.log"


def initialize_logger():
    """
    Initialize or reinitialize the logger with a new timestamped file.
    Call this when creating a new mouse clock instance.
    """
    global _current_log_file

    # Remove any existing handlers
    logger.handlers.clear()

    # Create new log file with timestamp
    _current_log_file = _create_new_log_file()

    # Create file handler
    file_handler = logging.FileHandler(_current_log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(file_handler)

    # Log initialization
    logger.info("=" * 60)
    logger.info(f"Mouse Clock Log Session Started")
    logger.info(f"Log file: {_current_log_file.name}")
    logger.info("=" * 60)

    return _current_log_file


def get_current_log_file():
    """Get the path to the current log file."""
    return _current_log_file


# Initialize on module import
initialize_logger()


def log_separator():
    """Log a separator line for readability."""
    logger.info("=" * 60)


def log_debug(msg: str):
    """Log a debug message."""
    logger.debug(msg)


def log_info(msg: str):
    """Log an info message."""
    logger.info(msg)


def log_warning(msg: str):
    """Log a warning message."""
    logger.warning(msg)


def log_error(msg: str):
    """Log an error message."""
    logger.error(msg)
