"""Logging setup: rotating file handler (INFO) - console stays clean for the user."""
import logging
from logging.handlers import RotatingFileHandler

from .config import LOG_DIR, LOG_FILE

_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    root = logging.getLogger("expense_tracker")
    if not _configured:
        root.setLevel(logging.INFO)
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(LOG_FILE, maxBytes=500_000, backupCount=2)
            handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
            root.addHandler(handler)
        except OSError:  # read-only file system etc. - never crash because of logging
            root.addHandler(logging.NullHandler())
        root.propagate = False
        _configured = True
    return logging.getLogger(f"expense_tracker.{name}")
