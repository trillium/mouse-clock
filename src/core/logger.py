"""
Logging configuration for the mouse clock system.

Logs to both file and Talon console (via print).
Use LOG_LEVEL to control verbosity.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Get the mouse-clock directory (two levels up from this file)
MOUSE_CLOCK_DIR = Path(__file__).parent.parent.parent
LOGS_DIR = MOUSE_CLOCK_DIR / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# Log levels - set this to control verbosity
# DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40
LOG_LEVEL = logging.DEBUG
CONSOLE_LOG_LEVEL = logging.INFO  # What shows in Talon console

# Create logger
logger = logging.getLogger("mouse_clock")
logger.setLevel(LOG_LEVEL)
logger.propagate = False

# Global state
_current_log_file: Optional[Path] = None
_console_handler: Optional[logging.Handler] = None


class TalonConsoleHandler(logging.Handler):
    """Handler that outputs to Talon's console via print()."""

    def emit(self, record):
        try:
            msg = self.format(record)
            # Prefix with [MC] for easy grep in Talon logs
            print(f"[MC] {msg}")
        except Exception:
            self.handleError(record)


def _create_new_log_file() -> Path:
    """Create a new timestamped log file and return its path."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return LOGS_DIR / f"mouse_clock_{timestamp}.log"


def initialize_logger() -> Path:
    """
    Initialize or reinitialize the logger with a new timestamped file.
    Call this when creating a new mouse clock instance.
    """
    global _current_log_file, _console_handler

    # Close and remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    # Create new log file with timestamp
    _current_log_file = _create_new_log_file()

    # File handler - detailed format with timestamps
    file_handler = logging.FileHandler(_current_log_file, mode='w', encoding='utf-8')
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d | %(levelname)-5s | %(message)s',
        datefmt='%H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler - compact format for Talon log
    _console_handler = TalonConsoleHandler()
    _console_handler.setLevel(CONSOLE_LOG_LEVEL)
    console_formatter = logging.Formatter('%(levelname)-5s | %(message)s')
    _console_handler.setFormatter(console_formatter)
    logger.addHandler(_console_handler)

    # Log initialization
    logger.info("=" * 50)
    logger.info(f"Session started - {_current_log_file.name}")
    logger.info("=" * 50)

    return _current_log_file


def get_current_log_file() -> Optional[Path]:
    """Get the path to the current log file."""
    return _current_log_file


def set_console_level(level: int):
    """Change console log level at runtime. Use logging.DEBUG, INFO, WARNING, ERROR."""
    global _console_handler
    if _console_handler:
        _console_handler.setLevel(level)
        logger.info(f"Console log level set to {logging.getLevelName(level)}")


# Initialize on module import
initialize_logger()


# =============================================================================
# Convenience functions with context
# =============================================================================

def log_debug(msg: str):
    """Log a debug message (file only by default)."""
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


def log_mode_change(old_mode: str, new_mode: str):
    """Log a mode transition."""
    logger.info(f"MODE: {old_mode} -> {new_mode}")


def log_action(action: str, **kwargs):
    """Log an action with optional parameters."""
    if kwargs:
        params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.info(f"ACTION: {action}({params})")
    else:
        logger.info(f"ACTION: {action}")


def log_state(component: str, **kwargs):
    """Log component state for debugging."""
    state = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f"STATE [{component}]: {state}")


def log_position(label: str, x: float, y: float):
    """Log a position with context label."""
    logger.debug(f"POS [{label}]: ({x:.0f}, {y:.0f})")


def log_tags(tags: list):
    """Log tag changes."""
    tag_str = ", ".join(t.replace("user.", "") for t in tags)
    logger.info(f"TAGS: [{tag_str}]")


def log_separator(label: str = ""):
    """Log a separator line for readability."""
    if label:
        logger.info(f"--- {label} ---")
    else:
        logger.info("-" * 40)
