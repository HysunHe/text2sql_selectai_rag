""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
"""

import logging
import logging.handlers
import os
import sys
import functools
import threading
import contextlib
import rich.console as rich_console
from logging import Logger
from datetime import datetime
from conf import app_config

_console = rich_console.Console()
_STATUS = None

logging.basicConfig(encoding="utf8")

_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger()
_logger.setLevel(app_config.DEBUG_LEVEL)

# _console_handler = logging.StreamHandler(sys.stdout)
# _console_handler.setFormatter(_formatter)
# _logger.addHandler(_console_handler)

_file_handler = logging.handlers.RotatingFileHandler(
    filename=app_config.LOG_FILE_PATH,
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    mode="a",
    encoding="utf8",
)
_file_handler.setFormatter(_formatter)
_logger.addHandler(_file_handler)


class _NoOpConsoleStatus:
    """An empty class for multi-threaded console.status."""

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def update(self, text):
        """docstring"""

    def stop(self):
        """docstring"""

    def start(self):
        """docstring"""


def safe_rich_status(msg: str):
    """A wrapper for multi-threaded console.status."""
    if threading.current_thread() is threading.main_thread():
        global _STATUS  # pylint: disable=global-statement
        if _STATUS is None:
            _STATUS = _console.status(msg)
        _STATUS.update(msg)
        return _STATUS
    return _NoOpConsoleStatus()


@contextlib.contextmanager
def print_exception_no_traceback():
    """A context manager that prints out an exception without traceback.

    Mainly for UX: user-facing errors, e.g., ValueError, should suppress long
    tracebacks.

    If SHOW_DEBUG environment variable is set, this context manager is a
    no-op and the full traceback will be shown.

    Example usage:

        with print_exception_no_traceback():
            if error():
                raise ValueError('...')
    """
    if os.getenv("SHOW_DEBUG", "False").lower() in ("true", "1"):
        # When SHOW_DEBUG is set, show the full traceback
        yield
    else:
        original_tracelimit = getattr(sys, "tracebacklimit", 1000)
        sys.tracebacklimit = 0
        yield
        sys.tracebacklimit = original_tracelimit


def debug_enabled(logger: Logger):
    """docstring"""

    def decorate(func_name):

        @functools.wraps(func_name)
        def wrapper(*args, **kwargs):
            dt_str = datetime.now().strftime("%Y%m%d%H%M%S.%f")
            logger.debug(f"* {dt_str} - Enter {func_name}, {args}, {kwargs}")
            try:
                return func_name(*args, **kwargs)
            finally:
                logger.debug(f"* {dt_str} - Exit {func_name}")

        return wrapper

    return decorate
